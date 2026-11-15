from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.repositories import DatasetRepository
from app.schemas.common import DatasetMetadata
from app.services.gibs_service import GibsService

router = APIRouter(tags=["Dataset & System Metadata"])

@router.get("/datasets", response_model=List[DatasetMetadata])
def list_datasets(db: Session = Depends(get_db)):
    ds_repo = DatasetRepository(db)
    datasets = ds_repo.list_all()
    return [
        DatasetMetadata(
            id=d.id,
            title=d.title,
            organization=d.organization,
            source_url=d.source_url,
            version=d.version,
            measurement_name=d.measurement_name,
            unit=d.unit,
            baseline=d.baseline,
            temporal_resolution=d.temporal_resolution,
            geographic_coverage=d.geographic_coverage
        )
        for d in datasets
    ]

@router.get("/metadata")
def get_system_metadata(db: Session = Depends(get_db)):
    ds_repo = DatasetRepository(db)
    datasets = ds_repo.list_all()
    return {
        "system": "ARIA - Earth Sonification System Backend",
        "tagline": "Hear the planet. Understand its changes.",
        "scientific_integrity_policy": "Strict empirical provenance. No simulated or fabricated measurements.",
        "active_datasets_count": len(datasets),
        "primary_scientific_institutions": [
            "NASA Goddard Institute for Space Studies (GISS)",
            "NOAA Global Monitoring Laboratory (GML)",
            "NOAA Laboratory for Satellite Altimetry",
            "NASA Langley Research Center (LaRC) POWER Project",
            "NASA Earth Science Data and Information System (ESDIS) GIBS"
        ],
        "datasets": [
            {
                "id": d.id,
                "title": d.title,
                "organization": d.organization,
                "unit": d.unit,
                "baseline": d.baseline,
                "last_retrieved": d.last_retrieved.isoformat() if d.last_retrieved else None
            }
            for d in datasets
        ]
    }

@router.get("/imagery/layers")
def get_imagery_layers():
    return {
        "service": "NASA GIBS (Global Imagery Browse Services)",
        "endpoint": "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi",
        "documentation": "https://nasa-gibs.github.io/gibs-api-docs/",
        "supported_projections": ["EPSG:4326", "EPSG:3857"],
        "layers": GibsService.get_layers()
    }
