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

## Testing

```bash
cd backend
python3 -m pytest test_parser.py -v
```

---

## License

This project is for educational and research purposes.
