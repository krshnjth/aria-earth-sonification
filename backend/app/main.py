from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.connection import init_db, SessionLocal
from app.utils.http_client import HttpClient
from app.api.router import api_router
from app.services.gistemp_service import GistempService
from app.services.co2_service import Co2Service
from app.services.ch4_service import Ch4Service
from app.services.sea_level_service import SeaLevelService

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ARIA Earth Sonification Backend...")
    # Initialize database tables
    init_db()
    
    # Pre-sync core baseline datasets from local cache/remote if not already populated
    db = SessionLocal()
    try:
        logger.info("Synchronizing core datasets in database...")
        await GistempService.sync_database(db)
        await Co2Service.sync_database(db)
        await Ch4Service.sync_database(db)
        await SeaLevelService.sync_database(db)
        logger.info("Core scientific datasets successfully loaded.")
    except Exception as e:
        logger.warning(f"Initial dataset synchronization notice: {e}")
    finally:
        db.close()
        
    yield
    
    logger.info("Shutting down ARIA Backend...")
    await HttpClient.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Scientific Backend API for ARIA — Earth Sonification System. Provides real NASA & NOAA empirical observations.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred processing the scientific dataset.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "path": request.url.path
        }
    )

@app.get("/", tags=["Root"])
def root_status():
    return {
        "system": "ARIA - Earth Sonification System Backend",
        "tagline": "Hear the planet. Understand its changes.",
        "status": "online",
        "docs_url": "/docs",
        "health_url": f"{settings.API_V1_STR}/health",
        "version": "1.0.0"
    }

# Mount unified /api/v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)
