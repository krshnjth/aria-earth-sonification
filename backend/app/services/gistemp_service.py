import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.utils.http_client import HttpClient
from app.database.repositories import DatasetRepository, ObservationRepository

DATASET_META = {
    "id": "global_temperature",
    "title": "Global Surface Temperature Anomaly (GISTEMP v4 LOTI)",
    "organization": "NASA Goddard Institute for Space Studies (GISS)",
    "source_url": settings.GISTEMP_URL,
    "version": "v4",
    "measurement_name": "Surface Temperature Anomaly",
    "unit": "°C",
    "baseline": "1951-1980 Mean",
    "temporal_resolution": "monthly",
    "geographic_coverage": "global",
    "is_active": True
}

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

class GistempService:
    @staticmethod
    def get_cache_file() -> str:
        return os.path.join(settings.DATA_CACHE_DIR, "gistemp_loti.csv")

    @classmethod
    async def fetch_and_cache(cls) -> str:
        cache_path = cls.get_cache_file()
        try:
            logger.info(f"Downloading official NASA GISTEMP LOTI dataset from {settings.GISTEMP_URL}")
            resp = await HttpClient.fetch_with_retry(settings.GISTEMP_URL)
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            logger.info(f"Saved GISTEMP cache to {cache_path} ({len(resp.text)} bytes)")
            return cache_path
        except Exception as e:
            logger.warning(f"Failed to download GISTEMP from remote ({e}). Checking local cache...")
            if os.path.exists(cache_path):
                logger.info(f"Using existing local cache at {cache_path}")
                return cache_path
            raise RuntimeError(f"GISTEMP dataset unavailable: {e}")

    @classmethod
    def parse_csv(cls, file_path: str) -> List[Dict[str, Any]]:
        observations = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        # Find header line starting with Year,Jan
        header_idx = -1
        for idx, line in enumerate(lines):
            if line.strip().startswith("Year,Jan"):
                header_idx = idx
                break

        if header_idx == -1:
            raise ValueError("Invalid GISTEMP CSV format: Header starting with 'Year,Jan' not found.")

        reader = csv.reader(lines[header_idx:])
        headers = next(reader)
        col_indices = {m: headers.index(m) for m in MONTH_MAP.keys() if m in headers}

        for row in reader:
            if not row or len(row) < 13:
                continue
            year_token = row[0].strip()
            if not year_token.isdigit():
                continue
            year = int(year_token)

            for month_name, col_idx in col_indices.items():
                if col_idx >= len(row):
                    continue
                val_token = row[col_idx].strip()
                # Skip missing markers or empty tokens
                if not val_token or val_token.startswith("***") or val_token == "NA":
                    continue
                try:
                    val = float(val_token)
                    month_num = MONTH_MAP[month_name]
                    date_str = f"{year}-{month_num:02d}"
                    observations.append({
                        "date": date_str,
                        "year": year,
                        "month": month_num,
                        "value": val,
                        "raw_value": val_token,
                        "uncertainty": None,
                        "latitude": None,
                        "longitude": None,
                        "quality_flag": "OFFICIAL_NASA"
                    })
                except ValueError:
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
            logger.debug(f"GISTEMP dataset already populated ({existing_count} records).")
            return

        # Fetch or use cache
        if force_refresh or not os.path.exists(cache_path):
            await cls.fetch_and_cache()

        observations = cls.parse_csv(cache_path)
        logger.info(f"Parsed {len(observations)} monthly GISTEMP observations (1880–present).")

        ds_repo.upsert(DATASET_META)
        obs_repo.bulk_replace(DATASET_META["id"], observations)
        logger.info(f"Database successfully synchronized with {len(observations)} GISTEMP records.")
