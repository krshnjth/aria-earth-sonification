import os
import csv
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.utils.http_client import HttpClient
from app.database.repositories import DatasetRepository, ObservationRepository

DATASET_META = {
    "id": "atmosphere_methane_global",
    "title": "Globally Averaged Marine Surface Atmospheric Methane (CH₄)",
    "organization": "NOAA Global Monitoring Laboratory (GML) Carbon Cycle Group",
    "source_url": settings.NOAA_CH4_URL,
    "version": "NOAA Global Marine Boundary Layer In-Situ Surface Network",
    "measurement_name": "Atmospheric Methane Mole Fraction",
    "unit": "ppb",
    "baseline": "722 ppb (Pre-Industrial Historical Baseline)",
    "temporal_resolution": "monthly",
    "geographic_coverage": "global marine boundary layer",
    "is_active": True
}

class Ch4Service:
    @staticmethod
    def get_cache_file() -> str:
        return os.path.join(settings.DATA_CACHE_DIR, "ch4_mm_gl.csv")

    @classmethod
    async def fetch_and_cache(cls) -> str:
        cache_path = cls.get_cache_file()
        try:
            logger.info(f"Downloading official NOAA Methane (CH4) dataset from {settings.NOAA_CH4_URL}")
            resp = await HttpClient.fetch_with_retry(settings.NOAA_CH4_URL)
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            logger.info(f"Saved NOAA CH4 cache to {cache_path} ({len(resp.text)} bytes)")
            return cache_path
        except Exception as e:
            logger.warning(f"Failed to download NOAA CH4 from remote ({e}). Checking local cache...")
            if os.path.exists(cache_path):
                logger.info(f"Using existing local cache at {cache_path}")
                return cache_path
            raise RuntimeError(f"NOAA CH4 dataset unavailable: {e}")

    @classmethod
    def parse_csv(cls, file_path: str) -> List[Dict[str, Any]]:
        observations = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        data_lines = [l for l in lines if not l.startswith("#") and l.strip()]
        if not data_lines:
            raise ValueError("No valid data rows found in NOAA CH4 CSV.")

        reader = csv.reader(data_lines)
        # Check header
        header = next(reader, None)

        for row in reader:
            if not row or len(row) < 4:
                continue
            try:
                year = int(row[0].strip())
                month = int(row[1].strip())
                val_token = row[3].strip()  # average
                val = float(val_token)

                # NOAA uses -999.99 or -9.99 for missing values
                if val < 500.0 or val > 3000.0:
                    continue

                unc = None
                if len(row) > 4:
                    try:
                        unc_val = float(row[4].strip())
                        if unc_val >= 0:
                            unc = unc_val
                    except ValueError:
                        pass

                date_str = f"{year}-{month:02d}"
                observations.append({
                    "date": date_str,
                    "year": year,
                    "month": month,
                    "value": round(val, 1),
                    "raw_value": val_token,
                    "uncertainty": unc,
                    "latitude": None,
                    "longitude": None,
                    "quality_flag": "OFFICIAL_NOAA_GML"
                })
            except (ValueError, IndexError):
                continue

        observations.sort(key=lambda x: x["date"])
        return observations

    @classmethod
    async def sync_database(cls, db: Session, force_refresh: bool = False):
        ds_repo = DatasetRepository(db)
        obs_repo = ObservationRepository(db)

        dataset = ds_repo.get(DATASET_META["id"])
        cache_path = cls.get_cache_file()
        existing_count = obs_repo.count(DATASET_META["id"])

        if not force_refresh and dataset and existing_count > 0:
            logger.debug(f"NOAA CH4 dataset already populated ({existing_count} records).")
            return

        if force_refresh or not os.path.exists(cache_path):
            await cls.fetch_and_cache()

        observations = cls.parse_csv(cache_path)
        logger.info(f"Parsed {len(observations)} monthly NOAA CH4 observations (1983–present).")

        ds_repo.upsert(DATASET_META)
        obs_repo.bulk_replace(DATASET_META["id"], observations)
        logger.info(f"Database successfully synchronized with {len(observations)} NOAA CH4 records.")
