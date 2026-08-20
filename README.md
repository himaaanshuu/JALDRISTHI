# JAL-DRISHTI

**AI-Powered Groundwater Intelligence Platform for India**

JAL-DRISHTI is a comprehensive groundwater assessment and monitoring platform covering all 36 states and union territories of India. It integrates official CGWB/IN-GRES data with an AI chat assistant, interactive map, trend analytics, and risk scoring — all in a single deployable application.

---

## Features

- **Interactive Map** — Leaflet-based map with 192+ groundwater blocks color-coded by category (Safe, Semi-Critical, Critical, Over-Exploited), restricted to Indian boundaries
- **AI Chat Assistant** — Natural language queries in English, Hindi, and Hinglish with 9+ intent types (status, compare, risk, top blocks, trend, category, help, search, export)
- **Trend Analytics** — Area chart showing extraction, recharge, and stage trends across 4 assessment years (2020, 2022, 2024, 2025)
- **Risk Analysis** — AI-derived risk scores for each block based on extraction stage, recharge deficit, and multi-year trends
- **Data Provenance** — Full source tracking with official data import, validation reports, and evidence citations
- **Dark Geological Theme** — Custom "Deep Earth" design system with Instrument Serif, DM Sans, and JetBrains Mono typography
- **State & District Coverage** — 522 official records across all 36 states/UTs, 4 assessment years, 8 categories

---

## Architecture

```
jaldrishti/
├── backend/
│   ├── main.py                  # FastAPI application (21 endpoints)
│   ├── database.py              # SQLAlchemy models (GroundWater, DataSource, Evidence)
│   ├── parser.py                # Intent parser (English/Hindi/Hinglish)
│   ├── requirements.txt         # Python dependencies
│   ├── test_parser.py           # 42 unit tests for parser
│   └── scripts/
│       ├── import_ingres_data.py    # Data ingestion from OpenCity.in
│       └── validate_ingres_data.py  # Data quality validation
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Dashboard, Map, Chat pages
│   │   ├── components/
│   │   │   ├── ChatAssistant.tsx # AI chat interface
│   │   │   └── GroundwaterMap.tsx # Leaflet map component
│   │   └── index.css            # Design system (CSS variables, animations)
│   ├── index.html               # Google Fonts (Instrument Serif, DM Sans, JetBrains Mono)
│   └── package.json             # React + Vite + TypeScript + Tailwind
└── data/                        # SQLite database (gitignored)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Recharts, Leaflet |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite |
| Data Source | CGWB/IN-GRES via OpenCity.in CKAN API |
| Fonts | Instrument Serif, DM Sans, JetBrains Mono |

---

## Prerequisites

- **Python 3.10+** (tested with Python 3.14)
- **Node.js 18+** and npm
- **Git**

---

## Clone & Setup

### 1. Clone the repository

```bash
git clone https://github.com/himaaanshuu/JALDRISTHI.git
cd JALDRISTHI
```

### 2. Set up the backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set up the frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### 4. Import data (optional — a fresh database is created on first run)

```bash
cd ../backend
python3 -m scripts.import_ingres_data
```

---

## Running the App

### Development mode (two terminals)

**Terminal 1 — Backend:**
```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

### Production mode (single server)

```bash
cd frontend && npm run build
cd ../backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

- App: http://localhost:8000 (serves both frontend and API)

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/blocks` | GET | All groundwater blocks with coordinates |
| `/api/states` | GET | State-level summary |
| `/api/data/categories` | GET | Category distribution |
| `/api/data/trend` | GET | Multi-year trend data |
| `/api/data/top-extraction` | GET | Top extraction blocks |
| `/api/data/coverage` | GET | Data coverage stats |
| `/api/data/sources` | GET | Data sources & provenance |
| `/api/risk/blocks` | GET | Risk scores for all blocks |
| `/api/data/search` | GET | Search groundwater data |
| `/api/data/export` | GET | Export as CSV |
| `/api/chat` | POST | AI chat with natural language queries |
| `/api/chat/parse` | POST | Parse intent without querying DB |

---

## Data Sources

| Source | Year | Records | Coverage |
|--------|------|---------|----------|
| GWRA-2024 (CGWB) | 2024 | 235 | 39 states, 221 districts |
| GWRA-2025 (CGWB) | 2025 | 241 | 39 states, 227 districts |
| State-level import | 2020 | 37 | All states |
| State-level import | 2022 | 37 | All states |

Data sourced from **OpenCity.in** CKAN Datastore API with full provenance tracking.

> **Note:** JAL-DRISHTI is a prototype. Official groundwater data should be verified against primary CGWB/IN-GRES sources for policy or operational decisions.

---

## Implementation Plan

### Phase 1: Foundation
- [x] Initialize FastAPI backend with SQLite + SQLAlchemy
- [x] Define data models (`GroundWater`, `DataSource`, `WaterReading`, `Evidence`)
- [x] Build core API endpoints (blocks, states, categories, health)
- [x] Set up React + Vite + TypeScript + Tailwind frontend scaffold

### Phase 2: Data Integration
- [x] Ingest official CGWB/IN-GRES data from OpenCity.in CKAN API
- [x] Import state-level data for 2020 and 2022 (37 states each)
- [x] Import district/block-level data for 2024 and 2025 (235 + 241 records)
- [x] Fix data quality issues: filter summary rows, correct TN/TG swap, normalize state names
- [x] Add `DataSource` model for full provenance tracking
- [x] Add coordinates to all 516 records for map display
- [x] Build data validation and quality reporting scripts

### Phase 3: Frontend — Dashboard & Map
- [x] Build sidebar navigation (OVERVIEW + INTELLIGENCE sections)
- [x] Create dashboard with category cards, trend chart, and top blocks table
- [x] Implement Leaflet interactive map with India bounds restriction
- [x] Add CartoDB dark basemap tiles and category-colored markers
- [x] Build state summary grid with extraction stage indicators
- [x] Add data source banner showing coverage years

### Phase 4: AI Chat Assistant & Intelligence
- [x] Build intent parser supporting English, Hindi, and Hinglish (9+ intents)
- [x] Implement 33 known states/UTs + 6 years (2020–2025) recognition
- [x] Build chat UI with Markdown rendering, evidence badges, risk scores
- [x] Add Hindi/Hinglish translations in chat responses
- [x] Implement intent handlers: status, compare, trend, risk, top blocks, category, help, search, export
- [x] Add source citations to all chat responses
- [x] Build AI-derived risk scoring (extraction stage + recharge deficit + multi-year trend)

### Phase 5: Analytics & Trend Features
- [x] Build multi-year trend endpoint with 4 data points (2020, 2022, 2024, 2025)
- [x] Create Recharts area chart (extraction, recharge, stage)
- [x] Add insight bar with extraction change % and stage direction
- [x] Filter trend data to state-level only for accurate cross-year comparison
- [x] Implement top extraction ranking (latest year default, no duplicates)
- [x] Build compare handler for year-over-year state comparison

### Phase 6: Design & Polish
- [x] Design "Deep Earth" geological dark theme with CSS variables
- [x] Add Instrument Serif (headings), DM Sans (body), JetBrains Mono (data) typography
- [x] Implement glassmorphism cards, grain texture overlay, glow shadows
- [x] Add staggered fadeInUp animations and pulse-glow effects
- [x] Restrict map to India bounds with maxBounds and viscosity
- [x] Update chat suggestions with Hindi queries and data source reference

### Phase 7: Search, Export & Deployment
- [x] Add search bar in dashboard header (navigates to AI Assistant)
- [x] Build CSV export endpoint with filtering
- [x] Add `/api/data/search` endpoint for full-text search
- [x] Add static file serving to FastAPI for production deployment
- [x] Write comprehensive README with clone instructions
- [ ] Deploy with ngrok or similar tunneling for shareable access

---

## Testing

```bash
cd backend
python3 -m pytest test_parser.py -v
```

---

## License

This project is for educational and research purposes.
