from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.common import DatasetMetadata, ObservationPoint, ResponseMetadata
from app.schemas.regions import RegionSummary, RegionalClimateResponse
from app.services.region_catalog import RegionCatalog
from app.services.power_service import PowerService
from app.utils.validation import validate_year_range

router = APIRouter(prefix="/regions", tags=["Global Regions & Hotspots"])

@router.get("", response_model=List[RegionSummary])
def list_regions():
    hotspots = RegionCatalog.list_all()
    return [
        RegionSummary(
            id=h["id"],
            name=h["name"],
            location=h["location"],
            latitude=h["latitude"],
            longitude=h["longitude"],
            category=h["category"],
            badge=h["badge"],
            sound_type=h["sound_type"],
            sound_description=h["sound_description"],
            icon=h["icon"]
        )
        for h in hotspots
    ]

@router.get("/{region_id}/metadata", response_model=RegionSummary)
def get_region_metadata(
    region_id: str = Path(..., description="Hotspot identifier e.g. amazon, mojave, gbr")
):
    region = RegionCatalog.get_by_id(region_id)
    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_id}' not found in ARIA catalog.")
    return RegionSummary(
        id=region["id"],
        name=region["name"],
        location=region["location"],
        latitude=region["latitude"],
        longitude=region["longitude"],
        category=region["category"],
        badge=region["badge"],
        sound_type=region["sound_type"],
        sound_description=region["sound_description"],
        icon=region["icon"]
    )

@router.get("/{region_id}/climate", response_model=RegionalClimateResponse)
async def get_region_climate(
    region_id: str = Path(..., description="Hotspot identifier"),
    start_year: int = Query(2020, description="Start year"),
    end_year: int = Query(2024, description="End year"),
    force_refresh: bool = Query(False, description="Bypass local cache"),
    db: Session = Depends(get_db)
):
    region = RegionCatalog.get_by_id(region_id)
    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_id}' not found in ARIA catalog.")

    validate_year_range(start_year, end_year, min_year=1981, max_year=2026)

    result = await PowerService.get_or_create_regional_series(
        db,
        latitude=region["latitude"],
        longitude=region["longitude"],
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
            latitude=region["latitude"],
            longitude=region["longitude"],
            quality_flag=o.quality_flag
        )
        for o in obs_list
    ]

    return RegionalClimateResponse(
        region_id=region["id"],
        name=region["name"],
        latitude=region["latitude"],
        longitude=region["longitude"],
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
            quality=f"NASA POWER Meteorological Station for {region['name']} ({region['location']})",
            record_count=len(data_points)
        )
    )
