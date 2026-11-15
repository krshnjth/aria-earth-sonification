# ARIA Backend — Scientific Earth Sonification API

> **"Hear the planet. Understand its changes."**  
> Empirical environmental data pipeline connecting NASA, NOAA, and Copernicus planetary observations directly to ARIA's data sonification engine.

---

## 1. Overview & Architecture

The ARIA backend serves real, standardized scientific observations to drive dynamic 3D globe visualizations and real-time Web Audio API sound synthesis. 

### Core Tech Stack
- **Python 3.11+**
- **FastAPI**: Asynchronous high-performance REST framework
- **Pydantic v2**: Type enforcement & schema validation
- **SQLAlchemy 2.0**: Relational ORM (SQLite for development, PostgreSQL-ready)
- **HTTPX**: Robust asynchronous external data retrieval with exponential backoff
- **Pandas & NumPy**: Time series normalization, interpolation, and anomaly parsing

### Architectural Data Flow
```
[NASA / NOAA Sources] 
         │ (HTTPX Async Client with Retries & TLS Validation)
         ▼
[Ingestion Services: GISTEMP, NOAA CO2, Sea Level, POWER]
         │ (Parsing, Quality Flagging & File Caching in data/cache/)
         ▼
[SQLAlchemy Repository Layer] ──▶ [SQLite DB: data/aria.db]
         │
         ▼
[Unified REST API: /api/v1/*]
         │ (JSON Response with Metadata & Provenance)
         ▼
[ARIA Web Observatory Frontend] ──▶ [Web Audio Synthesizer & 3D Shaders]
```

---

## 2. Integrated Scientific Datasets & Attribution

| Dimension | Physical Variable | Authoritative Source | Unit | Baseline Period | Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Climate** | Global Surface Temperature Anomaly | [NASA GISTEMP v4 LOTI](https://data.giss.nasa.gov/gistemp/) | °C | 1951–1980 Mean | Global (1880–present) |
| **Atmosphere** | In-Situ Carbon Dioxide ($CO_2$) | [NOAA GML Mauna Loa](https://gml.noaa.gov/ccgg/trends/) | ppm | 280 ppm Pre-Industrial | In-situ Mauna Loa (1958–present) |
| **Oceans** | Global Mean Sea Level (GMSL) | [NOAA / NASA Altimetry](https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/) | mm | 1993–2008 Altimeter Mean | Global ocean 66°S–66°N (1993–present) |
| **Regional** | Point Surface Air Temp & Precip | [NASA POWER API](https://power.larc.nasa.gov/) | °C, mm/d | Point Absolute Observation | 18 Global ARIA Hotspots |
| **Imagery** | Satellite Earth Imagery Layers | [NASA GIBS](https://nasa-gibs.github.io/gibs-api-docs/) | WMTS Tiles | EPSG:4326 True Color | Global daily coverage |

---

## 3. Windows PowerShell Installation & Startup

### Step 1: Open PowerShell and navigate to the backend directory
```powershell
cd C:\Users\remya\.gemini\antigravity\scratch\aria-earth-sonification\backend
```

### Step 2: Create and activate a Python virtual environment (Optional if using system Python)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run test suite to verify all scientific parsers
```powershell
pytest -v
```

### Step 5: Start the Uvicorn development server
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The interactive Swagger UI documentation is available at:
👉 **http://127.0.0.1:8000/docs**

---

## 4. API Endpoints Reference

### Health & Metadata
- `GET /api/v1/health`: Server status, database health, and loaded dataset count.
- `GET /api/v1/datasets`: Catalog of active empirical datasets.
- `GET /api/v1/metadata`: System provenance and source institution details.
- `GET /api/v1/imagery/layers`: NASA GIBS satellite layer definitions.

### Climate & Global Temperatures
- `GET /api/v1/climate/temperature/global`: NASA GISTEMP LOTI monthly anomalies (1880–present).
  - Optional Query Params: `start_year`, `end_year`, `force_refresh`.
- `GET /api/v1/climate/temperature/regional`: NASA POWER point meteorological data.
  - Query Params: `latitude`, `longitude`, `start_year`, `end_year`.

### Oceans & Sea Level
- `GET /api/v1/oceans/sea-level/global`: NOAA/NASA multi-mission satellite altimetry GMSL (1993–present).
  - Optional Query Params: `start_year`, `end_year`, `force_refresh`.

### Atmosphere & CO₂
- `GET /api/v1/atmosphere/co2/mauna-loa`: NOAA GML Mauna Loa monthly in-situ $CO_2$ (1958–present).
  - Optional Query Params: `start_year`, `end_year`, `force_refresh`.

### Regional Hotspots
- `GET /api/v1/regions`: Catalog of all 18 ARIA global biomes and hotspots.
- `GET /api/v1/regions/{region_id}/climate`: NASA POWER weather series for a specific hotspot.
- `GET /api/v1/regions/{region_id}/metadata`: Hotspot acoustic and biome characteristics.

---

## 5. Scientific Limitations & Data Integrity Policies

1. **No Fabricated Telemetry**: ARIA explicitly distinguishes between global anomalies (e.g. NASA GISTEMP LOTI) and regional point measurements (e.g. NASA POWER 2-meter air temperature).
2. **Missing Observation Protocol**: Missing records are preserved as `None`/null with explicit quality flags rather than silently filled with zeros or speculative linear extrapolation.
3. **Attribution**: All visualizations and audio representations clearly attribute the originating scientific institution.
