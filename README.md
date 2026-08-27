# जलदृष्टि DRISTI

**Groundwater Intelligence Platform for India**

जलदृष्टि DRISTI is a comprehensive groundwater assessment and monitoring platform covering all 36 states and union territories of India. It integrates official CGWB/IN-GRES data with a fully functional AI chat assistant, interactive map, trend analytics, risk scoring, and a bilingual learning center — all in a single deployable application.

---

## Features

- **Interactive Map** — Leaflet-based map with 192+ groundwater blocks color-coded by category (Safe, Semi-Critical, Critical, Over-Exploited), restricted to Indian boundaries
- **AI Chat Assistant** — Fully functional chat with natural language queries in English, Hindi, and Hinglish. 9+ intent types: status, compare, risk, top blocks, trend, category, greeting, search, export. Evidence citations and suggested follow-ups in every response
- **Trend Analytics** — Area chart showing extraction, recharge, and stage trends across 4 assessment years (2020, 2022, 2024, 2025)
- **Risk Analysis** — AI-derived risk scores for each block based on extraction stage, recharge deficit, and multi-year trends
- **Data Provenance** — Full source tracking with official data import, validation reports, and evidence citations
- **Groundwater Learning Center** — Bilingual (English + Hindi) educational section covering measurement units (BCM, MCM, ham, m³), extraction stage formulas, core concepts, aquifer basics, and India usage breakdown
- **Bilingual Design** — Hindi + English typography with Noto Sans Devanagari, Inter, IBM Plex Mono, and Bebas Neue (display)
- **State & District Coverage** — 914 total records (522 official + 392 district-level) across all 36 states/UTs, 4 assessment years, 8 categories
- **Editorial Hero Design** — Dramatic full-viewport typography with metadata labels, inspired by premium editorial layouts

---

## Architecture

```
jaldrishti/
├── backend/
│   ├── main.py                  # FastAPI application (21+ endpoints)
│   ├── database.py              # SQLAlchemy models (GroundWater, DataSource, Evidence)
│   ├── parser.py                # Intent parser (English/Hindi/Hinglish)
│   ├── requirements.txt         # Python dependencies
│   ├── test_parser.py           # 42 unit tests for parser
│   └── scripts/
│       ├── import_ingres_data.py    # Data ingestion from OpenCity.in
│       └── validate_ingres_data.py  # Data quality validation
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # App shell with view routing
│   │   ├── App.css              # Design system (CSS variables, typography scale, spacing)
│   │   ├── components/
│   │   │   ├── Sidebar.tsx      # Bilingual navigation (English + Hindi)
│   │   │   ├── Topbar.tsx       # Search input, year selector, AI button
│   │   │   ├── IndiaLeafletMap.tsx  # Leaflet interactive map (react-leaflet)
│   │   │   ├── IndiaMap.tsx     # SVG India map (alternate)
│   │   │   └── views/
│   │   │       ├── Overview.tsx     # Dashboard with KPI cards + map + editorial hero
│   │   │       ├── AIAssistant.tsx  # Fully functional chat interface
│   │   │       ├── MapView.tsx      # Full-screen Leaflet map
│   │   │       ├── Analytics.tsx    # Trends and rankings
│   │   │       ├── Compare.tsx      # Year-over-year comparison
│   │   │       ├── Reports.tsx      # Report generation
│   │   │       ├── DataSources.tsx  # Data provenance
│   │   │       └── Learning.tsx     # Groundwater knowledge center (bilingual)
│   │   ├── data/states.ts       # State data types and coordinates
│   │   └── lib/api.ts           # API client (fetchJson, sendChatMessage)
│   └── index.html               # Google Fonts (Bebas Neue, Noto Sans Devanagari, Inter, IBM Plex Mono)
├── data/                        # SQLite database (gitignored)
├── .env                         # Environment variables (gitignored)
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite |
| Map | react-leaflet, Leaflet, CartoDB dark tiles |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite |
| Data Source | CGWB/IN-GRES via OpenCity.in CKAN API |
| Display Font | Bebas Neue (editorial headlines) |
| Hindi Font | Noto Sans Devanari (300–700) |
| English Font | Inter (300–800) |
| Data Font | IBM Plex Mono (400–600) |
| Env Config | python-dotenv |

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

## Environment Variables

Copy `.env` or create your own:

```bash
# Backend
DATABASE_URL=sqlite:///data/jaldrishti.db
CORS_ORIGINS=http://localhost:5173,http://localhost:8000
HOST=0.0.0.0
PORT=8000
DEBUG=true

# LLM (Ollama)
OLLAMA_BIN=/Applications/Ollama.app/Contents/Resources/ollama
LLM_MODEL=llama3.1:8b

# Frontend
VITE_API_URL=http://localhost:8000
```

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
| `/api/data/coverage` | GET | Data coverage stats (records, recharge, extraction, stage) |
| `/api/data/sources` | GET | Data sources & provenance |
| `/api/risk/blocks` | GET | Risk scores for all blocks |
| `/api/data/search` | GET | Search groundwater data |
| `/api/data/export` | GET | Export as CSV |
| `/api/chat` | POST | AI chat with natural language queries |
| `/api/chat/parse` | POST | Parse intent without querying DB |
| `/api/llm/chat` | POST | LLM-powered chat (Ollama RAG) |
| `/api/llm/health` | GET | Check Ollama availability |
| `/api/llm/rebuild` | POST | Rebuild RAG knowledge base |

---

## LLM Integration (Ollama)

जलदृष्टि DRISTI includes a local LLM integration powered by Ollama for conversational groundwater intelligence.

**Setup:**
1. Install Ollama from https://ollama.ai
2. Pull the model: `ollama pull llama3.1:8b`
3. Start Ollama: `open /Applications/Ollama.app`
4. The backend automatically connects to Ollama at `localhost:11434`

**Architecture:**
- **Retrieval**: TF-IDF vector search over 33+ knowledge documents (domain KB + database records)
- **Generation**: Ollama llama3.1:8b for response generation
- **Knowledge Base**: Covers aquifer types, extraction stages, CGWB categories, contamination issues, government policies, measurement units, and state-specific data
- **Database Integration**: Real-time queries to SQLite for state/district/block data

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/llm/chat` | POST | Chat with LLM (params: `message`, `top_k`) |
| `/api/llm/health` | GET | Check Ollama status and model availability |
| `/api/llm/rebuild` | POST | Rebuild knowledge base after DB updates |

**Frontend Mode Toggle:**
The AI Assistant includes a toggle between Rule-Based (fast, deterministic) and LLM (conversational, context-aware) modes.

---

## AI Chat (Rule-Based)

The AI assistant accepts natural language queries and returns structured responses with data, evidence, and follow-up suggestions.

**Supported intents:** greeting, status, compare, top_extraction, critical_areas, trend, category, location, what_changed

**Example queries:**
- "What is the groundwater status of Punjab?"
- "Compare Haryana between 2020 and 2024."
- "Which districts have the highest extraction?"
- "Show over-exploited areas in Rajasthan."
- "राजस्थान की भूजल स्थिति बताओ" (Hindi)

---

## Data Sources

| Source | Year | Records | Coverage |
|--------|------|---------|----------|
| GWRA-2024 (CGWB) | 2024 | 221 | 36 states, 221 districts |
| GWRA-2025 (CGWB) | 2025 | 227 | 36 states, 227 districts |
| State-level import | 2020 | 37 | All states |
| State-level import | 2022 | 37 | All states |
| District-level additions | 2020–2025 | 392 | 24 states, 285 districts |

**Total: 914 records** across 36 states, 285 districts, 192 blocks, 4 years.

Data sourced from **OpenCity.in** CKAN Datastore API with full provenance tracking.

> **Note:** जलदृष्टि DRISTI is a prototype. Official groundwater data should be verified against primary CGWB/IN-GRES sources for policy or operational decisions.

---

## Learning Center

The built-in **Groundwater Learning Center** (जलज्ञान) provides bilingual educational content:

- **Measurement Units** — BCM, MCM, ham, m³, % with conversions and usage context
- **Extraction Stage Formula** — `Stage (%) = (Extraction / Availability) × 100` with Safe/Semi-Critical/Critical/Over-Exploited ranges
- **Core Concepts** — Recharge, Extraction Stage, Safe Category, Over-Exploited, Annual Recharge, Extractable Resource — each with Hindi definitions and real-world examples
- **Aquifer Basics** — What is an aquifer, Water table, Declining water levels
- **India Usage** — Irrigation (63%), Domestic (18%), Industrial (19%) breakdown

All content is available in both English and Hindi (हिन्दी).

---

## Implementation Plan

### Phase 1: Foundation
- [x] Initialize FastAPI backend with SQLite + SQLAlchemy
- [x] Define data models (`GroundWater`, `DataSource`, `WaterReading`, `Evidence`)
- [x] Build core API endpoints (blocks, states, categories, health)
- [x] Set up React + Vite + TypeScript frontend scaffold

### Phase 2: Data Integration
- [x] Ingest official CGWB/IN-GRES data from OpenCity.in CKAN API
- [x] Import state-level data for 2020 and 2022 (37 states each)
- [x] Import district/block-level data for 2024 and 2025 (221 + 227 records)
- [x] Add 392 district-level records across 24 states
- [x] Fix data quality issues: filter summary rows, correct TN/TG swap, normalize state names
- [x] Add `DataSource` model for full provenance tracking
- [x] Add coordinates to 516 records for map display (192 blocks rendered)

### Phase 3: Frontend — Dashboard & Map
- [x] Build sidebar navigation with bilingual labels (English + Hindi)
- [x] Create dashboard with KPI cards (mono-font labels, colored accent bars)
- [x] Implement Leaflet interactive map with India bounds restriction
- [x] Add CartoDB dark basemap tiles and category-colored markers
- [x] Build state detail panel with extraction metrics and trend chart
- [x] Make logo clickable to navigate to overview

### Phase 4: AI Chat Assistant & Intelligence
- [x] Build intent parser supporting English, Hindi, and Hinglish (9+ intents)
- [x] Implement 33 known states/UTs + 6 years (2020–2025) recognition
- [x] Build chat UI with Markdown rendering, evidence badges, risk scores
- [x] Add Hindi/Hinglish translations in chat responses
- [x] Implement intent handlers: status, compare, trend, risk, top blocks, category, help, search, export
- [x] Add source citations to all chat responses
- [x] Build AI-derived risk scoring (extraction stage + recharge deficit + multi-year trend)
- [x] Wire up frontend to backend `/api/chat` endpoint with full state management
- [x] Add loading states, follow-up chips, suggested queries sidebar

### Phase 5: Analytics & Trend Features
- [x] Build multi-year trend endpoint with 4 data points (2020, 2022, 2024, 2025)
- [x] Create Recharts area chart (extraction, recharge, stage)
- [x] Add insight bar with extraction change % and stage direction
- [x] Filter trend data to state-level only for accurate cross-year comparison
- [x] Implement top extraction ranking (latest year default, no duplicates)
- [x] Build compare handler for year-over-year state comparison

### Phase 6: Typography & Visual Identity
- [x] Brand redesign: जलदृष्टि (Hindi) + DRISTI (English) + GROUNDWATER INTELLIGENCE
- [x] Import Bebas Neue (display), Noto Sans Devanagari (Hindi), Inter (English), IBM Plex Mono (data)
- [x] Build bilingual sidebar navigation with Hindi secondary labels
- [x] Add bilingual eyebrow prefixes to all view headers
- [x] Create CSS typography scale (--text-xs through --text-3xl)
- [x] Create CSS spacing scale (--sp-1 through --sp-10)
- [x] Apply consistent font-family across all components
- [x] Redesign KPI cards with mono labels, colored accent bars, improved typography

### Phase 7: Learning Center & Hindi Translations
- [x] Build Groundwater Learning view with measurement units (BCM, MCM, ham, m³, %)
- [x] Add extraction stage formula card with colored range boxes
- [x] Create core concept cards with Hindi definitions and real-world examples
- [x] Add aquifer basics section with Hindi translations
- [x] Add India usage breakdown (irrigation/domestic/industrial) with Hindi
- [x] Add Hindi translations throughout all learning content

### Phase 8: Editorial Design & Polish
- [x] Dramatic full-viewport hero typography (Bebas Neue, 110px)
- [x] Editorial metadata labels (States, Districts, Data Source, Records)
- [x] Hindi subtitle with opacity hierarchy
- [x] Responsive design for mobile (42px title, wrapping meta)

### Phase 9: Deployment
- [x] Add static file serving to FastAPI for production deployment
- [x] Add environment variable configuration with python-dotenv
- [x] Write comprehensive README with clone instructions
- [ ] Deploy with ngrok or similar tunneling for shareable access

### Phase 10: LLM Integration (Ollama)
- [x] Install Ollama + pull llama3.1:8b model
- [x] Create RAG pipeline with TF-IDF retrieval + Ollama generation
- [x] Build 33-document knowledge base (aquifers, contamination, policies, state data)
- [x] Add SQLite DB integration for real-time state/district/block queries
- [x] Add /api/llm/chat, /api/llm/health, /api/llm/rebuild endpoints
- [x] Frontend mode toggle (Rule-Based / LLM)
- [x] Language selector (English / Hindi) for pure language responses
- [x] Optimized for speed: HTTP API instead of subprocess, 2048 context

---

## Implementation Plan — What's Next

### Currently Working
| Feature | Status | Description |
|---------|--------|-------------|
| Interactive Map | ✅ Done | Leaflet map with 192 blocks, color-coded by category |
| Rule-Based AI Chat | ✅ Done | 9+ intents, Hindi/English/Hinglish, evidence citations |
| LLM AI Chat (Ollama) | ✅ Done | RAG pipeline, 33-doc knowledge base, pure Hindi/English |
| Trend Analytics | ✅ Done | Multi-year extraction/recharge/stage charts |
| Risk Scoring | ✅ Done | AI-derived 0-100 risk scores per state |
| Learning Center | ✅ Done | Bilingual educational content |
| Editorial Hero | ✅ Done | Bebas Neue typography, metadata bar |
| Data Coverage | ✅ Done | 914 records, 36 states, 285 districts |

### Phase 11: Enhanced LLM Features (In Progress)
- [ ] Streaming responses for real-time text display
- [ ] Conversation memory (multi-turn context)
- [ ] Auto-detect language from user input
- [ ] Voice input support (Web Speech API)
- [ ] Export chat history as PDF/Markdown

### Phase 12: Advanced Analytics
- [ ] Predictive modeling — forecast extraction trends 5 years ahead
- [ ] Anomaly detection — flag unusual extraction spikes
- [ ] District-level heatmaps with drill-down
- [ ] Water budget calculator — input area, get recharge/extraction estimates
- [ ] Satellite data integration (NASA GRACE groundwater storage)

### Phase 13: User Features
- [ ] User authentication (JWT-based)
- [ ] Saved queries and bookmarks
- [ ] Custom dashboards — pin favorite states/districts
- [ ] Alert system — email/SMS when extraction crosses threshold
- [ ] Compare tool — side-by-side state comparison

### Phase 14: Data Expansion
- [ ] Real-time CGWB data sync (webhook/API polling)
- [ ] Water quality data integration (fluoride, arsenic, nitrate levels)
- [ ] Rainfall data integration (IMD records)
- [ ] Crop water requirement data (CGWB crop coefficient tables)
- [ ] Borewell registration data (state-level)

### Phase 15: Mobile & Deployment
- [ ] Progressive Web App (PWA) with offline support
- [ ] React Native mobile app
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP)
- [ ] Public API for third-party integrations

---

## Testing

```bash
cd backend
python3 -m pytest test_parser.py -v
```

---

## License

This project is for educational and research purposes.
