# NEXUS AI — Autonomous Multi-Agent Intelligence System

Nexus AI is an end-to-end autonomous intelligence platform built for the **AI Seekho Hackathon**. It ingests any business content (news articles, PDFs, URLs, spreadsheets, raw text), runs it through a 6-agent AI pipeline powered by **Google Gemini**, and autonomously executes domain-specific business actions — from repricing logistics routes to booking FX hedges and dispatching repair crews.

The system consists of two parts:

| Layer | Stack | Location |
|---|---|---|
| **Backend** (NewsOps) | Python · FastAPI · Google Gemini · SQLAlchemy | `newsops/` |
| **Frontend** (Nexus AI) | Flutter · Dart · Provider | `nexus_ai/` |

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Backend — NewsOps](#3-backend--newsops)
   - [Folder Structure](#31-folder-structure)
   - [6 AI Agents](#32-6-ai-agents)
   - [Content Parsers](#33-content-parsers)
   - [REST API Endpoints](#34-rest-api-endpoints)
   - [Mock API (30+ Endpoints)](#35-mock-api-30-endpoints)
   - [Database Models](#36-database-models)
   - [Configuration & Environment Variables](#37-configuration--environment-variables)
4. [Frontend — Nexus AI](#4-frontend--nexus-ai)
   - [Folder Structure](#41-folder-structure)
   - [13 Screens](#42-13-screens)
   - [State Management](#43-state-management)
5. [End-to-End Data Flow](#5-end-to-end-data-flow)
6. [Supported Domains](#6-supported-domains)
7. [Installation & Setup](#7-installation--setup)
   - [Backend (Local)](#71-backend-local)
   - [Backend (Docker)](#72-backend-docker)
   - [Frontend (Flutter)](#73-frontend-flutter)
8. [API Usage Examples](#8-api-usage-examples)
9. [Running Tests](#9-running-tests)

---

## 1. Project Overview

### What Does It Do?

1. **Ingest** — accepts a news article, PDF report, CSV dataset, DOCX file, or any URL
2. **Detect** — automatically identifies which of 6 business domains the content belongs to (Logistics, Business, Finance, Policy, Healthcare, or Urban)
3. **Analyse** — a pipeline of 6 specialized AI agents extracts facts, verifies credibility, maps KPI impact, ranks actions, and executes the top action
4. **Act** — calls stateful Mock API endpoints that simulate real business systems (pricing engines, CRM platforms, hedging desks, procurement portals)
5. **Report** — returns a structured JSON response with severity score, insight, before/after state, delta, and a full agent trace

### Who Is It For?

Enterprises operating in Pakistan's logistics, finance, healthcare, or urban infrastructure sectors who need to convert real-time news signals into automated operational decisions.

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Flutter App (nexus_ai)                 │
│  Android · iOS · Web · Windows                           │
│  13 screens  ·  Provider state management  ·  Dio HTTP   │
└─────────────────────────┬────────────────────────────────┘
                          │  HTTP (JSON / multipart)
                          ▼
┌──────────────────────────────────────────────────────────┐
│                  FastAPI Server (:8000)                   │
│  POST /api/analyse/text   POST /api/analyse/url          │
│  POST /api/analyse/file   GET  /api/session/{id}/trace   │
│  GET  /api/state/{domain} POST /api/state/reset          │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│                     run_pipeline()                        │
│  Parsers: text | url | pdf | docx | csv | excel          │
│  → create AnalysisSession  →  Orchestrator.run()         │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│                  Orchestrator                 │
│  ┌────────────────┐  ┌─────────────────┐     │
│  │ IngestionAgent │  │  ResearchAgent  │  ── parallel
│  └───────┬────────┘  └────────┬────────┘     │
│          └──────────┬─────────┘              │
│                     ▼                        │
│           ┌──────────────────┐               │
│           │  AnalysisAgent   │  ── sequential│
│           └────────┬─────────┘               │
│                    ▼                         │
│           ┌──────────────────┐               │
│           │  DecisionAgent   │  ── sequential│
│           └────────┬─────────┘               │
│                    ▼                         │
│           ┌──────────────────┐               │
│           │ merge_artifacts  │  ── pure Python
│           └────────┬─────────┘               │
│                    ▼                         │
│           ┌──────────────────┐               │
│           │ ExecutionAgent   │  ── calls Mock API
│           └──────────────────┘               │
└──────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│            Mock API  (/api/*)                 │
│  Stateful in-memory stores for all 6 domains │
│  30+ action endpoints simulate real systems  │
└──────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│    PostgreSQL / SQLite  (async SQLAlchemy)    │
│  analysis_sessions · agent_artifacts         │
│  state_logs                                  │
└──────────────────────────────────────────────┘
```

---

## 3. Backend — NewsOps

### 3.1 Folder Structure

```
newsops/
├── main.py                  # FastAPI app, CORS, rate-limiting, router wiring, lifespan
├── config.py                # Gemini model names, domain keywords, severity labels, env vars
├── requirements.txt         # All Python dependencies
├── .env.example             # Environment variable template
├── Dockerfile               # Production container image (Python 3.11 slim)
├── docker-compose.yml       # Multi-container orchestration (API + PostgreSQL)
│
├── agents/                  # The 6 AI agents
│   ├── orchestrator.py      # Pipeline coordinator — runs all agents in correct order
│   ├── ingestion_agent.py   # Extracts facts, entities, numbers, confidence scores
│   ├── research_agent.py    # Verifies credibility, adds Pakistan business context
│   ├── analysis_agent.py    # Maps signals to domain KPIs, scores severity 1–10
│   ├── decision_agent.py    # Ranks top-3 actions from domain catalogues
│   └── execution_agent.py   # Calls Mock API, captures before/after state, logs
│
├── pipelines/
│   └── pipeline.py          # run_pipeline() — parse → save session → orchestrate
│
├── parsers/                 # File type handlers
│   ├── text_parser.py       # Raw text and URL content (BeautifulSoup scraper)
│   ├── pdf_parser.py        # PDF with Tesseract OCR for scanned documents
│   ├── docx_parser.py       # Microsoft Word documents
│   ├── csv_parser.py        # Comma-separated values
│   └── excel_parser.py      # .xlsx / .xls spreadsheets (pandas + openpyxl)
│
├── routers/                 # FastAPI route handlers
│   ├── analysis.py          # POST /api/analyse/{text|url|file}
│   ├── session.py           # GET /api/session/{id}/trace and /status
│   └── state.py             # GET /api/state/{domain}, POST /api/state/reset
│
├── mock_api/                # Simulated business systems
│   ├── state_store.py       # In-memory domain state (numeric values, mutated by actions)
│   └── endpoints.py         # 30+ stateful mock action endpoints
│
├── database/
│   ├── db.py                # Async SQLAlchemy engine, sessionmaker, get_db()
│   └── models.py            # ORM: AnalysisSession, AgentArtifact, StateLog
│
├── schemas/
│   ├── input_schemas.py     # TextAnalysisRequest, UrlAnalysisRequest, FileAnalysisRequest
│   └── output_schemas.py    # AnalysisResponse, TraceResponse, and sub-models
│
└── utils/
    ├── helpers.py           # generate_uuid(), detect_domain(), compute_delta(), retry()
    └── logger.py            # SessionLogger — structured JSON logging to stdout
```

### 3.2 Six AI Agents

Each agent is a self-contained class that calls Google Gemini with a domain-specific prompt and returns a structured artifact saved to the database.

| Agent | Gemini Model | Runs | What It Does |
|---|---|---|---|
| **Orchestrator** | gemini-1.5-pro | Wraps all | Coordinates pipeline, detects domain, merges outputs, saves artifacts |
| **IngestionAgent** | gemini-1.5-flash | Parallel (step 1) | Extracts facts, named entities, numeric signals, confidence score |
| **ResearchAgent** | gemini-1.5-flash | Parallel (step 1) | Verifies source credibility, adds Pakistan-specific business context, flags contradictions |
| **AnalysisAgent** | gemini-1.5-flash | Sequential (step 2) | Maps extracted signals to domain KPIs, scores severity 1–10, quantifies PKR financial impact |
| **DecisionAgent** | gemini-1.5-pro | Sequential (step 3) | Selects top-3 ranked actions from a domain-specific catalogue, builds complete API payloads |
| **ExecutionAgent** | — (no LLM) | Sequential (step 4) | Reads state_before, calls Mock API, reads state_after, computes delta, logs notifications |

**Execution order:**

```
Ingestion ──┐
             ├── (asyncio.gather — parallel)
Research  ──┘
             ▼
          Analysis  (sequential — needs ingestion + research output)
             ▼
          Decision  (sequential — needs analysis KPIs)
             ▼
          merge_artifacts()  (pure Python — no LLM)
             ▼
          Execution  (sequential — calls Mock API with decision payload)
```

### 3.3 Content Parsers

The system accepts 6 input types. Each parser returns a normalized dict containing `clean_text`, `word_count`, `source_type`, and optionally extracted `entities`.

| Parser | Input Type | How It Works |
|---|---|---|
| `TextParser` | `text` | Passes raw string through; strips whitespace |
| `TextParser` | `url` | HTTP GET via `httpx`, HTML parsed with `BeautifulSoup`, extracts `<p>` text |
| `PDFParser` | `pdf` | `pdfplumber` for digital PDFs; falls back to `pytesseract` OCR for scanned pages |
| `DOCXParser` | `docx` | `python-docx` reads paragraphs and tables |
| `CSVParser` | `csv` | `pandas` reads CSV, converts to a descriptive text summary with statistics |
| `ExcelParser` | `excel` | `pandas` + `openpyxl` reads sheets, same summary format as CSV |

### 3.4 REST API Endpoints

#### Analysis

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/analyse/text` | Analyse raw text string |
| `POST` | `/api/analyse/url` | Scrape and analyse a URL |
| `POST` | `/api/analyse/file` | Upload and analyse a file (PDF/DOCX/CSV/Excel) |

#### Session

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/session/{id}/trace` | Full agent trace — all 6 artifact JSONs for a session |
| `GET` | `/api/session/{id}/status` | Current pipeline status (`pending`, `running`, `complete`, `failed`) |

#### State

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/state/{domain}` | Read current Mock API state for a domain |
| `POST` | `/api/state/reset` | Reset all domain states to factory defaults |

#### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Root health check — returns API version and status |
| `GET` | `/health` | Detailed health check |

Interactive Swagger docs: `http://localhost:8000/docs`

### 3.5 Mock API (30+ Endpoints)

The Mock API simulates real enterprise systems. All state is held in memory and mutated by incoming requests. Use `POST /api/state/reset` to restore defaults.

#### Logistics

| Endpoint | Action |
|---|---|
| `POST /api/logistics/pricing/update` | Adjust delivery price per kg on a route |
| `POST /api/logistics/routes/optimize` | Recompute route for fuel savings |
| `POST /api/notifications/bulk_send` | Notify carriers/buyers of a change |
| `POST /api/warehouse/reallocation` | Move SKUs between warehouse locations |

#### Business

| Endpoint | Action |
|---|---|
| `POST /api/crm/campaigns/create` | Launch a targeted marketing campaign |
| `POST /api/catalog/pricing/update` | Update regional product pricing |
| `POST /api/crm/workflows/trigger` | Trigger a CRM retention workflow |

#### Finance

| Endpoint | Action |
|---|---|
| `POST /api/finance/hedging/book` | Book an FX hedge contract (USD/PKR) |
| `POST /api/portfolio/rebalance/flag` | Flag a portfolio for rebalancing |

#### Policy

| Endpoint | Action |
|---|---|
| `POST /api/compliance/alert` | Send a regulatory compliance alert |
| `POST /api/duty/adjust` | Adjust import/export duty parameters |

#### Healthcare

| Endpoint | Action |
|---|---|
| `POST /api/procurement/emergency_order` | Place an emergency drug procurement order |
| `POST /api/notifications/clinical_alert` | Alert clinical staff to a drug shortage or advisory |

#### Urban

| Endpoint | Action |
|---|---|
| `POST /api/operations/dispatch` | Dispatch a repair crew to a fault location |
| `POST /api/communications/public_advisory` | Publish a public safety advisory via SMS/Twitter |

### 3.6 Database Models

Three tables are managed by SQLAlchemy (async). Tables are auto-created on startup.

**`analysis_sessions`**

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `created_at` | DateTime | Session creation timestamp |
| `domain` | String | Detected domain (e.g. `logistics`) |
| `input_type` | String | `text`, `url`, `pdf`, `docx`, `csv`, `excel` |
| `input_preview` | Text | First 500 chars of input |
| `status` | String | `pending`, `running`, `complete`, `failed` |
| `error_detail` | Text | Error message if status is `failed` |
| `duration_seconds` | Float | Total pipeline runtime |

**`agent_artifacts`**

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `session_id` | UUID | Foreign key → `analysis_sessions.id` |
| `agent_name` | String | e.g. `ingestion`, `analysis`, `decision` |
| `artifact_type` | String | e.g. `signals`, `kpi_impact`, `action_plan` |
| `content` | JSON | Full structured output from the agent |
| `created_at` | DateTime | Artifact creation timestamp |
| `duration_seconds` | Float | Agent runtime |

**`state_logs`**

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `session_id` | UUID | Foreign key → `analysis_sessions.id` |
| `domain` | String | Affected domain |
| `state_before` | JSON | Domain state snapshot before execution |
| `state_after` | JSON | Domain state snapshot after execution |
| `action_taken` | String | Mock API endpoint that was called |
| `delta` | JSON | Computed diff between before and after |
| `created_at` | DateTime | Log creation timestamp |

### 3.7 Configuration & Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
# Required
GEMINI_API_KEY=AIzaSy...

# Database (defaults to SQLite if not set)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/newsops

# Server
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
DEMO_MODE=false

# Optional model overrides (all default to gemini-1.5-flash)
MODEL_ORCHESTRATOR=gemini-1.5-pro
MODEL_INGESTION=gemini-1.5-flash
MODEL_ANALYSIS=gemini-1.5-flash
MODEL_DECISION=gemini-1.5-pro
MODEL_RESEARCH=gemini-1.5-flash
MODEL_EXECUTION=gemini-1.5-flash
MODEL_INPUT_PARSER=gemini-1.5-flash

# Optional email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASSWORD=yourpassword
```

---

## 4. Frontend — Nexus AI

The Flutter app provides a polished UI for submitting content, watching the live agent pipeline, and reviewing AI-generated insights and actions.

**Design:** Dark glassmorphic theme (purple / indigo / neon blue)
**State management:** Provider (ChangeNotifier)
**HTTP client:** Dio 5.4.3
**Cross-platform:** Android, iOS, Web, Windows

### 4.1 Folder Structure

```
nexus_ai/
├── lib/
│   ├── main.dart                    # Entry point — MultiProvider + MaterialApp routes
│   ├── core/
│   │   ├── theme.dart               # App-wide dark theme, colors, text styles
│   │   ├── constants.dart           # API base URL, timeout values, domain names
│   │   └── utils.dart               # Date formatting, string helpers
│   ├── data/
│   │   ├── models/                  # Dart data classes (AnalysisResult, AgentArtifact, etc.)
│   │   ├── api_service.dart         # Dio singleton — all HTTP calls to FastAPI
│   │   └── file_service.dart        # file_picker integration for uploading files
│   └── presentation/
│       ├── providers/
│       │   └── analysis_provider.dart  # Central ChangeNotifier — holds all app state
│       ├── screens/                 # 13 screens (see section 4.2)
│       └── widgets/                 # Shared UI components (cards, loaders, chips)
├── integration_test/                # Flutter integration tests
├── android/                         # Android-specific config
├── ios/                             # iOS-specific config
├── web/                             # Web support
├── windows/                         # Windows desktop support
└── pubspec.yaml                     # Flutter dependencies
```

### 4.2 Thirteen Screens

| Route | Screen | Purpose |
|---|---|---|
| `/splash` | **SplashScreen** | Shows logo; pings backend for connectivity |
| `/onboarding` | **OnboardingScreen** | 3-page feature carousel for first-time users |
| `/login` | **LoginScreen** | Email/password form (mocked authentication) |
| `/home` | **HomeScreen** | Dashboard with recent analyses, bottom navigation bar |
| `/analyze` | **AnalyzeScreen** | Input type selector, domain picker, content field, "Run AI Analysis" button |
| `/progress` | **AgentProgressScreen** | Live agent progress steps; polls `/api/session/{id}/status` every 2 seconds |
| `/insight` | **InsightScreen** | Severity score, key insight summary, business impact, KPIs affected |
| `/actions` | **ActionsScreen** | Top recommended action + 2 alternatives with feasibility and impact scores |
| `/simulate` | **SimulationScreen** | Animated execution log showing Mock API calls and before/after state |
| `/results` | **ResultsScreen** | Final green checkmark, execution timeline, projected outcomes |
| `/trace` | **TraceScreen** | Raw JSON output of all 6 agents (collapsible per agent) |
| `/workflow` | **WorkflowScreen** | Visual decision flow diagram and agent execution timeline |
| `/profile` | **ProfileScreen** | User settings, API endpoint config, "Reset Domain State" button |

### 4.3 State Management

`AnalysisProvider` (a `ChangeNotifier`) is the single source of truth for the app:

| Property | Type | Description |
|---|---|---|
| `inputType` | String | Selected input type (`text`, `url`, `file`) |
| `domain` | String | Selected domain override (or `auto`) |
| `content` | String | Raw text or URL entered by the user |
| `selectedFile` | File? | Picked file for upload |
| `isLoading` | bool | True while the pipeline is running |
| `sessionId` | String? | Session ID returned by FastAPI |
| `result` | AnalysisResult? | Full pipeline response |
| `agentProgressStep` | int | Current agent step index (0–5) |
| `liveLogs` | List\<String\> | Real-time log lines from the backend |
| `pollingTimer` | Timer? | 2-second polling timer for status updates |

---

## 5. End-to-End Data Flow

```
User opens AnalyzeScreen
  └─ selects input type, domain, enters content
        └─ taps "Run AI Analysis"
              └─ AnalysisProvider.runAnalysis()
                    └─ ApiService: POST /api/analyse/{type}
                                         │
                              ┌──────────┴──────────┐
                              │   FastAPI receives   │
                              └──────────┬──────────┘
                                         │
                              Parser extracts clean_text
                                         │
                              AnalysisSession saved (status: pending)
                                         │
                              Orchestrator.run()
                                         │
                           ┌────────────┴────────────┐
                     Ingestion Agent         Research Agent
                      (parallel via asyncio.gather)
                           └────────────┬────────────┘
                                         │
                                  Analysis Agent
                                         │
                                  Decision Agent
                                         │
                                 merge_artifacts()
                                         │
                                  Execution Agent
                                  calls Mock API
                                         │
                           AnalysisResponse JSON returned
                                         │
              Flutter polls /api/session/{id}/status every 2s
              (updates AgentProgressScreen live steps)
                                         │
                           status == "complete"
                                         │
                     Auto-navigate → InsightScreen
                                         │
                     User taps "Simulate Execution"
                                         │
                            SimulationScreen (animated)
                                         │
                              ResultsScreen (done)
                                         │
                          User can tap "View Agent Trace"
                                         │
                            TraceScreen (raw JSON)
```

---

## 6. Supported Domains

| Domain | What the System Analyses | Example Actions Taken |
|---|---|---|
| **logistics** | Fuel price changes, shipment disruptions, carrier outages, route efficiency, warehouse load | Update delivery pricing, optimize routes, notify carriers |
| **business** | Revenue trends, customer churn signals, regional sales drops, SKU performance | Launch CRM campaign, adjust catalog pricing, trigger retention workflow |
| **finance** | PKR/USD rate moves, KSE market shocks, FX exposure, portfolio risk, SBP policy | Book FX hedge, flag portfolio for rebalancing |
| **policy** | OGRA/SECP/SBP regulatory changes, gazette notifications, compliance deadlines, duty adjustments | Send compliance alert, adjust duty parameters |
| **healthcare** | Drug shortages, DRAP advisories, WHO alerts, formulary changes, procurement gaps | Place emergency procurement order, alert clinical staff |
| **urban** | Power outages (LESCO/WAPDA), water faults (WASA), traffic disruptions, CDA zone issues | Dispatch repair crew, publish public advisory |

---

## 7. Installation & Setup

### 7.1 Backend (Local)

**Prerequisites:** Python 3.11+, Tesseract OCR, Poppler

```bash
# 1. Clone the repository
git clone <repo-url>
cd AI-SEEKHO-HACKTHON/newsops

# 2. Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and add your GEMINI_API_KEY

# 5. Start the server (SQLite used by default if DATABASE_URL is not set)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be live at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

**Install Tesseract (required for PDF OCR):**
- Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

### 7.2 Backend (Docker)

```bash
cd AI-SEEKHO-HACKTHON/newsops

# 1. Create .env file first
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# 2. Start production containers (API + PostgreSQL)
docker compose up --build -d

# 3. View logs
docker compose logs -f newsops-api

# 4. Check health
curl http://localhost:8000/

# 5. Stop containers
docker compose down

# 6. Development mode (hot reload, source mounted)
docker compose -f docker-compose.dev.yml up --build

# 7. Shell into container
docker exec -it newsops-api bash
```

### 7.3 Frontend (Flutter)

**Prerequisites:** Flutter SDK 3.19+, Dart 3.3+

```bash
cd AI-SEEKHO-HACKTHON/nexus_ai

# 1. Install dependencies
flutter pub get

# 2. Update the API base URL in lib/core/constants.dart
#    Set it to your backend address (default: http://localhost:8000)

# 3. Run on connected device or emulator
flutter run

# 4. Build release APK (Android)
flutter build apk --release

# 5. Build for web
flutter build web --release

# 6. Build for Windows
flutter build windows --release
```

---

## 8. API Usage Examples

### Analyse raw text

```bash
curl -s -X POST http://localhost:8000/api/analyse/text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Pakistan State Oil reports fuel prices have surged 18% this week following a PKR devaluation. Logistics companies across Lahore and Karachi are facing increased delivery costs."
  }' | python -m json.tool
```

### Analyse a URL

```bash
curl -X POST http://localhost:8000/api/analyse/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.dawn.com/news/1234567"}'
```

### Analyse a file

```bash
# PDF
curl -X POST http://localhost:8000/api/analyse/file \
  -F "file=@report.pdf" \
  -F "input_type=pdf"

# CSV
curl -X POST http://localhost:8000/api/analyse/file \
  -F "file=@sales_data.csv" \
  -F "input_type=csv"
```

### Get agent trace for a session

```bash
curl http://localhost:8000/api/session/<session_id>/trace
```

### Read and reset domain state

```bash
# Read current logistics state
curl http://localhost:8000/api/state/logistics

# Reset all domain states to defaults
curl -X POST http://localhost:8000/api/state/reset
```

### Example response (abbreviated)

```json
{
  "session_id": "a1b2c3d4-...",
  "domain": "logistics",
  "severity": 8,
  "severity_label": "Critical",
  "insight": "An 18% fuel price surge will increase delivery costs by approximately PKR 2.4M per month across the Lahore–Karachi corridor.",
  "top_action": {
    "action_id": "logistics_pricing_update",
    "endpoint": "/api/logistics/pricing/update",
    "feasibility_score": 9,
    "impact_score": 8,
    "payload": { "route_id": "R-001", "price_delta_pct": 12.0 }
  },
  "alternative_actions": [...],
  "kpis_affected": ["fuel_ratio", "delivery_cost_per_kg", "route_efficiency"],
  "before_state": { "fuel_ratio": 0.28, "delivery_cost_per_kg": 45.0 },
  "after_state":  { "fuel_ratio": 0.31, "delivery_cost_per_kg": 50.4 },
  "delta": { "fuel_ratio": "+0.03", "delivery_cost_per_kg": "+5.4" },
  "notifications_sent": ["carrier_bulk_notification"],
  "trace_url": "/api/session/a1b2c3d4-.../trace",
  "duration_seconds": 14.3
}
```

---

## 9. Running Tests

```bash
cd newsops

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_agents.py -v

# Run with coverage report
pytest --cov=. --cov-report=term-missing
```

**Test files:**

| File | What It Tests |
|---|---|
| `tests/test_parsers.py` | Text, PDF, CSV, Excel parser output |
| `tests/test_helpers.py` | Domain detection, UUID generation, delta computation |
| `tests/test_database.py` | ORM session creation, artifact queries |
| `tests/test_mock_api.py` | Mock endpoint responses and state mutations |
| `tests/test_agents.py` | Agent orchestration (parallel + sequential execution) |
| `tests/test_pipeline.py` | Full end-to-end pipeline run |
| `tests/test_routers.py` | FastAPI route handlers via TestClient |
| `tests/test_docker.py` | Docker image build validation |

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| Backend framework | FastAPI 0.115 + Uvicorn (ASGI) |
| AI / LLM | Google Gemini 1.5 Flash & Pro (`google-genai`) |
| Database ORM | SQLAlchemy 2.0 (async) + `aiosqlite` / `asyncpg` |
| PDF / OCR | `pdfplumber`, `pytesseract`, `pdf2image`, `pymupdf` |
| Document parsing | `python-docx`, `pandas`, `openpyxl` |
| Web scraping | `httpx`, `beautifulsoup4`, `lxml` |
| Containerisation | Docker + Docker Compose |
| Frontend | Flutter 3.19 + Dart 3.3 |
| State management | Provider 6.1.2 (ChangeNotifier) |
| HTTP client (Flutter) | Dio 5.4.3 |
| UI libraries | `google_fonts`, `flutter_animate`, `shimmer`, `percent_indicator` |
| Testing | `pytest`, `pytest-asyncio`, Flutter integration_test |
