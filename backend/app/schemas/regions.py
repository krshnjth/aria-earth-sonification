from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.schemas.common import DatasetMetadata, ObservationPoint, ResponseMetadata

class RegionSummary(BaseModel):
    id: str
    name: str
    location: str
    latitude: float
    longitude: float
    category: str
    badge: str
    sound_type: str
    sound_description: str
    icon: str

class RegionalClimateResponse(BaseModel):
    region_id: Optional[str] = None
    name: Optional[str] = None
    latitude: float
    longitude: float
    dataset: DatasetMetadata
    parameters: Dict[str, str] = Field(..., description="Parameter code to unit/description mapping")
    data: List[ObservationPoint]
    metadata: ResponseMetadata
