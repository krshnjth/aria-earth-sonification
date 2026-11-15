from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.database.connection import get_db
from app.database.repositories import DatasetRepository
from app.schemas.common import HealthResponse

router = APIRouter(tags=["System Health"])

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    db_status = "operational"
    cached_count = 0
    try:
        db.execute(text("SELECT 1"))
        cached_count = len(DatasetRepository(db).list_all())
    except Exception as e:
        db_status = f"degraded: {str(e)}"

    return HealthResponse(
        status="healthy" if db_status == "operational" else "degraded",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        database_status=db_status,
        cached_datasets=cached_count,
        environment="development" if settings.DEBUG else "production"
    )
