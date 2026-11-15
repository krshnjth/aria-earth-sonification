import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.utils.http_client import HttpClient
from app.database.repositories import DatasetRepository, ObservationRepository
from app.utils.validation import validate_coordinates

class PowerService:
    @staticmethod
    def get_cache_filename(lat: float, lon: float, start_year: int, end_year: int) -> str:
        return os.path.join(
            settings.DATA_CACHE_DIR,
            f"power_{lat:.2f}_{lon:.2f}_{start_year}_{end_year}.json"
        )

    @classmethod
    async def fetch_regional_data(
        cls,
        latitude: float,
        longitude: float,
        start_year: int = 2020,
        end_year: int = 2024,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        validate_coordinates(latitude, longitude)
        cache_file = cls.get_cache_filename(latitude, longitude, start_year, end_year)

        if not force_refresh and os.path.exists(cache_file):
            logger.info(f"Loading NASA POWER cache from {cache_file}")
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading cache file {cache_file}: {e}")

        params = {
            "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR",
            "community": "RE",
            "longitude": f"{longitude:.4f}",
            "latitude": f"{latitude:.4f}",
            "start": str(start_year),
            "end": str(end_year),
            "format": "JSON"
        }

        try:
            logger.info(f"Requesting NASA POWER API for ({latitude}, {longitude}) [{start_year}-{end_year}]")
            resp = await HttpClient.fetch_with_retry(settings.NASA_POWER_BASE_URL, params=params)
            data = resp.json()

            # Save to disk cache
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            return data
        except Exception as exc:
            logger.warning(f"Failed to fetch live NASA POWER data: {exc}. Checking local fallback cache...")
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            # Check if any power_*.json exists in cache as fallback
            for fn in os.listdir(settings.DATA_CACHE_DIR):
                if fn.startswith("power_") and fn.endswith(".json"):
                    with open(os.path.join(settings.DATA_CACHE_DIR, fn), "r", encoding="utf-8") as f:
                        return json.load(f)
            raise RuntimeError(f"NASA POWER meteorological data unavailable: {exc}")

    @classmethod
    def parse_power_json(cls, data: Dict[str, Any], lat: float, lon: float) -> List[Dict[str, Any]]:
        observations = []
        properties = data.get("properties", {})
        parameter_data = properties.get("parameter", {})
        t2m_data = parameter_data.get("T2M", {})

        for date_code, val in sorted(t2m_data.items()):
            # date_code is "YYYYMM" (or "YYYY13" for annual mean)
            if len(date_code) != 6 or date_code.endswith("13"):
                continue
            try:
                year = int(date_code[:4])
                month = int(date_code[4:6])
                # Skip invalid fill values (NASA POWER uses -999.0)
                if val == -999.0 or val < -100.0 or val > 70.0:
                    continue

                date_str = f"{year}-{month:02d}"
                observations.append({
                    "date": date_str,
                    "year": year,
                    "month": month,
                    "value": float(val),
                    "raw_value": str(val),
                    "uncertainty": 0.5,
                    "latitude": lat,
                    "longitude": lon,
                    "quality_flag": "NASA_POWER_MERRA2"
                })
            except (ValueError, IndexError):
                continue

        observations.sort(key=lambda x: x["date"])
        return observations

    @classmethod
    async def get_or_create_regional_series(
        cls,
        db: Session,
        latitude: float,
        longitude: float,
        start_year: int = 2020,
        end_year: int = 2024,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        dataset_id = f"regional_power_{latitude:.2f}_{longitude:.2f}"
        ds_repo = DatasetRepository(db)
        obs_repo = ObservationRepository(db)

        dataset = ds_repo.get(dataset_id)
        existing_count = obs_repo.count(dataset_id)

        if force_refresh or not dataset or existing_count == 0:
            raw_data = await cls.fetch_regional_data(latitude, longitude, start_year, end_year, force_refresh)
            observations = cls.parse_power_json(raw_data, latitude, longitude)

            dataset_meta = {
                "id": dataset_id,
                "title": f"Regional Meteorological Surface Observations ({latitude:.2f}°N, {longitude:.2f}°E)",
                "organization": "NASA Langley Research Center (LaRC) POWER Project",
                "source_url": f"{settings.NASA_POWER_BASE_URL}?latitude={latitude}&longitude={longitude}",
                "version": "MERRA-2 / GEOS-5.12.4 assimilation",
                "measurement_name": "Surface Air Temperature at 2 Meters (T2M)",
                "unit": "°C",
                "baseline": "Point Observation (Absolute, NOT global anomaly)",
                "temporal_resolution": "monthly",
                "geographic_coverage": f"Point ({latitude:.2f}, {longitude:.2f})",
                "is_active": True
            }

            ds_repo.upsert(dataset_meta)
            obs_repo.bulk_replace(dataset_id, observations)
            dataset = ds_repo.get(dataset_id)

        observations_models = obs_repo.get_time_series(dataset_id, start_year, end_year)
        return {
            "dataset": dataset,
            "observations": observations_models
        }
