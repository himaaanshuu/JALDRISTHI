# जलDRISTHI

**Groundwater Intelligence for a Sustainable India**

**जल संरक्षण • जल संवर्धन • जल समृद्धि**

जलDRISTHI is a comprehensive groundwater assessment and monitoring platform covering all 36 states and union territories of India. It integrates official CGWB/IN-GRES data with an AI-powered INGRES AI chatbot, interactive GeoJSON choropleth map, year-aware assessment timeline (2020–2026), CGWB classification criteria, trend analytics, risk scoring, water quality intelligence, and a bilingual learning center — deployed on Supabase PostgreSQL with Google OAuth and Mobile OTP authentication.

---

## Features

- **INGRES AI Chatbot** — Professional bilingual (English/Hindi) conversational assistant powered by Ollama LLM with hybrid RAG pipeline (TF-IDF retrieval + structured SQL data). Streaming responses, conversation memory, and 16 query types
- **Interactive GeoJSON Map** — Leaflet-based choropleth map with state boundaries color-coded by CGWB groundwater category (Safe, Semi-Critical, Critical, Over-Exploited). Supports state and district drill-down with tooltips showing state name (EN+HI), category, extraction stage, recharge, and extraction values
- **Authentication System** — Google OAuth and Mobile OTP login via Supabase Auth. JWT-based session management with role-based access control. Profile completion flow with glassmorphic login UI and cinematic water video background
- **Water Quality Intelligence** — BIS/CGWB drinking water quality standards (IS 10500:2012) with state and district-level assessment. Parameter-wise exceedance analysis with safe/moderate/exceeded breakdowns
- **CGWB Classification Criteria** — Complete documentation of Central Ground Water Board classification system with extraction stage thresholds, conditions, and management actions for each category
- **Year-Aware Assessment System (2020–2026)** — Dynamic assessment-year timeline with availability detection from Supabase. All map data, statistics, district details, and charts filter by selected year. Unavailable years shown dimmed with "Data unavailable" indicator
- **Year Comparison** — Compare any two assessment years for a state. Shows block-level changes, stage/extraction/recharge deltas, category improvements/deteriorations, and overall trend
- **Status History & Transitions** — Timeline of category transitions across available years with trend arrows (improved/deteriorated/unchanged)
- **Historical Trend Charts** — Multi-year trend visualization with gaps for missing years (no fabricated data)
- **Trend Analytics** — Dynamic charts showing category distribution, state rankings, regional analysis, and AI-powered insights
- **Risk Analysis** — AI-derived risk scores (0–100) for each state based on extraction stage, category distribution, historical trends, and risk concentration
- **Intelligence Reports** — Configurable report generation with state selection, section toggles, and dynamic preview based on CGWB classification
- **Data Provenance** — Full source tracking with official data import, validation reports, and evidence citations
- **Groundwater Learning Center** — Bilingual educational content covering CGWB classification criteria, measurement units, extraction stage formulas, aquifer basics, and India usage breakdown
- **Bilingual Design** — Hindi + English typography with Noto Sans Devanagari, Inter, IBM Plex Mono, and Instrument Serif
- **State & District Coverage** — 520+ records across all 36 states/UTs, multiple assessment years (2020–2025)
- **Supabase Backend** — PostgreSQL database hosted on Supabase with REST API, row-level security, and real-time capabilities

---

## CGWB Groundwater Classification

The Central Ground Water Board (CGWB) classifies assessment units based on the Stage of Groundwater Extraction (SGE):

| Category | SGE Range | Condition | Management Action |
|----------|-----------|-----------|-------------------|
| **Safe** | < 70% | Extraction within sustainable limits | Monitor and maintain |
| **Semi-Critical** | 70–90% | Approaching sustainable limits | Regulate new wells, promote efficiency |
| **Critical** | 90–100% | Nearly exceeded recharge | Ban new extraction, enforce pricing |
| **Over-Exploited** | ≥ 100% | More extracted than replenished | Emergency measures, alternative sources |

**Formula:** `SGE (%) = (Net Groundwater Extraction / Net Groundwater Availability) × 100`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite |
| Map | react-leaflet, Leaflet, GeoJSON choropleth, CartoDB dark tiles |
| GeoJSON Data | India state boundaries (35 features), district boundaries (594 features) |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | **Supabase PostgreSQL** (hosted) |
| Authentication | Supabase Auth — Google OAuth + Mobile OTP (SMS) |
| Data Source | CGWB National Compilation on Dynamic Ground Water Resources of India (2020, 2022, 2024, 2025) |
| AI/LLM | Ollama (llama3.1:8b), TF-IDF retrieval, hybrid RAG |
| Query Engine | Geo resolver, query router, numeric calculator |
| Display Font | Instrument Serif (branding & hero headings) |
| Hindi Font | Noto Sans Devanagari (300–700) |
| English Font | Inter (300–800) |
| Data Font | IBM Plex Mono (400–600) |
| Env Config | python-dotenv |

---

## Architecture

```
jaldrishti/
├── backend/
│   ├── main.py                  # FastAPI app (40+ endpoints, streaming, CORS)
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
│   ├── auth_middleware.py       # JWT verification, require_auth, require_admin
│   ├── auth_routes.py           # /api/auth/* endpoints (me, users, roles, verify)
│   ├── water_quality_routes.py  # /api/water-quality/* endpoints, BIS standards
│   ├── requirements.txt         # Python dependencies
│   ├── test_comprehensive.py    # 108 automated tests (7 groups)
│   └── scripts/
│       ├── migrate_supabase.sql     # Supabase schema migration
│       ├── migrate_to_supabase.py   # SQLite → Supabase data migration
│       ├── auth_migration.sql       # Profiles table + RLS + auto-create trigger
│       ├── import_ingres_data.py    # Data ingestion from CGWB publications
│       └── validate_ingres_data.py  # Data quality validation
├── frontend/
│   ├── public/
│   │   └── data/
│   │       ├── india_states.geojson      # India state boundaries (1.5MB, 35 features)
│   │       └── india_districts.geojson   # India district boundaries (2.8MB, 594 features)
│   ├── src/
│   │   ├── App.tsx              # App shell with view routing + auth
│   │   ├── App.css              # Design system (CSS variables, typography, map styles)
│   │   ├── Auth.css             # Glassmorphic auth pages with video background
│   │   ├── index.css            # Global reset, font imports
│   │   ├── styles/
│   │   │   ├── fonts.css        # Instrument Serif + Inter font imports
│   │   │   └── theme.css        # Fade-rise animation keyframes
│   │   ├── components/
│   │   │   ├── Sidebar.tsx      # Bilingual navigation with जलDRISTHI logo
│   │   │   ├── Topbar.tsx       # Search input, year selector, INGRES AI button
│   │   │   ├── IndiaLeafletMap.tsx  # Leaflet + GeoJSON choropleth map
│   │   │   └── auth/
│   │   │       ├── AuthContext.tsx       # Session management, profile state
│   │   │       ├── AuthCallback.tsx      # OAuth redirect handler
│   │   │       ├── LoginPage.tsx         # Google + OTP login with video bg
│   │   │       ├── ProfileCompletePage.tsx  # Post-login profile collection
│   │   │       ├── ProfilePage.tsx       # Edit profile with video bg
│   │   │       └── ProtectedRoute.tsx    # Auth gating with profile check
│   │   │   └── views/
│   │   │       ├── Overview.tsx     # Dashboard with KPI cards + map + video bg
│   │   │       ├── AIAssistant.tsx  # INGRES AI chat with streaming
│   │   │       ├── MapView.tsx      # Full intelligence map (modes, year timeline, panels)
│   │   │       ├── Analytics.tsx    # Dynamic analytics with rankings and insights
│   │   │       ├── Compare.tsx      # Year-over-year comparison with state selection
│   │   │       ├── Reports.tsx      # Configurable report generation
│   │   │       ├── DataSources.tsx  # Data provenance
│   │   │       ├── Learning.tsx     # CGWB classification + groundwater knowledge center
│   │   │       └── WaterQuality.tsx # BIS water quality standards & assessment
│   │   ├── data/
│   │   │   ├── stateMap.ts      # GeoJSON↔DB name mapping, status colors, color scales
│   │   │   └── states.ts       # Simplified state overview data for the SVG map
│   │   └── lib/
│   │       ├── api.ts           # API client (chat, streaming, groundwater, year-aware endpoints)
│   │       └── supabase.ts      # Supabase client with auth persistence config
│   └── index.html               # Google Fonts, dark first-paint background
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

### 3. Set up Supabase (Database)

Supabase hosts the PostgreSQL database for all groundwater data. The free tier is sufficient.

#### Step 3.1 — Create a Supabase Account

1. Go to **https://supabase.com** and sign up (GitHub login is fastest)
2. Verify your email if prompted

#### Step 3.2 — Create a New Project

1. Click **"New project"** on the dashboard
2. Fill in:
   - **Organization**: Select your org (or create one)
   - **Project name**: `jaldrishti` (or anything you like)
   - **Database password**: Choose a strong password — **save this somewhere**, you'll need it later
   - **Region**: Choose the closest to you (e.g., `Mumbai` for India)
3. Click **"Create new project"** and wait ~2 minutes for it to spin up

#### Step 3.3 — Get Your API Credentials

Once the project is ready:

1. Go to **Settings** (gear icon, bottom-left) → **API**
2. Copy these two values:

| Credential | Where to find it | Example |
|-----------|-----------------|---------|
| **Project URL** | Settings → API → Project URL | `https://abc123xyz.supabase.co` |
| **Anon Key** | Settings → API → `anon` `public` key | `eyJhbGciOiJIUzI1NiIs...` (starts with `eyJ`) |

3. Go to **Settings** → **Database** → **Connection string** → **URI**
4. Copy the **password** from the connection string (the part after `:` and before `@`)

> **Tip:** The URI looks like: `postgresql://postgres.[project-ref]:YOUR_PASSWORD@aws-0-...pooler.supabase.com:6543/postgres`
> You only need the **password** portion.

#### Step 3.4 — Create Database Tables

1. In the Supabase dashboard, click **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Open the file `backend/scripts/migrate_supabase.sql` from this repo and paste its **entire contents** into the editor
4. Click **"Run"** (or press `Ctrl+Enter` / `Cmd+Enter`)
5. You should see: `Success. No rows returned`

This creates 7 tables: `groundwater`, `data_sources`, `water_readings`, `groundwater_quality`, `groundwater_levels`, `conversation_history`, `dataset_versions` — plus indexes and row-level security policies.

> **Verify:** Go to **Table Editor** (left sidebar) and you should see all 7 tables listed.

#### Step 3.5 — Configure Authentication

Run the auth migration in Supabase SQL Editor:

1. Open `backend/scripts/auth_migration.sql` and paste into SQL Editor
2. Click **"Run"**

This creates the `profiles` table with RLS policies and auto-create trigger.

Then configure auth providers in Supabase Dashboard → **Authentication** → **Providers**:

1. **Google OAuth**: Enable, add your Google Client ID and Secret
   - Callback URL: `https://<your-project>.supabase.co/auth/v1/callback`
2. **Phone (SMS)**: Enable, configure your SMS provider (Twilio, etc.)

Set the JWT secret in Supabase Dashboard → **Settings** → **API** → **JWT Secret**.

#### Step 3.6 — Configure Environment Variables

1. From the project root, copy the example env file:

```bash
cp .env.example .env
```

2. Open `.env` and fill in your Supabase credentials:

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

# Supabase — FILL IN YOUR VALUES
SUPABASE_URL=https://abc123xyz.supabase.co          # Your Project URL
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...           # Your Anon Key
SUPABASE_DB_PASSWORD=your-strong-password-here       # Your DB Password
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIs...   # Your Service Role Key
SUPABASE_JWT_SECRET=your-jwt-secret-here             # Your JWT Secret
USE_SUPABASE=true
```

3. Also create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://abc123xyz.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

> **Important:** Never commit `.env` files to git. They're already in `.gitignore`.

#### Step 3.7 — Migrate Data to Supabase

Run the migration script to transfer groundwater records from the local SQLite database to Supabase:

```bash
cd backend
PYTHONPATH=. python3 scripts/migrate_to_supabase.py
```

Expected output:
```
============================================================
JAL-DRISHTI: SQLite → Supabase Migration
============================================================
Supabase connection: OK

  Migrating data_sources: 4 rows...
    [4/4] inserted
  [DONE] data_sources: 4/4 rows migrated

  Migrating groundwater: 522 rows...
    [50/522] inserted
    ...
    [522/522] inserted
  [DONE] groundwater: 522/522 rows migrated

  Migrating water_readings: 40 rows...
    [40/40] inserted
  [DONE] water_readings: 40/40 rows migrated

Migration complete! Total rows: 566
```

#### Step 3.8 — Verify the Migration

```bash
PYTHONPATH=. python3 -c "
import sys; sys.path.insert(0, '.')
from dotenv import load_dotenv; load_dotenv('../.env')
from supabase_client import sb_count

print(f'Groundwater: {sb_count(\"groundwater\")} rows')
print(f'Data Sources: {sb_count(\"data_sources\")} rows')
print(f'Water Readings: {sb_count(\"water_readings\")} rows')
"
```

Expected: `Groundwater: 520 rows`

#### Supabase Troubleshooting

| Problem | Solution |
|---------|----------|
| `Invalid API key` | Check `SUPABASE_ANON_KEY` in `.env` — must start with `eyJ` |
| `relation "groundwater" does not exist` | Run the SQL migration in Step 3.4 |
| `password authentication failed` | Check `SUPABASE_DB_PASSWORD` in `.env` |
| `Could not find the table in the schema cache` | Wait 30 seconds after running SQL, then try again (schema cache refresh) |
| Migration script hangs | Check your internet connection, Supabase may be temporarily slow |
| `ModuleNotFoundError: No module named 'supabase'` | Run `pip install supabase` in your virtual environment |
| Infinite recursion in RLS | Replace self-referencing admin policies with `auth.role() = 'service_role'` |

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
- Login page: http://localhost:5173 (redirects if not authenticated)

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
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (admin ops) | — |
| `SUPABASE_JWT_SECRET` | JWT secret for token verification | — |
| `USE_SUPABASE` | Enable Supabase (true/false) | `false` |

---

## API Endpoints

### Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/dashboard/stats` | GET | Dashboard statistics |
| `/api/data/coverage` | GET | Data coverage stats |

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/me` | GET | Get current user profile |
| `/api/auth/users` | GET | List all users (admin) |
| `/api/auth/users/{id}/role` | PUT | Update user role (admin) |
| `/api/auth/verify` | POST | Verify JWT token |

### Groundwater Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/states` | GET | State-level summary |
| `/api/districts` | GET | District-level data |
| `/api/blocks` | GET | Block-level data with coordinates |
| `/api/assessments` | GET | Assessment records (filtered by state/year/category) |
| `/api/assessment/latest` | GET | Latest year assessments |
| `/api/assessment/history` | GET | Block assessment history |
| `/api/groundwater/state/{state}` | GET | Comprehensive state groundwater data |
| `/api/groundwater/district/{state}` | GET | District data for a state |
| `/api/groundwater/block/{state}` | GET | Block data for a state |
| `/api/groundwater/overview` | GET | National overview (all years) |

### Year-Aware Assessment
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/groundwater/assessment-years` | GET | Available assessment years (2020–2026) with availability status |
| `/api/groundwater/overview-year?year=` | GET | Year-specific national overview |
| `/api/groundwater/year-compare?state=&year1=&year2=` | GET | YoY comparison with block-level changes |
| `/api/groundwater/status-transitions?state=` | GET | Category transitions across years |

### Water Quality
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/water-quality/standards` | GET | BIS/CGWB drinking water standards (IS 10500:2012) |
| `/api/water-quality/state/{state}` | GET | State-level water quality assessment |
| `/api/water-quality/district/{state}/{district}` | GET | District-level water quality |
| `/api/water-quality/overall` | GET | Overall water quality summary |
| `/api/water-quality/ingest` | POST | Ingest water quality data |

### Analytics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analytics/category-distribution` | GET | Category distribution |
| `/api/analytics/top-extraction` | GET | Top extraction blocks |
| `/api/analytics/trend` | GET | Multi-year trend data |
| `/api/analytics/what-changed` | GET | Year-over-year changes |
| `/api/analytics/risk-score` | GET | AI-derived risk scores |
| `/api/groundwater/rankings` | GET | State rankings by extraction stage |
| `/api/groundwater/trends/{state}` | GET | Multi-year trend for a state |
| `/api/groundwater/over-exploited` | GET | Over-exploited blocks list |

### AI Chat (INGRES AI)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/smart/chat` | POST | Smart chat (SQL + RAG hybrid) |
| `/api/smart/chat/stream` | POST | Streaming smart chat (SSE) |
| `/api/chat` | POST | Legacy chat endpoint |
| `/api/llm/chat` | POST | Direct LLM chat |
| `/api/llm/health` | GET | Check Ollama availability |

---

## INGRES AI Assistant

INGRES AI is the intelligent groundwater assistant built into the जलDRISTHI platform.

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
| `groundwater` | 520 | Core assessment data (state, district, block, extraction, stage, category) — sourced from CGWB |
| `data_sources` | 4 | CGWB National Compilation publications (2020, 2022, 2024, 2025) |
| `water_readings` | 40 | Sensor/monitoring data |
| `profiles` | — | User profiles (auto-created on signup via trigger) |
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

**Total: 520 records** across 36 states, sourced directly from CGWB publications.

**Available assessment years:** 2020, 2022, 2024, 2025 (2021, 2023, 2026 not yet published by CGWB)

Data sourced from **Central Ground Water Board (CGWB)**, Ministry of Jal Shakti — National Compilation on Dynamic Ground Water Resources of India, with full provenance tracking.

---

## Implementation Plan

### Completed Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Foundation | ✅ | FastAPI backend, SQLAlchemy models, React+Vite frontend |
| Phase 2: Data Integration | ✅ | CGWB data ingestion, 520 records from official publications, provenance tracking |
| Phase 3: Dashboard & Map | ✅ | Leaflet map, KPI cards, state detail panels |
| Phase 4: AI Chat Assistant | ✅ | Intent parser, 9+ intents, Hindi/English/Hinglish |
| Phase 5: Analytics | ✅ | Multi-year trends, risk scoring, comparisons |
| Phase 6: Typography | ✅ | Bilingual design system, Instrument Serif, Noto Sans Devanagari |
| Phase 7: Learning Center | ✅ | Bilingual educational content, measurement units |
| Phase 8: Editorial Design | ✅ | Full-viewport hero, metadata labels |
| Phase 9: Deployment | ✅ | Static file serving, environment config |
| Phase 10: LLM Integration | ✅ | Ollama + RAG pipeline, 36+ knowledge docs |
| Phase 11: INGRES AI Rename | ✅ | Sidebar, topbar, chat header rebranded |
| Phase 12: Source Count Fix | ✅ | Improved retrieval, Hindi keyword mapping |
| Phase 13: Production Upgrade | ✅ | Geo resolver, query router, numeric calc, streaming |
| Phase 14: Supabase Migration | ✅ | PostgreSQL on Supabase, REST API client, data migration |
| Phase 15: GeoJSON Choropleth Map | ✅ | Leaflet + GeoJSON state/district boundaries, color-coded by category |
| Phase 16: Year-Aware Assessment | ✅ | 2020–2026 timeline, availability detection, year-specific filtering |
| Phase 17: Year Comparison | ✅ | YoY block-level comparison, category transitions, status history |
| Phase 18: CGWB Classification | ✅ | Complete classification criteria with conditions and management actions |
| Phase 19: Enhanced Views | ✅ | Dynamic Analytics, Compare with state selection, configurable Reports |
| Phase 20: Authentication | ✅ | Google OAuth + Mobile OTP via Supabase Auth, JWT verification, role-based access |
| Phase 21: Water Quality | ✅ | BIS/CGWB drinking water standards, state & district assessment, exceedance analysis |

### Currently Working

| Feature | Status | Description |
|---------|--------|-------------|
| INGRES AI Chatbot | ✅ Done | LLM-only mode, streaming, bilingual |
| Authentication | ✅ Done | Google OAuth + Mobile OTP, glassmorphic UI with video bg |
| Supabase Database | ✅ Done | 520 CGWB records on PostgreSQL |
| GeoJSON Choropleth Map | ✅ Done | State + district boundaries, 35 states, 594 districts |
| Year-Aware Timeline | ✅ Done | 2020–2026 with availability detection |
| Year Comparison | ✅ Done | Block-level YoY comparison |
| Status Transitions | ✅ Done | Category transition history across years |
| CGWB Classification | ✅ Done | Complete criteria documentation |
| Trend Analytics | ✅ Done | Multi-year extraction/recharge/stage charts |
| Risk Scoring | ✅ Done | AI-derived 0-100 risk scores per state |
| Intelligence Reports | ✅ Done | Configurable report generation |
| Water Quality | ✅ Done | BIS standards, state/district assessment |
| Learning Center | ✅ Done | CGWB criteria + bilingual educational content |
| 108 Automated Tests | ✅ Done | Geo, router, calc, DB, SQL injection, hallucination |

### Upcoming Features

#### Phase 22: Advanced Analytics
- [ ] Predictive modeling — forecast extraction trends 5 years ahead
- [ ] Anomaly detection — flag unusual extraction spikes
- [ ] District-level heatmaps with drill-down
- [ ] Water budget calculator — input area, get recharge/extraction estimates
- [ ] Satellite data integration (NASA GRACE groundwater storage)

#### Phase 23: Data Expansion
- [ ] Real-time CGWB data sync (webhook/API polling)
- [ ] Rainfall data integration (IMD records)
- [ ] Crop water requirement data (CGWB crop coefficient tables)
- [ ] Borewell registration data (state-level)

#### Phase 24: Mobile & Deployment
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
