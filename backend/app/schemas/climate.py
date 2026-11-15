from typing import List, Optional
from pydantic import BaseModel
from app.schemas.common import DatasetMetadata, ObservationPoint, ResponseMetadata

class GlobalTemperatureResponse(BaseModel):
    dataset: DatasetMetadata
    data: List[ObservationPoint]
    metadata: ResponseMetadata
