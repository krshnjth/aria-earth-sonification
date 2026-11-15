import os
import csv
import math
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.utils.http_client import HttpClient
from app.database.repositories import DatasetRepository, ObservationRepository

DATASET_META = {
    "id": "global_sea_level",
    "title": "Global Mean Sea Level Change (Multi-Mission Satellite Altimetry)",
    "organization": "NASA / NOAA / CNES / EUMETSAT Standardized Reference Missions",
    "source_url": settings.NOAA_GMSL_URL,
    "version": "Satellite Altimeter GDR Free All (66°S to 66°N)",
    "measurement_name": "Global Mean Sea Level Anomaly",
    "unit": "mm",
    "baseline": "1993-2008 Altimeter Mean",
    "temporal_resolution": "10-day cycle / monthly interpolated",
    "geographic_coverage": "global ocean (66°S to 66°N)",
    "is_active": True
}

class SeaLevelService:
    @staticmethod
    def get_cache_file() -> str:
        return os.path.join(settings.DATA_CACHE_DIR, "gmsl_altimetry.csv")

    @classmethod
    async def fetch_and_cache(cls) -> str:
        cache_path = cls.get_cache_file()
        try:
            logger.info(f"Downloading official NOAA/NASA GMSL Altimetry dataset from {settings.NOAA_GMSL_URL}")
            resp = await HttpClient.fetch_with_retry(settings.NOAA_GMSL_URL)
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            logger.info(f"Saved GMSL cache to {cache_path} ({len(resp.text)} bytes)")
            return cache_path
        except Exception as e:
            logger.warning(f"Failed to download GMSL from remote ({e}). Checking local cache...")
            if os.path.exists(cache_path):
                logger.info(f"Using existing local cache at {cache_path}")
                return cache_path
            raise RuntimeError(f"GMSL dataset unavailable: {e}")

    @classmethod
    def parse_csv(cls, file_path: str) -> List[Dict[str, Any]]:
        observations = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        data_lines = [l for l in lines if not l.startswith("#") and l.strip()]
        if not data_lines:
            raise ValueError("No data lines in GMSL CSV.")

        reader = csv.reader(data_lines)
        header = next(reader)  # year,TOPEX/Poseidon,Jason-1,Jason-2,Jason-3,Sentinel-6MF

        # Group observations by year-month to provide a standardized monthly time series
        monthly_buckets: Dict[str, List[float]] = {}
        raw_tokens: Dict[str, str] = {}

        for row in reader:
            if not row or len(row) < 2:
                continue
            try:
                dec_year = float(row[0].strip())
                year = int(math.floor(dec_year))
                frac = dec_year - year
                month = max(1, min(12, int(math.floor(frac * 12)) + 1))
                date_key = f"{year}-{month:02d}"

                # Look for valid value across satellite mission columns (most recent mission has priority)
                val = None
                token = ""
                for col_idx in range(len(row) - 1, 0, -1):
                    item = row[col_idx].strip()
                    if item:
                        try:
                            val = float(item)
                            token = item
                            break
                        except ValueError:
                            continue

                if val is not None and -200.0 <= val <= 500.0:
                    if date_key not in monthly_buckets:
                        monthly_buckets[date_key] = []
                    monthly_buckets[date_key].append(val)
                    raw_tokens[date_key] = token
            except (ValueError, IndexError):
                continue

        for date_str, vals in sorted(monthly_buckets.items()):
            year, month = map(int, date_str.split("-"))
            avg_val = round(sum(vals) / len(vals), 2)
            observations.append({
                "date": date_str,
                "year": year,
                "month": month,
                "value": avg_val,
                "raw_value": raw_tokens.get(date_str, str(avg_val)),
                "uncertainty": 1.5,  # Standard satellite altimeter error estimate ~1.5mm
                "latitude": None,
                "longitude": None,
                "quality_flag": "OFFICIAL_SATELLITE_ALTIMETRY"
            })

        return observations

    @classmethod
    async def sync_database(cls, db: Session, force_refresh: bool = False):
        ds_repo = DatasetRepository(db)
        obs_repo = ObservationRepository(db)

        dataset = ds_repo.get(DATASET_META["id"])
        cache_path = cls.get_cache_file()
        existing_count = obs_repo.count(DATASET_META["id"])

        if not force_refresh and dataset and existing_count > 0:
            logger.debug(f"GMSL dataset already populated ({existing_count} records).")
            return

        if force_refresh or not os.path.exists(cache_path):
            await cls.fetch_and_cache()

        observations = cls.parse_csv(cache_path)
        logger.info(f"Parsed {len(observations)} monthly GMSL altimetry observations (1993–present).")

        ds_repo.upsert(DATASET_META)
        obs_repo.bulk_replace(DATASET_META["id"], observations)
        logger.info(f"Database successfully synchronized with {len(observations)} GMSL records.")
