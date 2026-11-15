from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class DatasetMetadata(BaseModel):
    id: str = Field(..., description="Unique dataset identifier")
    title: str = Field(..., description="Full descriptive dataset title")
    organization: str = Field(..., description="Source institution or agency")
    source_url: str = Field(..., description="Authoritative origin download URL")
    version: Optional[str] = Field(None, description="Dataset release or processing version")
    measurement_name: str = Field(..., description="Physical variable name")
    unit: str = Field(..., description="Standardized measurement unit")
    baseline: Optional[str] = Field(None, description="Reference climatological period or baseline")
    temporal_resolution: str = Field("monthly", description="Temporal frequency of observations")
    geographic_coverage: str = Field("global", description="Spatial scope (global, regional, point)")

class ObservationPoint(BaseModel):
    date: str = Field(..., description="ISO or period timestamp (YYYY-MM or YYYY)")
    year: int = Field(..., description="Observation year")
    month: Optional[int] = Field(None, description="Observation month (1-12) if monthly")
    value: float = Field(..., description="Primary numerical observation value")
    raw_value: Optional[str] = Field(None, description="Exact textual token from raw source file")
    uncertainty: Optional[float] = Field(None, description="Reported scientific uncertainty or margin")
    latitude: Optional[float] = Field(None, description="Latitude coordinate if spatially bound")
    longitude: Optional[float] = Field(None, description="Longitude coordinate if spatially bound")
    quality_flag: Optional[str] = Field("VALID", description="Scientific data provenance or quality tag")

class ResponseMetadata(BaseModel):
    retrieved_at: str = Field(..., description="Server query or retrieval timestamp")
    last_observation: Optional[str] = Field(None, description="Latest available observation date in series")
    is_cached: bool = Field(True, description="Whether returned from local database or cache")
    quality: str = Field("Official scientific observation archive", description="Quality statement")
    record_count: int = Field(..., description="Total observation count in returned slice")

class StandardTimeSeriesResponse(BaseModel):
    dataset: DatasetMetadata
    data: List[ObservationPoint]
    metadata: ResponseMetadata

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    database_status: str
    cached_datasets: int
    environment: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: str
