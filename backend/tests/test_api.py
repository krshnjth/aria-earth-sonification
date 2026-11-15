import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "ARIA" in data["system"]

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_status"] == "operational"
    assert data["cached_datasets"] >= 3

def test_list_datasets():
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    dataset_ids = [d["id"] for d in data]
    assert "global_temperature" in dataset_ids
    assert "atmosphere_co2_mlo" in dataset_ids
    assert "atmosphere_methane_global" in dataset_ids
    assert "global_sea_level" in dataset_ids

def test_system_metadata():
    response = client.get("/api/v1/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "primary_scientific_institutions" in data
    assert len(data["primary_scientific_institutions"]) > 0

def test_gistemp_global_temperature():
    response = client.get("/api/v1/climate/temperature/global")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset"]["id"] == "global_temperature"
    assert data["dataset"]["unit"] == "°C"
    assert data["dataset"]["baseline"] == "1951-1980 Mean"
    assert len(data["data"]) > 1000
    # Spot-check 1880-01 value matches official NASA record (-0.19)
    first_obs = data["data"][0]
    assert first_obs["date"] == "1880-01"
    assert first_obs["value"] == -0.19

def test_gistemp_year_filtering():
    response = client.get("/api/v1/climate/temperature/global?start_year=1990&end_year=2025")
    assert response.status_code == 200
    data = response.json()
    for point in data["data"]:
        assert 1990 <= point["year"] <= 2025

def test_climate_invalid_year_range():
    response = client.get("/api/v1/climate/temperature/global?start_year=2025&end_year=1990")
    assert response.status_code == 400
    assert "cannot be greater than" in response.json()["detail"]

def test_noaa_co2_mauna_loa():
    response = client.get("/api/v1/atmosphere/co2/mauna-loa")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset"]["id"] == "atmosphere_co2_mlo"
    assert data["dataset"]["unit"] == "ppm"
    assert "NOAA" in data["dataset"]["organization"]
    assert len(data["data"]) > 500
    # Values should be realistic (above 310 ppm, below 450 ppm)
    assert data["data"][0]["value"] > 310.0
    assert data["data"][-1]["value"] > 400.0

def test_noaa_co2_filtered():
    response = client.get("/api/v1/atmosphere/co2/mauna-loa?start_year=2015&end_year=2024")
    assert response.status_code == 200
    data = response.json()
    for point in data["data"]:
        assert 2015 <= point["year"] <= 2024

def test_noaa_ch4_methane():
    response = client.get("/api/v1/atmosphere/methane/global")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset"]["id"] == "atmosphere_methane_global"
    assert data["dataset"]["unit"] == "ppb"
    assert "NOAA" in data["dataset"]["organization"]
    assert len(data["data"]) > 400
    # Values should be realistic (above 1500 ppb, below 2200 ppb)
    assert data["data"][0]["value"] > 1500.0
    assert data["data"][-1]["value"] > 1900.0

def test_noaa_ch4_filtered():
    response = client.get("/api/v1/atmosphere/methane/global?start_year=2010&end_year=2024")
    assert response.status_code == 200
    data = response.json()
    for point in data["data"]:
        assert 2010 <= point["year"] <= 2024

def test_global_sea_level():
    response = client.get("/api/v1/oceans/sea-level/global")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset"]["id"] == "global_sea_level"
    assert data["dataset"]["unit"] == "mm"
    assert len(data["data"]) > 200

def test_global_sea_level_filtered():
    response = client.get("/api/v1/oceans/sea-level/global?start_year=2000&end_year=2020")
    assert response.status_code == 200
    data = response.json()
    for point in data["data"]:
        assert 2000 <= point["year"] <= 2020

def test_nasa_power_regional_temperature():
    response = client.get(
        "/api/v1/climate/temperature/regional?latitude=-3.4&longitude=-62.2&start_year=2022&end_year=2023"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == -3.4
    assert data["longitude"] == -62.2
    assert "T2M" in data["parameters"]
    assert len(data["data"]) > 0

def test_invalid_coordinates():
    response = client.get("/api/v1/climate/temperature/regional?latitude=105.0&longitude=0.0")
    assert response.status_code == 400
    assert "Latitude must be within" in response.json()["detail"]

def test_regions_catalog():
    response = client.get("/api/v1/regions")
    assert response.status_code == 200
    regions = response.json()
    assert len(regions) == 18
    region_ids = [r["id"] for r in regions]
    assert "amazon" in region_ids
    assert "siberia" in region_ids
    assert "mlo" in region_ids

def test_region_climate_amazon():
    response = client.get("/api/v1/regions/amazon/climate?start_year=2022&end_year=2023")
    assert response.status_code == 200
    data = response.json()
    assert data["region_id"] == "amazon"
    assert "Amazon Basin" in data["name"]
    assert len(data["data"]) > 0

def test_region_not_found():
    response = client.get("/api/v1/regions/atlantis_underwater/climate")
    assert response.status_code == 404

def test_gibs_imagery_layers():
    response = client.get("/api/v1/imagery/layers")
    assert response.status_code == 200
    data = response.json()
    assert len(data["layers"]) >= 4
    layer_ids = [l["id"] for l in data["layers"]]
    assert "BlueMarble_NextGeneration" in layer_ids
