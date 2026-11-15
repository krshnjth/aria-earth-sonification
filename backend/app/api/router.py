from fastapi import APIRouter
from app.api.routes import health, climate, oceans, atmosphere, regions, metadata

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(climate.router)
api_router.include_router(oceans.router)
api_router.include_router(atmosphere.router)
api_router.include_router(regions.router)
api_router.include_router(metadata.router)
