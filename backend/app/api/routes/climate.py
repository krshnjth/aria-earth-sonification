from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.repositories import DatasetRepository, ObservationRepository
from app.schemas.common import StandardTimeSeriesResponse, DatasetMetadata, ObservationPoint, ResponseMetadata
from app.schemas.regions import RegionalClimateResponse
from app.services.gistemp_service import GistempService, DATASET_META
from app.services.power_service import PowerService
from app.utils.validation import validate_coordinates, validate_year_range

router = APIRouter(prefix="/climate", tags=["Climate"])

@router.get("/temperature/global", response_model=StandardTimeSeriesResponse)
async def get_global_temperature(
    start_year: Optional[int] = Query(None, description="Starting year (>= 1880)"),
    end_year: Optional[int] = Query(None, description="Ending year (<= 2030)"),
    force_refresh: bool = Query(False, description="Bypass cache and re-download official dataset"),
    db: Session = Depends(get_db)
):
    validate_year_range(start_year, end_year, min_year=1880, max_year=2030)
    await GistempService.sync_database(db, force_refresh=force_refresh)

    ds_repo = DatasetRepository(db)
    obs_repo = ObservationRepository(db)

    dataset = ds_repo.get(DATASET_META["id"])
    if not dataset:
        raise HTTPException(status_code=500, detail="GISTEMP dataset metadata missing from database.")

    observations = obs_repo.get_time_series(DATASET_META["id"], start_year=start_year, end_year=end_year)
    latest_date = obs_repo.get_latest_date(DATASET_META["id"])

    data_points = [
        ObservationPoint(
            date=o.date,
            year=o.year,
            month=o.month,
            value=o.value,
            raw_value=o.raw_value,
            uncertainty=o.uncertainty,
            latitude=o.latitude,
            longitude=o.longitude,
            quality_flag=o.quality_flag
        )
        for o in observations
    ]

    return StandardTimeSeriesResponse(
        dataset=DatasetMetadata(
            id=dataset.id,
            title=dataset.title,
            organization=dataset.organization,
            source_url=dataset.source_url,
            version=dataset.version,
            measurement_name=dataset.measurement_name,
            unit=dataset.unit,
            baseline=dataset.baseline,
            temporal_resolution=dataset.temporal_resolution,
            geographic_coverage=dataset.geographic_coverage
        ),
        data=data_points,
        metadata=ResponseMetadata(
            retrieved_at=datetime.utcnow().isoformat() + "Z",
            last_observation=latest_date,
            is_cached=not force_refresh,
            quality="NASA GISS GISTEMP v4 LOTI (1951-1980 baseline anomaly)",
            record_count=len(data_points)
        )
    )

@router.get("/temperature/regional", response_model=RegionalClimateResponse)
async def get_regional_temperature(
    latitude: float = Query(..., description="Latitude coordinate [-90.0, 90.0]"),
    longitude: float = Query(..., description="Longitude coordinate [-180.0, 180.0]"),
    start_year: int = Query(2020, description="Start year"),
    end_year: int = Query(2024, description="End year"),
    force_refresh: bool = Query(False, description="Bypass local cache"),
    db: Session = Depends(get_db)
):
    validate_coordinates(latitude, longitude)
    validate_year_range(start_year, end_year, min_year=1981, max_year=2026)

    result = await PowerService.get_or_create_regional_series(
        db,
        latitude=latitude,
        longitude=longitude,
        start_year=start_year,
        end_year=end_year,
        force_refresh=force_refresh
    )

    dataset = result["dataset"]
    obs_list = result["observations"]

    data_points = [
        ObservationPoint(
            date=o.date,
            year=o.year,
            month=o.month,
            value=o.value,
            raw_value=o.raw_value,
            uncertainty=o.uncertainty,
            latitude=latitude,
            longitude=longitude,
            quality_flag=o.quality_flag
        )
        for o in obs_list
    ]

    return RegionalClimateResponse(
        region_id=None,
        name=f"Point ({latitude:.2f}°N, {longitude:.2f}°E)",
        latitude=latitude,
        longitude=longitude,
        dataset=DatasetMetadata(
            id=dataset.id,
            title=dataset.title,
            organization=dataset.organization,
            source_url=dataset.source_url,
            version=dataset.version,
            measurement_name=dataset.measurement_name,
            unit=dataset.unit,
            baseline=dataset.baseline,
            temporal_resolution=dataset.temporal_resolution,
            geographic_coverage=dataset.geographic_coverage
        ),
        parameters={
            "T2M": "Temperature at 2 Meters (°C)",
            "T2M_MAX": "Maximum Temperature at 2 Meters (°C)",
            "T2M_MIN": "Minimum Temperature at 2 Meters (°C)",
            "PRECTOTCORR": "Precipitation Corrected (mm/day)"
        },
        data=data_points,
        metadata=ResponseMetadata(
            retrieved_at=datetime.utcnow().isoformat() + "Z",
            last_observation=data_points[-1].date if data_points else None,
            is_cached=not force_refresh,
            quality="NASA POWER MERRA-2 assimilation (Local point temperature, NOT global anomaly)",
            record_count=len(data_points)
        )
    )
