from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.repositories import DatasetRepository, ObservationRepository
from app.schemas.common import StandardTimeSeriesResponse, DatasetMetadata, ObservationPoint, ResponseMetadata
from app.services.sea_level_service import SeaLevelService, DATASET_META
from app.utils.validation import validate_year_range

router = APIRouter(prefix="/oceans", tags=["Oceans"])

@router.get("/sea-level/global", response_model=StandardTimeSeriesResponse)
async def get_global_sea_level(
    start_year: Optional[int] = Query(None, description="Starting year (>= 1992)"),
    end_year: Optional[int] = Query(None, description="Ending year (<= 2030)"),
    force_refresh: bool = Query(False, description="Bypass cache and re-download official dataset"),
    db: Session = Depends(get_db)
):
    validate_year_range(start_year, end_year, min_year=1992, max_year=2030)
    await SeaLevelService.sync_database(db, force_refresh=force_refresh)

    ds_repo = DatasetRepository(db)
    obs_repo = ObservationRepository(db)

    dataset = ds_repo.get(DATASET_META["id"])
    if not dataset:
        raise HTTPException(status_code=500, detail="GMSL dataset metadata missing from database.")

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
            quality="NOAA / NASA Multi-Mission Satellite Altimetry Global Sea Level Anomaly",
            record_count=len(data_points)
        )
    )
