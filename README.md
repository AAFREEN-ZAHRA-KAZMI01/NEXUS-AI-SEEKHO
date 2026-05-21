# NEXUS AI — Autonomous Multi-Agent Intelligence System

> **AI Seekho Hackathon Submission** | Built by Aafreen Zahra Kazmi

Nexus AI converts any piece of business content — a news article, PDF, URL, CSV, or raw text — into autonomous operational decisions. A 6-agent AI pipeline powered by Google Gemini reads the input, maps its impact onto live domain KPIs, ranks the best response actions, and executes them against stateful Mock API endpoints — all without human intervention.

---

## Table of Contents

1. [What It Does](#1-what-it-does)
2. [Solution Design](#2-solution-design)
3. [Architecture Overview](#3-architecture-overview)
4. [Tech Stack](#4-tech-stack)
5. [AI Agents](#5-ai-agents)
6. [Content Parsers](#6-content-parsers)
7. [REST API Reference](#7-rest-api-reference)
8. [Mock APIs (Simulated Business Systems)](#8-mock-apis-simulated-business-systems)
9. [Database Models](#9-database-models)
10. [Frontend — Flutter App](#10-frontend--flutter-app)
11. [Web Frontend — Vanilla JS](#11-web-frontend--vanilla-js)
12. [Supported Domains](#12-supported-domains)
13. [End-to-End Data Flow](#13-end-to-end-data-flow)
14. [Setup & Installation](#14-setup--installation)
15. [Environment Variables](#15-environment-variables)
16. [Running Tests](#16-running-tests)
17. [Project Structure](#17-project-structure)

---

## 1. What It Does

| Step | What Happens |
|------|-------------|
| **Ingest** | Accepts raw text, URL, PDF, DOCX, CSV, or Excel as input |
| **Detect** | Auto-classifies input into one of 6 business domains |
| **Analyse** | 6 AI agents extract facts, score severity, map KPI impact, rank actions |
| **Execute** | Calls Mock API endpoints — updates pricing, CRM, hedging, dispatch systems |
| **Report** | Returns structured JSON with severity, insights, before/after state, and full agent trace |

**Example:** A news article about a LESCO power outage in Lahore → system detects "logistics" domain → scores severity 8/10 → recommends rerouting 3 warehouse zones → calls `POST /mock/logistics/routes/optimize` → returns delta: -12% delivery time, +7% cost efficiency.

---

## 2. Solution Design

### Design Philosophy

Nexus AI is designed around three core principles:

1. **Domain Intelligence First** — Each of the 6 domains has its own KPI catalog, action catalog, and Mock API endpoints tuned for Pakistan-specific business context (PKR, SBP, LESCO, WAPDA, KSE).
2. **Parallel + Sequential Agent Pipeline** — Agents that can run independently (Ingestion + Research) execute in parallel via `asyncio.gather`. Downstream agents (Analysis → Decision → Execution) run sequentially, each receiving merged artifacts from previous steps.
3. **Mock-First Architecture** — All business system integrations (ERP, CRM, hedging, procurement) are simulated via an in-memory stateful Mock API. This allows the full autonomous execution loop to run without real credentials, while the same `ExecutionAgent` interface can be pointed at real APIs by swapping base URLs.

### Key Design Decisions

- **Google Gemini 2.5 Flash** is used for all 6 agents — chosen for its large context window, speed, and cost efficiency for hackathon-scale workloads.
- **Fallback to mock responses** — if `GEMINI_API_KEY` is absent or invalid, every agent falls back to deterministic mock responses (`agents/mock_responses.py`) so the system remains fully functional for demos.
- **Async SQLAlchemy** — all DB operations are non-blocking, enabling the pipeline and API polling to coexist without deadlocking.
- **Two frontends** — a Flutter mobile/web app (`nexus_ai/`) for production quality, and a vanilla HTML/JS web app (`nexus_web/`) as a lightweight fallback that works in any browser with no build step.

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                       │
│  Flutter App (nexus_ai/)    Vanilla Web (nexus_web/)    │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (REST/JSON)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI BACKEND (newsops/)              │
│  ┌──────────────┐  ┌────────────┐  ┌────────────────┐  │
│  │ /api/analyse │  │/api/session│  │   /api/state   │  │
│  └──────┬───────┘  └────────────┘  └────────────────┘  │
│         ▼                                               │
│  ┌─────────────────────────────────────┐               │
│  │           PARSER LAYER              │               │
│  │  text / url / pdf / docx / csv /    │               │
│  │  excel — normalises to clean text   │               │
│  └──────────────────┬──────────────────┘               │
│                     ▼                                   │
│  ┌─────────────────────────────────────┐               │
│  │          ORCHESTRATOR               │               │
│  │  ┌─────────────┐ ┌───────────────┐  │               │
│  │  │IngestionAgent│ │ ResearchAgent │  │  ← parallel  │
│  │  └──────┬───────┘ └───────┬───────┘  │               │
│  │         └────────┬────────┘          │               │
│  │              ▼   ▼                   │               │
│  │        ┌──────────────┐              │               │
│  │        │ AnalysisAgent│              │  ← sequential│
│  │        └──────┬───────┘              │               │
│  │               ▼                      │               │
│  │        ┌──────────────┐              │               │
│  │        │ DecisionAgent│              │               │
│  │        └──────┬───────┘              │               │
│  │               ▼                      │               │
│  │        ┌──────────────┐              │               │
│  │        │merge_artifacts│             │               │
│  │        └──────┬───────┘              │               │
│  │               ▼                      │               │
│  │        ┌──────────────┐              │               │
│  │        │ExecutionAgent│              │               │
│  │        └──────┬───────┘              │               │
│  └───────────────┼─────────────────────┘               │
│                  ▼                                       │
│  ┌─────────────────────────────────────┐               │
│  │          MOCK API LAYER             │               │
│  │  logistics / business / finance /   │               │
│  │  policy / healthcare / urban        │               │
│  │  (30+ stateful in-memory endpoints) │               │
│  └─────────────────────────────────────┘               │
│                  ▼                                       │
│  ┌─────────────────────────────────────┐               │
│  │       SQLite / PostgreSQL DB        │               │
│  │  analysis_sessions · agent_artifacts│               │
│  │  state_logs                         │               │
│  └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
              Google Gemini 2.5 Flash API
```

> For the full architecture diagram with sequence flows and component interactions, see [NEXUS_AI_ARCHITECTURE.md](./NEXUS_AI_ARCHITECTURE.md).

---

## 4. Tech Stack

### Backend (`newsops/`)

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | FastAPI | 0.115 |
| ASGI Server | Uvicorn | latest |
| AI / LLM | Google Gemini 2.5 Flash | via `google-genai` |
| ORM | SQLAlchemy (async) | 2.0 |
| Database (dev) | SQLite via aiosqlite | — |
| Database (prod) | PostgreSQL via asyncpg | — |
| PDF Parsing | pdfplumber + pytesseract | — |
| Office Parsing | python-docx, pandas, openpyxl | — |
| URL Scraping | httpx + BeautifulSoup4 | — |
| Rate Limiting | slowapi | — |
| Containerisation | Docker + docker-compose | — |
| Testing | pytest + pytest-asyncio | — |

### Frontend — Flutter App (`nexus_ai/`)

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Flutter / Dart | 3.19+ / 3.3+ |
| State Management | Provider | 6.1.2 |
| HTTP Client | Dio | 5.4.3 |
| Fonts | google_fonts | — |
| Animations | flutter_animate, shimmer | — |
| File Picker | file_picker | — |
| Charts | percent_indicator | — |
| Platforms | Android, iOS, Web, Windows | — |

### Web Frontend (`nexus_web/`)

| Component | Technology |
|-----------|-----------|
| Markup | Vanilla HTML5 |
| Styling | Vanilla CSS3 (glassmorphic dark theme) |
| Logic | Vanilla JavaScript (ES6+) |
| State | localStorage-based shared state |
| HTTP | Custom `_fetch` wrapper (Dio-style) |

---

## 5. AI Agents

All agents are powered by **Google Gemini 2.5 Flash** and live in `newsops/agents/`.

### Agent Pipeline

```
Input → [IngestionAgent + ResearchAgent] (parallel)
              ↓ merged artifacts
        [AnalysisAgent] (sequential)
              ↓
        [DecisionAgent] (sequential)
              ↓
        [merge_artifacts] (pure Python)
              ↓
        [ExecutionAgent] (calls Mock API)
              ↓
        Structured AnalysisResponse JSON
```

### Agent Details

#### 1. Ingestion Agent (`ingestion_agent.py`)
- **Runs:** Parallel (step 1)
- **Duration:** ~3–5 seconds
- **Model:** gemini-2.5-flash
- **What it does:** Reads the cleaned input text and extracts:
  - Key facts and named entities
  - Business signals (supply disruptions, price changes, policy shifts, etc.)
  - Confidence score for each signal (0.0–1.0)
  - Domain auto-classification

#### 2. Research Agent (`research_agent.py`)
- **Runs:** Parallel (step 1, alongside Ingestion)
- **Duration:** ~3–5 seconds
- **Model:** gemini-2.5-flash
- **What it does:**
  - Cross-checks claims for credibility
  - Applies Pakistan-specific business context (PKR, SBP, LESCO, WAPDA, KSE, DRAP)
  - Flags contradictions or unverified claims
  - Produces a credibility score

#### 3. Analysis Agent (`analysis_agent.py`)
- **Runs:** Sequential (step 2), receives Ingestion + Research output
- **Duration:** ~4–6 seconds
- **Model:** gemini-2.5-flash
- **What it does:**
  - Maps extracted signals to domain-specific KPIs
  - Scores overall severity on a 1–10 scale
  - Quantifies estimated PKR financial impact
  - Lists top affected KPIs with before/after projections

#### 4. Decision Agent (`decision_agent.py`)
- **Runs:** Sequential (step 3)
- **Duration:** ~5–7 seconds
- **Model:** gemini-2.5-flash
- **What it does:**
  - Selects top-3 ranked actions from the domain action catalog
  - Assigns confidence score to each action
  - Builds the exact API payload for each action (endpoint + body)
  - Explains the rationale for the top recommendation

#### 5. Merge Artifacts (pure Python, no LLM call)
- **Runs:** Sequential (step 4)
- **Duration:** <1 second
- **What it does:** Merges all agent outputs into a single unified JSON structure keyed by `agent_name`

#### 6. Execution Agent (`execution_agent.py`)
- **Runs:** Sequential (step 5)
- **Duration:** ~2–4 seconds
- **What it does:**
  - Reads the `decision_agent` output for the top-ranked action
  - Captures `state_before` from Mock API state store
  - Makes the HTTP call to the target Mock API endpoint
  - Captures `state_after`
  - Computes delta between before/after
  - Saves state log to database

### Mock Fallback

Every agent has a corresponding entry in `agents/mock_responses.py` — deterministic JSON responses used when `GEMINI_API_KEY` is absent. This keeps the full pipeline functional for demos without an API key.

---

## 6. Content Parsers

All parsers live in `newsops/parsers/` and implement the same interface: receive raw bytes / string / URL → return `clean_text`.

| Parser | Input Types | Technology | Notes |
|--------|------------|-----------|-------|
| `text_parser.py` | `text`, `url` | httpx + BeautifulSoup | URL mode scrapes `<p>` tags |
| `pdf_parser.py` | `pdf` | pdfplumber + pytesseract OCR | Handles scanned PDFs via Tesseract |
| `docx_parser.py` | `docx` | python-docx | Extracts paragraphs + tables |
| `csv_parser.py` | `csv` | pandas | Generates descriptive summary + stats |
| `excel_parser.py` | `excel` | pandas + openpyxl | Multi-sheet text summaries |

`document_intelligence.py` (683 lines) acts as a smart router: it inspects the file MIME type and routes to the correct parser automatically.

---

## 7. REST API Reference

Base URL: `http://localhost:8000`

### Analysis Endpoints

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `POST` | `/api/analyse/text` | `{ "text": "...", "domain": "auto" }` | Analyse raw text |
| `POST` | `/api/analyse/url` | `{ "url": "https://...", "domain": "auto" }` | Scrape and analyse a URL |
| `POST` | `/api/analyse/file` | `multipart/form-data` (file + domain) | Upload and analyse a file |

**Response (all three):**
```json
{
  "session_id": "uuid",
  "domain": "logistics",
  "severity_score": 8,
  "key_insight": "LESCO outage will impact 3 Lahore warehouses...",
  "kpis_affected": [
    { "kpi": "delivery_time", "before": 4.2, "after": 6.1, "unit": "hours" }
  ],
  "top_action": {
    "action": "routes/optimize",
    "confidence": 0.91,
    "rationale": "...",
    "payload": { "zones": ["DHA", "Gulberg", "Johar"] }
  },
  "alternative_actions": [...],
  "state_before": {...},
  "state_after": {...},
  "delta": {...},
  "artifacts": { "ingestion": {...}, "research": {...}, ... },
  "duration_seconds": 18.4
}
```

### Session Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/session/{id}/status` | Pipeline status: `pending \| running \| complete \| failed` |
| `GET` | `/api/session/{id}/trace` | Full agent trace (all 6 artifact JSONs) |

### State Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/state/{domain}` | Read current Mock API state for a domain |
| `POST` | `/api/state/reset` | Reset all domain states to factory defaults |

### Health Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root health check |
| `GET` | `/health` | Detailed status with timestamp |

---

## 8. Mock APIs (Simulated Business Systems)

The Mock API layer lives in `newsops/mock_api/`. It simulates 6 real-world business domains with 30+ endpoints backed by an in-memory state store (`state_store.py`). State persists across requests within a single server session.

### Logistics Domain
| Endpoint | Action |
|----------|--------|
| `POST /mock/logistics/pricing/update` | Update route pricing |
| `POST /mock/logistics/routes/optimize` | Reroute delivery zones |
| `POST /mock/logistics/notifications/bulk_send` | Bulk SMS/email to drivers |
| `POST /mock/logistics/warehouse/reallocation` | Redistribute warehouse stock |

### Business / Commerce Domain
| Endpoint | Action |
|----------|--------|
| `POST /mock/business/crm/campaigns/create` | Launch targeted CRM campaign |
| `POST /mock/business/catalog/pricing/update` | Update product catalog prices |
| `POST /mock/business/crm/workflows/trigger` | Trigger CRM automation workflow |

### Finance Domain
| Endpoint | Action |
|----------|--------|
| `POST /mock/finance/hedging/book` | Book FX hedge position |
| `POST /mock/finance/portfolio/rebalance/flag` | Flag portfolio for rebalance |

### Policy / Regulatory Domain
| Endpoint | Action |
|----------|--------|
| `POST /mock/policy/compliance/alert` | Issue compliance alert |
| `POST /mock/policy/duty/adjust` | Adjust import/export duty rates |

### Healthcare Domain
| Endpoint | Action |
|----------|--------|
| `POST /mock/healthcare/procurement/emergency_order` | Trigger emergency medical supply order |
| `POST /mock/healthcare/notifications/clinical_alert` | Send clinical staff alert |

### Urban / Infrastructure Domain
| Endpoint | Action |
|----------|--------|
| `POST /mock/urban/operations/dispatch` | Dispatch field crew |
| `POST /mock/urban/communications/public_advisory` | Issue public advisory |

---

## 9. Database Models

Three async SQLAlchemy tables (`newsops/database/models.py`):

### `analysis_sessions`
```
id               UUID (PK)
created_at       DateTime
domain           String (logistics|business|finance|policy|healthcare|urban)
input_type       String (text|url|file)
input_preview    String (first 300 chars of input)
status           String (pending|running|complete|failed)
error_detail     String (nullable)
duration_seconds Float (nullable)
```

### `agent_artifacts`
```
id               UUID (PK)
session_id       UUID (FK → analysis_sessions.id)
agent_name       String (ingestion|research|analysis|decision|execution)
artifact_type    String
content          JSON (full agent output)
created_at       DateTime
duration_seconds Float
```

### `state_logs`
```
id               UUID (PK)
session_id       UUID (FK → analysis_sessions.id)
domain           String
state_before     JSON
state_after      JSON
action_taken     String
delta            JSON
created_at       DateTime
```

---

## 10. Frontend — Flutter App

**Location:** `nexus_ai/`  
**Entry point:** `nexus_ai/lib/main.dart`

### 13 Screens

| Route | Screen | Purpose |
|-------|--------|---------|
| `/splash` | SplashScreen | Logo animation, backend connectivity check |
| `/onboarding` | OnboardingScreen | 3-slide feature walkthrough (no API calls) |
| `/login` | LoginScreen | Mocked email/password login (demo mode) |
| `/home` | HomeScreen | Dashboard with recent analyses |
| `/analyze` | AnalyzeScreen | Input type selector, domain picker, content entry |
| `/progress` | AgentProgressScreen | Live agent step indicator, polls every 2s |
| `/insight` | InsightScreen | Severity score, key insight, KPI impact table |
| `/actions` | ActionsScreen | Top action + 2 alternatives with confidence scores |
| `/simulate` | SimulationScreen | Animated execution log showing Mock API calls |
| `/results` | ResultsScreen | Final success screen with projected outcomes |
| `/trace` | TraceScreen | Collapsible raw JSON for all 6 agent artifacts |
| `/workflow` | WorkflowScreen | Visual decision flow diagram |
| `/profile` | ProfileScreen | API endpoint config, state reset, user settings |

### State Management

State flows through a single `AnalysisProvider` (ChangeNotifier, `nexus_ai/lib/presentation/providers/analysis_provider.dart`):

| State Field | Type | Description |
|-------------|------|-------------|
| `inputType` | String | `text \| url \| file` |
| `domain` | String | `auto \| logistics \| business \| ...` |
| `content` | String | Raw input text or URL |
| `selectedFile` | File? | Picked file reference |
| `isLoading` | bool | Controls loading state across screens |
| `sessionId` | String? | UUID returned by `/api/analyse/*` |
| `result` | AnalysisResponse? | Full parsed response |
| `agentProgressStep` | int | 0–5, drives the progress screen UI |
| `liveLogs` | List\<String\> | Real-time log messages for progress screen |
| `pollingTimer` | Timer? | 2-second polling timer for session status |

**Key flow:** `runAnalysis()` → POST to API → sets `sessionId` → starts polling timer → timer calls `/api/session/{id}/status` every 2s → updates `agentProgressStep` → on `complete`, fetches full result → auto-navigates to InsightScreen.

### App Theme

Dark glassmorphic design (`nexus_ai/lib/core/theme/`):
- Base: `#0D0D0D` background, `#1A1A2E` card surfaces
- Accent: Cyan `#00F5FF` and deep purple gradients
- Typography: Google Fonts (Rajdhani for headings, Inter for body)

---

## 11. Web Frontend — Vanilla JS

**Location:** `nexus_web/`

A zero-dependency fallback web interface sharing the same dark glassmorphic visual design as the Flutter app. No build step required — open `index.html` in any modern browser.

| File | Purpose |
|------|---------|
| `index.html` | Login page with backend status indicator |
| `home.html` | Dashboard with recent analyses |
| `analyze.html` | Input type selector, content entry, domain picker |
| `progress.html` | Live agent progress with step animations |
| `insight.html` | Severity card, KPI impact grid, business impact |
| `trace.html` | Raw JSON agent artifact viewer |
| `profile.html` | Settings, API endpoint config |
| `js/api.js` | HTTP client with `_fetch` wrapper (Dio-style error handling) |
| `js/state.js` | localStorage-based shared state manager |
| `css/app.css` | Dark glassmorphic CSS (matches Flutter theme) |

---

## 12. Supported Domains

| Domain | Pakistan-Specific Context | Example KPIs |
|--------|--------------------------|--------------|
| **Logistics** | LESCO/WAPDA outages, carrier disruptions, Lahore/Karachi routes | delivery_time, fuel_cost, warehouse_utilization |
| **Business** | Consumer demand shifts, retail pricing, import disruptions | revenue, conversion_rate, inventory_turnover |
| **Finance** | PKR/USD rate, KSE-100, SBP policy, SECP regulations | fx_exposure, portfolio_risk, hedge_ratio |
| **Policy** | OGRA energy policy, SECP/SBP circulars, gazette notifications | compliance_score, duty_rate, regulatory_risk |
| **Healthcare** | DRAP drug approvals, WHO alerts, hospital supply chains | stockout_risk, procurement_lead_time, patient_capacity |
| **Urban** | WASA water, LESCO power, CDA development, traffic incidents | infrastructure_uptime, dispatch_response_time |

---

## 13. End-to-End Data Flow

```
1. User submits input (text / URL / file) + selects domain
        ↓
2. POST /api/analyse/{text|url|file}
        ↓
3. Parser layer normalises input to clean_text
        ↓
4. AnalysisSession saved to DB (status: pending)
        ↓
5. Orchestrator.run(clean_text, domain) kicks off:
        ↓
6. [PARALLEL] IngestionAgent + ResearchAgent both call Gemini 2.5 Flash
        ↓
7. Artifacts merged → AnalysisAgent → Gemini 2.5 Flash
        ↓
8. AnalysisAgent output → DecisionAgent → Gemini 2.5 Flash
        ↓
9. merge_artifacts() combines all outputs
        ↓
10. ExecutionAgent reads top_action payload
        ↓
11. Capture state_before from Mock API state store
        ↓
12. HTTP call to Mock API endpoint (e.g. POST /mock/logistics/routes/optimize)
        ↓
13. Capture state_after, compute delta
        ↓
14. Save AgentArtifacts + StateLog to DB
        ↓
15. Session status set to: complete
        ↓
16. Frontend polling /api/session/{id}/status detects "complete"
        ↓
17. Frontend fetches full AnalysisResponse
        ↓
18. Auto-navigate: Insight → Actions → Simulate → Results screens
```

**Total pipeline time:** ~18–25 seconds (parallel agents + 5 sequential Gemini calls)

---

## 14. Setup & Installation

### Prerequisites

- Python 3.11+
- Flutter 3.19+ / Dart 3.3+
- Docker + Docker Compose (optional)
- Tesseract OCR + Poppler (for PDF/OCR support)
- Google Gemini API key (from https://aistudio.google.com/)

### Backend — Local

```bash
cd newsops

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here

# Run database migrations
python -c "from database.db import init_db; import asyncio; asyncio.run(init_db())"

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### Backend — Docker

```bash
cd newsops

# Copy and configure environment
cp .env.example .env
# Edit .env — set GEMINI_API_KEY

# Build and start
docker-compose up --build

# Or run in background
docker-compose up -d
```

### Frontend — Flutter App

```bash
cd nexus_ai

# Install dependencies
flutter pub get

# Point to backend (edit lib/core/constants/api_constants.dart)
# Default: http://10.0.2.2:8000 (Android emulator)
# For web: http://localhost:8000

# Run on device / emulator
flutter run

# Build for web
flutter build web
```

### Web Frontend — Vanilla

```bash
cd nexus_web

# Open directly — no build required
# Just open index.html in any browser
# Or serve via any static server:
python -m http.server 3000
```

Update `BASE_URL` in `nexus_web/js/api.js` to point at your backend.

---

## 15. Environment Variables

All variables go in `newsops/.env` (copy from `.env.example`):

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google AI Studio API key |
| `DATABASE_URL` | No | SQLite (default) or PostgreSQL connection string |
| `SMTP_HOST` | No | SMTP server hostname |
| `SMTP_PORT` | No | SMTP port (default: 587) |
| `SMTP_USER` | No | SMTP username |
| `SMTP_PASSWORD` | No | SMTP password |

Without `GEMINI_API_KEY`, the system auto-falls back to mock responses for all agents.

---

## 16. Running Tests

```bash
cd newsops

# Install test dependencies
pip install -r requirements.txt

# Run full test suite
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run a specific test file
pytest tests/test_agents.py -v
pytest tests/test_pipeline.py -v
```

| Test File | What It Tests |
|-----------|--------------|
| `test_agents.py` | Agent orchestration, parallel execution, mock fallback |
| `test_parsers.py` | PDF, CSV, Excel, DOCX, URL parser output |
| `test_database.py` | ORM session creation, artifact saves, queries |
| `test_pipeline.py` | Full end-to-end pipeline run |
| `test_routers.py` | FastAPI route handlers, request validation |
| `test_mock_api.py` | Mock endpoint responses, state mutation |
| `test_helpers.py` | Domain detection, delta computation, UUID generation |
| `test_docker.py` | Docker image build validation |

---

## 17. Project Structure

```
AI-SEEKHO-HACKTHON/
├── README.md                        ← This file
├── NEXUS_AI_ARCHITECTURE.md         ← Detailed architecture reference
│
├── newsops/                         ← Python FastAPI Backend
│   ├── main.py                      ← App entry point, CORS, rate-limiting
│   ├── config.py                    ← Env vars, domain/model constants
│   ├── requirements.txt             ← 26 Python dependencies
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── agents/
│   │   ├── orchestrator.py          ← Pipeline runner (parallel + sequential)
│   │   ├── ingestion_agent.py       ← Fact extraction agent
│   │   ├── research_agent.py        ← Credibility verification agent
│   │   ├── analysis_agent.py        ← KPI impact scoring agent
│   │   ├── decision_agent.py        ← Action ranking agent
│   │   ├── execution_agent.py       ← Mock API executor agent
│   │   └── mock_responses.py        ← Fallback deterministic responses
│   ├── parsers/
│   │   ├── document_intelligence.py ← Smart MIME-type parser router
│   │   ├── text_parser.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── csv_parser.py
│   │   └── excel_parser.py
│   ├── routers/
│   │   ├── analysis.py              ← POST /api/analyse/*
│   │   ├── session.py               ← GET /api/session/*
│   │   └── state.py                 ← GET/POST /api/state/*
│   ├── pipelines/
│   │   └── pipeline.py              ← parse → save session → orchestrate
│   ├── mock_api/
│   │   ├── endpoints.py             ← 30+ Mock API route handlers
│   │   └── state_store.py           ← In-memory domain KPI state
│   ├── database/
│   │   ├── db.py                    ← Async SQLAlchemy engine + session
│   │   └── models.py                ← ORM models (3 tables)
│   ├── schemas/
│   │   ├── input_schemas.py         ← Pydantic request models
│   │   └── output_schemas.py        ← Pydantic response models
│   ├── utils/
│   │   ├── helpers.py               ← UUID, domain detection, delta compute
│   │   └── logger.py                ← Session-scoped structured logger
│   └── tests/
│       ├── conftest.py
│       ├── fixtures/
│       └── test_*.py (8 test files)
│
├── nexus_ai/                        ← Flutter Mobile/Web Frontend
│   ├── pubspec.yaml
│   ├── lib/
│   │   ├── main.dart                ← App entry, MultiProvider, routing
│   │   ├── core/
│   │   │   ├── constants/           ← API URLs, app constants
│   │   │   ├── theme/               ← Dark glassmorphic theme
│   │   │   └── utils/               ← Formatters, connectivity
│   │   ├── data/
│   │   │   ├── models/              ← DTOs for all API contracts
│   │   │   └── services/            ← Dio API client, file picker, auth
│   │   └── presentation/
│   │       ├── providers/           ← AnalysisProvider, AuthProvider
│   │       ├── screens/             ← 13 app screens
│   │       └── widgets/             ← Reusable UI components
│   └── android/ ios/ web/ windows/  ← Platform configs
│
└── nexus_web/                       ← Vanilla JS Web Frontend (fallback)
    ├── index.html
    ├── home.html
    ├── analyze.html
    ├── progress.html
    ├── insight.html
    ├── trace.html
    ├── profile.html
    ├── js/
    │   ├── api.js                   ← HTTP client wrapper
    │   └── state.js                 ← localStorage state manager
    └── css/
        └── app.css                  ← Dark glassmorphic styles
```

---

## Hackathon Submission

- **Event:** AI Seekho Hackathon
- **Team / Builder:** Aafreen Zahra Kazmi
- **Contact:** aafreenzk1214@gmail.com
- **GitHub:** [AAFREEN-ZAHRA-KAZMI01/NEXUS-AI-SEEKHO](https://github.com/AAFREEN-ZAHRA-KAZMI01/NEXUS-AI-SEEKHO)
