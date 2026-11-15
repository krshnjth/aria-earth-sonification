from typing import List, Dict, Any
from app.core.config import settings

class GibsService:
    LAYERS: List[Dict[str, Any]] = [
        {
            "id": "BlueMarble_NextGeneration",
            "title": "NASA Blue Marble: Next Generation (MODIS Mosaic)",
            "organization": "NASA Earth Science Data and Information System (ESDIS)",
            "projection": "EPSG:4326",
            "tile_format": "image/jpeg",
            "matrix_set": "500m",
            "tile_url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/BlueMarble_NextGeneration/default/{Time}/500m/{TileMatrix}/{TileRow}/{TileCol}.jpeg",
            "time_enabled": False,
            "description": "Standardized true-color planetary surface base mosaic free of clouds and atmospheric scattering."
        },
        {
            "id": "MODIS_Terra_CorrectedReflectance_TrueColor",
            "title": "MODIS Terra Corrected Reflectance (True Color)",
            "organization": "NASA ESDIS / GIBS",
            "projection": "EPSG:4326",
            "tile_format": "image/jpeg",
            "matrix_set": "250m",
            "tile_url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{Time}/250m/{TileMatrix}/{TileRow}/{TileCol}.jpeg",
            "time_enabled": True,
            "description": "Daily near-real-time true-color imagery from the Moderate Resolution Imaging Spectroradiometer (MODIS) aboard Terra."
        },
        {
            "id": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
            "title": "VIIRS Suomi NPP Corrected Reflectance",
            "organization": "NASA / NOAA Suomi National Polar-orbiting Partnership",
            "projection": "EPSG:4326",
            "tile_format": "image/jpeg",
            "matrix_set": "250m",
            "tile_url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/{Time}/250m/{TileMatrix}/{TileRow}/{TileCol}.jpeg",
            "time_enabled": True,
            "description": "High-resolution visible spectrum daily composite imagery from the VIIRS instrument."
        },
        {
            "id": "AIRS_CO_Total_Column_Day",
            "title": "AIRS Carbon Monoxide (CO) Total Column (Day)",
            "organization": "NASA Jet Propulsion Laboratory (JPL) / Atmospheric Infrared Sounder",
            "projection": "EPSG:4326",
            "tile_format": "image/png",
            "matrix_set": "2km",
            "tile_url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/AIRS_CO_Total_Column_Day/default/{Time}/2km/{TileMatrix}/{TileRow}/{TileCol}.png",
            "time_enabled": True,
            "description": "Atmospheric constituent monitoring indicating wildfire smoke plumes and combustion transport."
        }
    ]

    @classmethod
    def get_layers(cls) -> List[Dict[str, Any]]:
        return cls.LAYERS

    @classmethod
    def get_layer_by_id(cls, layer_id: str) -> Dict[str, Any] | None:
        for layer in cls.LAYERS:
            if layer["id"] == layer_id:
                return layer
        return None
