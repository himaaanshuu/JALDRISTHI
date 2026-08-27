# जलदृष्टि DRISTI

**Groundwater Intelligence Platform for India**

जलदृष्टि DRISTI is a comprehensive groundwater assessment and monitoring platform covering all 36 states and union territories of India. It integrates official CGWB/IN-GRES data with an AI-powered chat assistant "Jaladhi", interactive map, trend analytics, risk scoring, and a bilingual learning center — deployed on Supabase PostgreSQL.

---

## Features

- **Jaladhi AI Assistant** — Professional bilingual (English/Hindi) conversational assistant powered by Ollama LLM with hybrid RAG pipeline (TF-IDF retrieval + structured SQL data). Streaming responses, conversation memory, and 16 query types
- **Interactive Map** — Leaflet-based map with groundwater blocks color-coded by category (Safe, Semi-Critical, Critical, Over-Exploited), restricted to Indian boundaries
- **Trend Analytics** — Area chart showing extraction, recharge, and stage trends across assessment years
- **Risk Analysis** — AI-derived risk scores (0–100) for each state based on extraction stage, category distribution, historical trends, and risk concentration
- **Data Provenance** — Full source tracking with official data import, validation reports, and evidence citations
- **Groundwater Learning Center** — Bilingual educational content covering measurement units, extraction stage formulas, aquifer basics, and India usage breakdown
- **Bilingual Design** — Hindi + English typography with Noto Sans Devanagari, Inter, IBM Plex Mono, and Bebas Neue
- **State & District Coverage** — 912+ records across all 36 states/UTs, multiple assessment years
- **Supabase Backend** — PostgreSQL database hosted on Supabase with REST API, row-level security, and real-time capabilities

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite |
| Map | react-leaflet, Leaflet, CartoDB dark tiles |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | **Supabase PostgreSQL** (hosted) |
| Data Source | CGWB/IN-GRES via OpenCity.in CKAN API |
| AI/LLM | Ollama (llama3.1:8b), TF-IDF retrieval, hybrid RAG |
| Query Engine | Geo resolver, query router, numeric calculator |
| Display Font | Bebas Neue (editorial headlines) |
| Hindi Font | Noto Sans Devanagari (300–700) |
| English Font | Inter (300–800) |
| Data Font | IBM Plex Mono (400–600) |
| Env Config | python-dotenv |

---

## Architecture

```
jaldrishti/
├── backend/
│   ├── main.py                  # FastAPI app (36+ endpoints, streaming, CORS)
│   ├── database.py              # SQLAlchemy models (7 tables)
│   ├── config.py                # Centralized configuration
│   ├── smart_chat.py            # Hybrid SQL+RAG chat pipeline
│   ├── rag.py                   # RAG engine (TF-IDF + Ollama, 36+ knowledge docs)
│   ├── parser.py                # Intent parser (English/Hindi/Hinglish)
│   ├── geo_resolver.py          # Geographic entity resolution (36 states, 100+ districts)
│   ├── query_router.py          # Intent classification (16 query types)
│   ├── numeric_calc.py          # Backend calculations (comparisons, trends, rankings)
│   ├── ingestion.py             # Data ingestion framework (CGWB adapters)
│   ├── supabase_client.py       # Supabase REST API client
│   ├── requirements.txt         # Python dependencies
│   ├── test_comprehensive.py    # 108 automated tests (7 groups)
│   └── scripts/
│       ├── migrate_supabase.sql     # Supabase schema migration
│       ├── migrate_to_supabase.py   # SQLite → Supabase data migration
│       ├── import_ingres_data.py    # Data ingestion from OpenCity.in
│       └── validate_ingres_data.py  # Data quality validation
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # App shell with view routing
│   │   ├── App.css              # Design system (CSS variables, typography scale)
│   │   ├── components/
│   │   │   ├── Sidebar.tsx      # Bilingual navigation ("Jaladhi" / "जलाधि")
│   │   │   ├── Topbar.tsx       # Search input, year selector, AI button
│   │   │   ├── IndiaLeafletMap.tsx  # Leaflet interactive map
│   │   │   └── views/
│   │   │       ├── Overview.tsx     # Dashboard with KPI cards + map
│   │   │       ├── AIAssistant.tsx  # Jaladhi chat with streaming
│   │   │       ├── MapView.tsx      # Full-screen Leaflet map
│   │   │       ├── Analytics.tsx    # Trends and rankings
│   │   │       ├── Compare.tsx      # Year-over-year comparison
│   │   │       ├── Reports.tsx      # Report generation
│   │   │       ├── DataSources.tsx  # Data provenance
│   │   │       └── Learning.tsx     # Groundwater knowledge center
│   │   ├── data/states.ts       # State data types and coordinates
│   │   └── lib/api.ts           # API client (smart chat, streaming, groundwater data)
│   └── index.html               # Google Fonts
├── data/                        # SQLite database (fallback, gitignored)
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Template for environment setup
└── README.md
```

---

## Prerequisites

- **Python 3.10+** (tested with Python 3.14)
- **Node.js 18+** and npm
- **Git**
- **Ollama** (for AI chat) — https://ollama.ai
- **Supabase account** (free tier works) — https://supabase.com

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

### 3. Set up Supabase

1. Create a free account at https://supabase.com
2. Create a new project (any name, any region)
3. Go to **Settings → API** and copy:
   - **Project URL** (e.g., `https://your-project.supabase.co`)
   - **Anon/Publishable Key** (starts with `eyJ...`)
4. Go to **Settings → Database** and copy the **Database Password**
5. Go to **SQL Editor** and run the migration:

```sql
-- Paste the contents of backend/scripts/migrate_supabase.sql
-- Or run it directly from the file
```

6. Create your `.env` file:

```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

Your `.env` should look like:

```env
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

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_DB_PASSWORD=your-db-password-here
USE_SUPABASE=true
```

7. Migrate data from SQLite to Supabase:

```bash
cd backend
PYTHONPATH=. python3 scripts/migrate_to_supabase.py
```

### 4. Set up Ollama (for AI chat)

```bash
# Install Ollama
brew install ollama  # macOS
# Or download from https://ollama.ai

# Pull the model
ollama pull llama3.1:8b

# Start Ollama
ollama serve
# Or open /Applications/Ollama.app on macOS
```

### 5. Set up the frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Build for production
npm run build
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

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite fallback path | `sqlite:///data/jaldrishti.db` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `OLLAMA_BIN` | Path to Ollama binary | `/Applications/Ollama.app/Contents/Resources/ollama` |
| `LLM_MODEL` | Ollama model name | `llama3.1:8b` |
| `VITE_API_URL` | Backend API URL for frontend | `http://localhost:8000` |
| `SUPABASE_URL` | Supabase project URL | — |
| `SUPABASE_ANON_KEY` | Supabase anon/publishable key | — |
| `SUPABASE_DB_PASSWORD` | Supabase database password | — |
| `USE_SUPABASE` | Enable Supabase (true/false) | `false` |

---

## API Endpoints

### Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/dashboard/stats` | GET | Dashboard statistics |
| `/api/data/coverage` | GET | Data coverage stats |

### Groundwater Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/states` | GET | State-level summary |
| `/api/districts` | GET | District-level data |
| `/api/blocks` | GET | Block-level data with coordinates |
| `/api/assessments` | GET | Assessment records (filtered) |
| `/api/assessment/latest` | GET | Latest year assessments |
| `/api/assessment/history` | GET | Block assessment history |

### Analytics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analytics/category-distribution` | GET | Category distribution |
| `/api/analytics/top-extraction` | GET | Top extraction blocks |
| `/api/analytics/trend` | GET | Multi-year trend data |
| `/api/analytics/what-changed` | GET | Year-over-year changes |
| `/api/analytics/risk-score` | GET | AI-derived risk scores |

### AI Chat (Jaladhi)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/smart/chat` | POST | Smart chat (SQL + RAG hybrid) |
| `/api/smart/chat/stream` | POST | Streaming smart chat (SSE) |
| `/api/chat` | POST | Legacy chat endpoint |
| `/api/llm/chat` | POST | Direct LLM chat |
| `/api/llm/health` | GET | Check Ollama availability |

---

## Jaladhi AI Assistant

Jaladhi is the intelligent groundwater assistant built into the platform.

**Capabilities:**
- Natural language queries in English, Hindi, and Hinglish
- 16 query types: greeting, state_status, comparison, ranking, trend, category, district_status, block_status, quality, level, recommendation, regulatory, extraction, recharge, what_changed, general
- Geographic entity resolution for 36 states, 100+ districts, abbreviations, and Hindi names
- Backend calculations for comparisons, trends, and rankings (LLM never does arithmetic)
- Streaming responses via Server-Sent Events (SSE)
- Conversation memory for follow-up questions
- Professional structured output: Introduction → Key Findings → Conclusion

**Example queries:**
- "What is the groundwater status of Punjab?"
- "Compare Delhi and Karnataka"
- "Which states have the highest extraction?"
- "Show trends in groundwater extraction for Maharashtra"
- "राजस्थान की भूजल स्थिति बताओ" (Hindi)
- "पंजाब और हरियाणा की तुलना करो" (Hindi)

---

## Database Schema

### Supabase Tables

| Table | Records | Description |
|-------|---------|-------------|
| `groundwater` | 912 | Core assessment data (state, district, block, extraction, stage, category) |
| `data_sources` | 4 | Source tracking (CGWB, IN-GRES) |
| `water_readings` | 40 | Sensor/monitoring data |
| `groundwater_quality` | 0 | Quality parameters (fluoride, arsenic, nitrate, etc.) |
| `groundwater_levels` | 0 | Pre/post monsoon water levels |
| `conversation_history` | — | Chat session memory |
| `dataset_versions` | — | Data ingestion tracking |

### Indexes

- `ix_gw_state_year` — State + assessment year lookups
- `ix_gw_district_year` — District + year lookups
- `ix_gw_category_state` — Category + state filtering
- `ix_gw_state`, `ix_gw_district`, `ix_gw_block` — Individual column indexes

---

## Data Sources

| Source | Year | Records | Coverage |
|--------|------|---------|----------|
| GWRA-2024 (CGWB) | 2024 | 221 | 36 states, 221 districts |
| GWRA-2025 (CGWB) | 2025 | 227 | 36 states, 227 districts |
| State-level import | 2020 | 37 | All states |
| State-level import | 2022 | 37 | All states |
| District-level additions | 2020–2025 | 392 | 24 states, 285 districts |

**Total: 912 records** across 36 states, 285 districts, 192 blocks, 4 years.

Data sourced from **OpenCity.in** CKAN Datastore API with full provenance tracking.

> **Note:** जलदृष्टि DRISTI is a prototype. Official groundwater data should be verified against primary CGWB/IN-GRES sources for policy or operational decisions.

---

## Implementation Plan

### Completed Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Foundation | ✅ | FastAPI backend, SQLAlchemy models, React+Vite frontend |
| Phase 2: Data Integration | ✅ | CGWB/IN-GRES data ingestion, 912 records, provenance tracking |
| Phase 3: Dashboard & Map | ✅ | Leaflet map, KPI cards, state detail panels |
| Phase 4: AI Chat Assistant | ✅ | Intent parser, 9+ intents, Hindi/English/Hinglish |
| Phase 5: Analytics | ✅ | Multi-year trends, risk scoring, comparisons |
| Phase 6: Typography | ✅ | Bilingual design system, Bebas Neue, Noto Sans Devanagari |
| Phase 7: Learning Center | ✅ | Bilingual educational content, measurement units |
| Phase 8: Editorial Design | ✅ | Full-viewport hero, metadata labels |
| Phase 9: Deployment | ✅ | Static file serving, environment config |
| Phase 10: LLM Integration | ✅ | Ollama + RAG pipeline, 36+ knowledge docs |
| Phase 11: Jaladhi Rename | ✅ | Sidebar, topbar, chat header rebranded |
| Phase 12: Source Count Fix | ✅ | Improved retrieval, Hindi keyword mapping |
| Phase 13: Production Upgrade | ✅ | Geo resolver, query router, numeric calc, streaming |
| Phase 14: Supabase Migration | ✅ | PostgreSQL on Supabase, REST API client, data migration |

### Currently Working

| Feature | Status | Description |
|---------|--------|-------------|
| Jaladhi AI Assistant | ✅ Done | LLM-only mode, streaming, bilingual |
| Supabase Database | ✅ Done | 912 records on PostgreSQL |
| Interactive Map | ✅ Done | Leaflet with category-colored markers |
| Trend Analytics | ✅ Done | Multi-year extraction/recharge/stage charts |
| Risk Scoring | ✅ Done | AI-derived 0-100 risk scores per state |
| Learning Center | ✅ Done | Bilingual educational content |
| 108 Automated Tests | ✅ Done | Geo, router, calc, DB, SQL injection, hallucination |

### Upcoming Features

#### Phase 15: Water Quality & Levels
- [ ] Groundwater quality data integration (fluoride, arsenic, nitrate, iron, TDS)
- [ ] Pre/post monsoon water level tracking
- [ ] Quality heatmap overlays on map
- [ ] Contamination risk alerts

#### Phase 16: Advanced Analytics
- [ ] Predictive modeling — forecast extraction trends 5 years ahead
- [ ] Anomaly detection — flag unusual extraction spikes
- [ ] District-level heatmaps with drill-down
- [ ] Water budget calculator — input area, get recharge/extraction estimates
- [ ] Satellite data integration (NASA GRACE groundwater storage)

#### Phase 17: User Features
- [ ] User authentication (JWT-based via Supabase Auth)
- [ ] Saved queries and bookmarks
- [ ] Custom dashboards — pin favorite states/districts
- [ ] Alert system — email/SMS when extraction crosses threshold
- [ ] Compare tool — side-by-side state comparison

#### Phase 18: Data Expansion
- [ ] Real-time CGWB data sync (webhook/API polling)
- [ ] Rainfall data integration (IMD records)
- [ ] Crop water requirement data (CGWB crop coefficient tables)
- [ ] Borewell registration data (state-level)
- [ ] Extensible ingestion framework for new data sources

#### Phase 19: Mobile & Deployment
- [ ] Progressive Web App (PWA) with offline support
- [ ] React Native mobile app
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP)
- [ ] Public API for third-party integrations

---

## Testing

```bash
cd backend

# Run all 108 tests
python3 -m pytest test_comprehensive.py -v

# Run specific test groups
python3 -m pytest test_comprehensive.py -k "geo_resolution" -v
python3 -m pytest test_comprehensive.py -k "query_router" -v
python3 -m pytest test_comprehensive.py -k "numeric_calc" -v
python3 -m pytest test_comprehensive.py -k "database_queries" -v
python3 -m pytest test_comprehensive.py -k "sql_injection" -v
python3 -m pytest test_comprehensive.py -k "hallucination" -v
python3 -m pytest test_comprehensive.py -k "followup" -v

# Run parser tests
python3 -m pytest test_parser.py -v
```

---

## Forking & Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Set up Supabase (free tier) and Ollama locally
4. Make your changes
5. Run tests: `python3 -m pytest test_comprehensive.py -v`
6. Commit: `git commit -m "Add your feature"`
7. Push: `git push origin feature/your-feature`
8. Open a Pull Request

---

## License

This project is for educational and research purposes.
