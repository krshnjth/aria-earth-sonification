import os
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "ARIA - Earth Sonification System Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Base directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DATA_CACHE_DIR: Path = DATA_DIR / "cache"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'aria.db'}"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://krshnjth.github.io",
        "null",  # allow file:// origin in local browser testing
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # HTTP Client Configuration
    HTTP_TIMEOUT: float = 15.0
    HTTP_MAX_RETRIES: int = 3
    
    # Cache settings
    CACHE_EXPIRATION_HOURS: int = 24
    
    # Official Scientific Dataset URLs
    GISTEMP_URL: str = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    NOAA_CO2_URL: str = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
    NOAA_GMSL_URL: str = "https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/slr/slr_sla_gbl_free_all_66.csv"
    NASA_POWER_BASE_URL: str = "https://power.larc.nasa.gov/api/temporal/monthly/point"
    NASA_GIBS_WMTS_URL: str = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi"
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.DATA_CACHE_DIR, exist_ok=True)
