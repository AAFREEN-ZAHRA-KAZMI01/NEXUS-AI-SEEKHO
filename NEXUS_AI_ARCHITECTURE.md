# NEXUS AI — Architecture Reference

> Deep-dive architecture document for **Nexus AI**, the Autonomous Multi-Agent Intelligence System.  
> For setup, API reference, and usage see [README.md](./README.md).

---

## Table of Contents

1. [System Layers](#1-system-layers)
2. [Component Map](#2-component-map)
3. [Agent Pipeline — Detailed Sequence](#3-agent-pipeline--detailed-sequence)
4. [Agent Internals](#4-agent-internals)
5. [Parser Architecture](#5-parser-architecture)
6. [Mock API State Machine](#6-mock-api-state-machine)
7. [Database Schema](#7-database-schema)
8. [Frontend Architecture — Flutter](#8-frontend-architecture--flutter)
9. [Frontend Architecture — Vanilla Web](#9-frontend-architecture--vanilla-web)
10. [API Contract (Request → Response)](#10-api-contract-request--response)
11. [Real vs Mock APIs](#11-real-vs-mock-apis)
12. [Configuration & Environment Model](#12-configuration--environment-model)
13. [Concurrency Model](#13-concurrency-model)
14. [Error Handling & Fallback Strategy](#14-error-handling--fallback-strategy)
15. [Deployment Architecture](#15-deployment-architecture)

---

## 1. System Layers

Nexus AI is built in four distinct layers, each with a clear boundary:

```
┌──────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                          │
│  Flutter App (nexus_ai/)  |  Vanilla Web (nexus_web/)        │
│  Provider state mgmt      |  localStorage state mgmt         │
└──────────────────────────────────┬───────────────────────────┘
                                   │  REST/JSON over HTTP
┌──────────────────────────────────▼───────────────────────────┐
│  API LAYER                                                   │
│  FastAPI 0.115 (ASGI / Uvicorn)                              │
│  Routers: /api/analyse  /api/session  /api/state  /health    │
│  CORS, Rate-limiting (slowapi), Pydantic validation          │
└──────────────────────────────────┬───────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────┐
│  INTELLIGENCE LAYER                                          │
│  Pipeline orchestrator → 6 AI Agents (Google Gemini 2.5)    │
│  Parser layer (5 format parsers + document intelligence)     │
│  Mock API layer (30+ endpoints, in-memory state)             │
└──────────────────────────────────┬───────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────┐
│  PERSISTENCE LAYER                                           │
│  SQLAlchemy 2.0 async                                        │
│  SQLite (dev) / PostgreSQL (prod)                            │
│  Tables: analysis_sessions, agent_artifacts, state_logs      │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Component Map

```
newsops/
│
├── main.py              FastAPI app factory
│   └── lifespan()       Startup: DB init, Mock API state init
│
├── config.py            Central config
│   ├── MODELS{}         Agent-name → Gemini model-ID mapping
│   ├── DOMAINS[]        ["logistics","business","finance","policy","healthcare","urban"]
│   └── SEVERITY_LABELS  1-10 → human label mapping
│
├── routers/
│   ├── analysis.py      POST /api/analyse/{text|url|file}
│   │   └── calls pipeline.run_pipeline()
│   ├── session.py       GET /api/session/{id}/{status|trace}
│   └── state.py         GET /api/state/{domain}  POST /api/state/reset
│
├── pipelines/
│   └── pipeline.py      run_pipeline(input, type, domain)
│       ├── 1. route to correct parser
│       ├── 2. create AnalysisSession (status=pending)
│       └── 3. call orchestrator.run()
│
├── agents/
│   ├── orchestrator.py  run(clean_text, domain, session_id)
│   │   ├── asyncio.gather(ingestion, research)   ← PARALLEL
│   │   ├── analysis(merged_artifacts)            ← SEQUENTIAL
│   │   ├── decision(analysis_out)                ← SEQUENTIAL
│   │   ├── merge_artifacts(all_outputs)          ← PYTHON ONLY
│   │   └── execution(decision_out)              ← SEQUENTIAL
│   │
│   ├── ingestion_agent.py   extract facts, entities, signals
│   ├── research_agent.py    credibility, PK context, contradictions
│   ├── analysis_agent.py    KPI mapping, severity score, PKR impact
│   ├── decision_agent.py    top-3 actions, payloads, rationale
│   ├── execution_agent.py   call Mock API, capture delta
│   └── mock_responses.py    deterministic fallback responses
│
├── parsers/
│   ├── document_intelligence.py  MIME-type router → correct parser
│   ├── text_parser.py            plain text + URL scraping
│   ├── pdf_parser.py             pdfplumber + tesseract OCR
│   ├── docx_parser.py            python-docx
│   ├── csv_parser.py             pandas statistics summary
│   └── excel_parser.py           pandas multi-sheet summary
│
├── mock_api/
│   ├── endpoints.py     30+ FastAPI routes under /mock/*
│   └── state_store.py   in-memory dict per domain
│       └── DOMAIN_STATES{"logistics": {...}, "finance": {...}, ...}
│
├── database/
│   ├── db.py            async engine, session factory, init_db()
│   └── models.py        AnalysisSession, AgentArtifact, StateLog
│
└── schemas/
    ├── input_schemas.py   TextAnalysisRequest, UrlAnalysisRequest, FileAnalysisRequest
    └── output_schemas.py  AnalysisResponse, KpiAffected, TopAction, ArtifactSet
```

---

## 3. Agent Pipeline — Detailed Sequence

```
POST /api/analyse/text
│
▼
pipeline.run_pipeline("raw text", "text", "auto")
│
├─ text_parser.parse() → clean_text
│
├─ DB: INSERT analysis_sessions (status=pending)
│
└─ orchestrator.run(clean_text, domain, session_id)
   │
   ├─ DB: UPDATE status=running
   │
   ├── [STEP 1 — PARALLEL — asyncio.gather]
   │   ├─ IngestionAgent.run(clean_text)
   │   │   └─ Gemini 2.5 Flash call #1
   │   │       prompt: extract facts, signals, entities
   │   │       output: {facts[], signals[], confidence_scores{}}
   │   │
   │   └─ ResearchAgent.run(clean_text)
   │       └─ Gemini 2.5 Flash call #2
   │           prompt: verify credibility, PK context, flags
   │           output: {credibility_score, pk_context{}, flags[]}
   │
   ├── [STEP 2 — SEQUENTIAL]
   │   └─ AnalysisAgent.run(ingestion_out, research_out)
   │       └─ Gemini 2.5 Flash call #3
   │           prompt: map signals to KPIs, score severity, PKR impact
   │           output: {severity_score, kpis_affected[], pkr_impact}
   │
   ├── [STEP 3 — SEQUENTIAL]
   │   └─ DecisionAgent.run(analysis_out, domain)
   │       └─ Gemini 2.5 Flash call #4
   │           prompt: rank top-3 actions from domain catalog
   │           output: {top_action{}, alternatives[], api_payloads{}}
   │
   ├── [STEP 4 — PYTHON ONLY]
   │   └─ merge_artifacts(ing, res, ana, dec)
   │       → unified {"ingestion":..., "research":..., ...}
   │
   ├── [STEP 5 — SEQUENTIAL]
   │   └─ ExecutionAgent.run(decision_out, domain)
   │       ├─ read state_before from mock_api.state_store
   │       ├─ HTTP POST to /mock/{domain}/{action_endpoint}
   │       ├─ read state_after
   │       ├─ compute delta (helpers.compute_delta)
   │       └─ DB: INSERT state_logs
   │
   ├─ DB: INSERT agent_artifacts (one row per agent)
   └─ DB: UPDATE status=complete
        return AnalysisResponse
```

**Timing breakdown (approximate, with live Gemini key):**

| Step | Parallel? | Duration |
|------|-----------|---------|
| Parse input | No | < 1s |
| Ingestion + Research | Yes (parallel) | 3–6s |
| Analysis | No | 4–7s |
| Decision | No | 5–8s |
| merge_artifacts | No (Python) | < 0.1s |
| Execution | No | 1–3s |
| **Total** | — | **~15–25s** |

---

## 4. Agent Internals

### Prompt Engineering Pattern

Every agent follows the same structure:

```python
class BaseAgent:
    def __init__(self, client: genai.Client, model: str):
        self.client = client
        self.model = model

    async def run(self, *args) -> dict:
        prompt = self._build_prompt(*args)
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=GenerateContentConfig(response_mime_type="application/json")
        )
        return self._parse_response(response.text)
```

- All agents request `response_mime_type="application/json"` — Gemini is instructed to return structured JSON only, no markdown.
- Every `run()` is `async` — compatible with `asyncio.gather` for parallel execution.
- Every agent wraps Gemini calls in `try/except` → falls back to `mock_responses.get_mock(agent_name)` on any error.

### Domain-Specific Prompt Injection

`config.py` defines domain-specific context injected into AnalysisAgent and DecisionAgent prompts:

```python
DOMAIN_CONTEXT = {
    "finance": "Pakistan financial context: PKR/USD exchange rate, KSE-100 index, "
               "SBP (State Bank of Pakistan) monetary policy, SECP regulations...",
    "logistics": "Pakistan logistics context: LESCO/WAPDA power outages, "
                 "carrier disruptions, Lahore/Karachi route network...",
    ...
}
```

### Action Catalogs

`DecisionAgent` selects actions from domain-specific catalogs defined in `config.py`:

```python
ACTION_CATALOG = {
    "logistics": [
        {"action": "pricing/update", "endpoint": "/mock/logistics/pricing/update"},
        {"action": "routes/optimize", "endpoint": "/mock/logistics/routes/optimize"},
        {"action": "notifications/bulk_send", "endpoint": "/mock/logistics/notifications/bulk_send"},
        {"action": "warehouse/reallocation", "endpoint": "/mock/logistics/warehouse/reallocation"},
    ],
    "finance": [
        {"action": "hedging/book", "endpoint": "/mock/finance/hedging/book"},
        {"action": "portfolio/rebalance/flag", "endpoint": "/mock/finance/portfolio/rebalance/flag"},
    ],
    ...
}
```

---

## 5. Parser Architecture

`document_intelligence.py` is the unified entry point. It inspects MIME type and routes:

```
Input (bytes + filename + content_type)
        ↓
DocumentIntelligence.parse(file_bytes, filename, content_type)
        │
        ├─ content_type == "application/pdf"  → PDFParser
        ├─ content_type == "text/csv"         → CSVParser
        ├─ content_type == "application/vnd.openxmlformats..."
        │   └─ filename ends with .docx       → DOCXParser
        │   └─ filename ends with .xlsx/.xls  → ExcelParser
        └─ default                            → TextParser
        │
        ▼
   clean_text: str  (normalised plain text, ready for agents)
```

### URL Parsing (TextParser)

```
URL input
    ↓
httpx.AsyncClient.get(url, timeout=15s)
    ↓
BeautifulSoup(response.text, "html.parser")
    ↓
soup.find_all("p") → join → strip whitespace → clean_text
```

### PDF Parsing (PDFParser)

```
PDF bytes
    ├─ pdfplumber.open() → extract text from each page
    │   ├─ if text > 50 chars → return text (digital PDF)
    │   └─ if text ≤ 50 chars → treat as scanned
    │       └─ convert page to image → pytesseract.image_to_string() → OCR text
    └─ join all pages → clean_text
```

---

## 6. Mock API State Machine

`mock_api/state_store.py` holds an in-memory dict initialised at startup:

```python
DOMAIN_STATES = {
    "logistics": {
        "pricing": {"base_rate_pkr": 850, "fuel_surcharge": 0.12, ...},
        "routes":  {"active_zones": [...], "avg_delivery_hrs": 4.2, ...},
        ...
    },
    "finance": {
        "hedging": {"open_positions": [], "hedge_ratio": 0.0, ...},
        ...
    },
    ...
}
```

**State lifecycle per request:**

```
GET /api/state/{domain}        → read DOMAIN_STATES[domain]         (no mutation)
POST /mock/{domain}/{action}   → mutate DOMAIN_STATES[domain]       (ExecutionAgent)
POST /api/state/reset          → reinitialise DOMAIN_STATES to defaults
```

Each Mock API endpoint handler:
1. Validates incoming payload (Pydantic)
2. Applies the mutation to `DOMAIN_STATES[domain]`
3. Returns `{ "success": true, "updated": {...} }`

`ExecutionAgent` reads state before and after the call, then calls `helpers.compute_delta(before, after)` to produce a diff object stored in `state_logs`.

---

## 7. Database Schema

```sql
-- analysis_sessions
CREATE TABLE analysis_sessions (
    id               TEXT PRIMARY KEY,   -- UUID
    created_at       DATETIME,
    domain           TEXT,               -- logistics | business | finance | policy | healthcare | urban
    input_type       TEXT,               -- text | url | file
    input_preview    TEXT,               -- first 300 chars
    status           TEXT,               -- pending | running | complete | failed
    error_detail     TEXT,
    duration_seconds REAL
);

-- agent_artifacts (one row per agent per session)
CREATE TABLE agent_artifacts (
    id               TEXT PRIMARY KEY,   -- UUID
    session_id       TEXT REFERENCES analysis_sessions(id),
    agent_name       TEXT,               -- ingestion | research | analysis | decision | execution
    artifact_type    TEXT,
    content          JSON,               -- full agent output dict
    created_at       DATETIME,
    duration_seconds REAL
);

-- state_logs (one row per execution)
CREATE TABLE state_logs (
    id               TEXT PRIMARY KEY,   -- UUID
    session_id       TEXT REFERENCES analysis_sessions(id),
    domain           TEXT,
    state_before     JSON,
    state_after      JSON,
    action_taken     TEXT,               -- e.g. "routes/optimize"
    delta            JSON,               -- compute_delta(before, after) output
    created_at       DATETIME
);
```

**ORM layer** (`database/db.py`):
- `AsyncEngine` from `create_async_engine(DATABASE_URL)`
- `AsyncSession` factory via `async_sessionmaker`
- `init_db()` called at app startup via FastAPI `lifespan`

**Connection string switching:**
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nexus_ai.db")
# For PostgreSQL:
# DATABASE_URL = "postgresql+asyncpg://user:pass@host/dbname"
```

---

## 8. Frontend Architecture — Flutter

### Module Dependency Graph

```
main.dart
    └─ MultiProvider
        ├─ AnalysisProvider (ChangeNotifier)
        │   ├─ ApiService (Dio singleton)
        │   ├─ FileService (file_picker)
        │   └─ notifyListeners() → all Consumer<AnalysisProvider> widgets
        └─ AuthProvider (ChangeNotifier)
            └─ AuthService (mocked, no real auth)

Screens consume AnalysisProvider via:
    context.read<AnalysisProvider>()   ← write / trigger actions
    context.watch<AnalysisProvider>()  ← rebuild on change
    Consumer<AnalysisProvider>         ← scoped rebuilds
```

### Screen Navigation Flow

```
SplashScreen
    └─ connectivity OK? → OnboardingScreen (first run) / HomeScreen (returning)

OnboardingScreen
    └─ Get Started → LoginScreen

LoginScreen
    └─ login (mocked) → HomeScreen

HomeScreen
    └─ New Analysis → AnalyzeScreen

AnalyzeScreen
    └─ runAnalysis() → navigate to AgentProgressScreen

AgentProgressScreen (polls every 2s)
    └─ status == complete → InsightScreen

InsightScreen
    ├─ View Actions → ActionsScreen
    └─ View Trace → TraceScreen

ActionsScreen
    └─ Execute → SimulationScreen

SimulationScreen
    └─ Done → ResultsScreen

ResultsScreen
    └─ back to HomeScreen or start new analysis
```

### AnalysisProvider State Transitions

```
IDLE
  │ user fills form + taps Analyse
  ▼
LOADING (isLoading=true)
  │ POST /api/analyse/* → sessionId received
  ▼
POLLING (pollingTimer running, every 2s)
  │ GET /api/session/{id}/status
  │ status=running → increment agentProgressStep (0→5)
  │ status=complete → fetch full result
  ▼
COMPLETE (isLoading=false, result set)
  │
  ▼
AUTO-NAVIGATE to InsightScreen
```

### Dio HTTP Client (`data/services/api_service.dart`)

```dart
class ApiService {
    final Dio _dio = Dio(BaseOptions(
        baseUrl: ApiConstants.baseUrl,    // from api_constants.dart
        connectTimeout: Duration(seconds: 30),
        receiveTimeout: Duration(seconds: 120),  // pipeline can take 25s
    ));

    Future<AnalysisResponse> analyseText(TextAnalysisRequest req) async {
        final res = await _dio.post('/api/analyse/text', data: req.toJson());
        return AnalysisResponse.fromJson(res.data);
    }
    // ... analyseUrl(), analyseFile() (multipart), getSessionStatus(), getSessionTrace()
}
```

---

## 9. Frontend Architecture — Vanilla Web

### State Management

`js/state.js` implements a simple shared state object backed by `localStorage`:

```javascript
const AppState = {
    get(key)         { return JSON.parse(localStorage.getItem(key)); },
    set(key, value)  { localStorage.setItem(key, JSON.stringify(value)); },
    clear()          { localStorage.clear(); },

    // Typed helpers
    getSession()     { return this.get('session'); },          // { id, domain, status }
    setSession(s)    { this.set('session', s); },
    getResult()      { return this.get('analysis_result'); },  // full AnalysisResponse
    setResult(r)     { this.set('analysis_result', r); },
    getUser()        { return this.get('user'); },              // mocked user object
};
```

### HTTP Client (`js/api.js`)

```javascript
async function _fetch(path, options = {}) {
    const res = await fetch(BASE_URL + path, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    return res.json();
}

const API = {
    analyseText: (text, domain) => _fetch('/api/analyse/text', {
        method: 'POST', body: JSON.stringify({ text, domain })
    }),
    getStatus: (id) => _fetch(`/api/session/${id}/status`),
    getResult: (id) => _fetch(`/api/session/${id}/trace`),
    resetState: ()  => _fetch('/api/state/reset', { method: 'POST' }),
};
```

### Page Communication Pattern

Since there is no SPA router, pages communicate via `AppState`:

```
analyze.html → submit → API.analyseText() → AppState.setSession({id, domain})
progress.html → onload → start polling AppState.getSession().id
             → status==complete → AppState.setResult(full_response) → redirect insight.html
insight.html → onload → render AppState.getResult()
```

---

## 10. API Contract (Request → Response)

### Text Analysis Request

```json
POST /api/analyse/text
{
    "text": "LESCO announces planned 8-hour loadshedding in DHA Lahore from Monday...",
    "domain": "auto"
}
```

### Full Analysis Response

```json
{
    "session_id": "a1b2c3d4-...",
    "domain": "logistics",
    "severity_score": 8,
    "severity_label": "High",
    "key_insight": "LESCO 8-hour outage will disrupt cold-chain warehouses in DHA, Gulberg, and Johar. Estimated 340 PKR/delivery cost increase.",
    "kpis_affected": [
        {
            "kpi": "delivery_time_hours",
            "before": 4.2,
            "after": 6.1,
            "change_pct": 45.2,
            "unit": "hours"
        }
    ],
    "pkr_impact": 2400000,
    "top_action": {
        "action": "routes/optimize",
        "endpoint": "/mock/logistics/routes/optimize",
        "confidence": 0.91,
        "rationale": "Rerouting to backup zones minimises time-in-transit during outage window.",
        "payload": {
            "zones": ["DHA", "Gulberg", "Johar"],
            "backup_hubs": ["Township", "Bahria"],
            "priority": "time_critical"
        }
    },
    "alternative_actions": [
        {
            "action": "notifications/bulk_send",
            "confidence": 0.76,
            "rationale": "Proactively notifying customers reduces escalations."
        },
        {
            "action": "warehouse/reallocation",
            "confidence": 0.61,
            "rationale": "Move perishable stock to generator-backed warehouses."
        }
    ],
    "state_before": {
        "routes": { "active_zones": ["DHA","Gulberg","Johar","Cantt"], "avg_delivery_hrs": 4.2 }
    },
    "state_after": {
        "routes": { "active_zones": ["Township","Bahria","Cantt"], "avg_delivery_hrs": 3.8 }
    },
    "delta": {
        "avg_delivery_hrs": { "before": 4.2, "after": 3.8, "change": -0.4, "change_pct": -9.5 }
    },
    "artifacts": {
        "ingestion": { "facts": [...], "signals": [...] },
        "research":  { "credibility_score": 0.88, "pk_context": {...} },
        "analysis":  { "severity_score": 8, "kpis_affected": [...] },
        "decision":  { "top_action": {...}, "alternatives": [...] },
        "execution": { "status": "success", "mock_response": {...} }
    },
    "duration_seconds": 19.3,
    "created_at": "2026-05-21T10:30:00Z"
}
```

---

## 11. Real vs Mock APIs

Nexus AI uses a **mock-first integration strategy**. The table below lists every external integration point and its current state:

| Integration | Category | Current State | Real API to Swap In |
|-------------|----------|---------------|---------------------|
| Google Gemini 2.5 Flash | AI/LLM inference | **REAL** (via `google-genai` SDK) | — already real |
| Logistics pricing engine | ERP/TMS | Mock (`/mock/logistics/pricing/update`) | SAP TM, Oracle TMS |
| Logistics route optimizer | Route planning | Mock (`/mock/logistics/routes/optimize`) | HERE Maps, Google Routes API |
| Bulk SMS/email notifications | Notification | Mock (`/mock/logistics/notifications/bulk_send`) | Twilio, Mailchimp |
| Warehouse reallocation | WMS | Mock (`/mock/logistics/warehouse/reallocation`) | Manhattan WMS, SAP EWM |
| CRM campaign creation | CRM | Mock (`/mock/business/crm/campaigns/create`) | Salesforce, HubSpot |
| Product catalog pricing | E-commerce | Mock (`/mock/business/catalog/pricing/update`) | Shopify, WooCommerce |
| FX hedge booking | Finance | Mock (`/mock/finance/hedging/book`) | Bloomberg TOMS, Murex |
| Portfolio rebalance flag | Asset mgmt | Mock (`/mock/finance/portfolio/rebalance/flag`) | Charles River, BlackRock Aladdin |
| Compliance alert | Regulatory | Mock (`/mock/policy/compliance/alert`) | Thomson Reuters ACCELUS |
| Duty rate adjustment | Customs | Mock (`/mock/policy/duty/adjust`) | FBR API (Pakistan customs) |
| Emergency medical order | Healthcare | Mock (`/mock/healthcare/procurement/emergency_order`) | SAP Ariba, DRAP portal |
| Clinical alert | Healthcare | Mock (`/mock/healthcare/notifications/clinical_alert`) | Epic EHR, Doximity |
| Urban crew dispatch | Field ops | Mock (`/mock/urban/operations/dispatch`) | ServiceMax, ClickSoftware |
| Public advisory | Communications | Mock (`/mock/urban/communications/public_advisory`) | Twilio Notify, AlertMedia |

**Swapping a mock for a real API requires only:**
1. Update `ACTION_CATALOG[domain][action]["endpoint"]` in `config.py`
2. Update `ExecutionAgent._build_headers()` to include real auth headers
3. No changes to agents, orchestrator, or database required

---

## 12. Configuration & Environment Model

```
config.py
    ├── GEMINI_API_KEY      → from os.environ (required)
    ├── DATABASE_URL        → from os.environ (default: sqlite+aiosqlite)
    ├── MODELS{}            → agent_name → gemini model id
    ├── DOMAINS[]           → valid domain names
    ├── SEVERITY_LABELS{}   → 1-10 → label string
    ├── DOMAIN_CONTEXT{}    → domain → PK-specific prompt context
    └── ACTION_CATALOG{}    → domain → list of {action, endpoint}
```

All sensitive values come from environment variables (never hardcoded).  
`.env.example` is committed; `.env` is gitignored.

---

## 13. Concurrency Model

Nexus AI uses **Python asyncio** throughout:

```
FastAPI request → async route handler
                        ↓
              pipeline.run_pipeline()  (async)
                        ↓
              orchestrator.run()       (async)
                ├── asyncio.gather(
                │       ingestion_agent.run(),   ← Task A
                │       research_agent.run()     ← Task B
                │   )                           ← await both
                ├── analysis_agent.run()         ← await single
                ├── decision_agent.run()         ← await single
                └── execution_agent.run()        ← await single
```

- FastAPI + Uvicorn handle concurrent HTTP requests via asyncio event loop.
- No threading — all I/O (Gemini API calls, DB writes, Mock API HTTP calls) is awaited.
- The 2-second polling from the Flutter frontend creates short-lived async requests that interleave with ongoing pipeline execution without blocking.
- SQLAlchemy async session is scoped per-request, preventing session sharing across concurrent requests.

---

## 14. Error Handling & Fallback Strategy

### Gemini API Errors

```python
try:
    response = await gemini_client.aio.models.generate_content(...)
    return parse_response(response.text)
except Exception as e:
    logger.warning(f"Gemini call failed: {e}. Using mock response.")
    return mock_responses.get_mock(self.agent_name)
```

Every agent falls back to `mock_responses.py` on any Gemini error (rate limit, invalid key, network timeout).

### Pipeline Errors

```python
try:
    result = await orchestrator.run(clean_text, domain, session_id)
    await db.update_session(session_id, status="complete", ...)
except Exception as e:
    await db.update_session(session_id, status="failed", error_detail=str(e))
    raise HTTPException(500, detail=str(e))
```

Session status is always updated — clients polling `/api/session/{id}/status` will receive `"failed"` and can surface the error.

### Frontend Errors (Flutter)

```dart
try {
    result = await apiService.analyseText(request);
    state = AnalysisState.complete(result);
} on DioException catch (e) {
    state = AnalysisState.error(e.message);
} catch (e) {
    state = AnalysisState.error("Unexpected error");
}
notifyListeners();
```

Error state surfaces on the AnalyzeScreen with a retry button.

---

## 15. Deployment Architecture

### Development (Local)

```
localhost:8000  ← uvicorn main:app --reload
localhost:3000  ← python -m http.server (nexus_web/)
Android emulator ← flutter run (connects to 10.0.2.2:8000)
```

### Docker (Single Service)

```yaml
# docker-compose.yml
services:
  newsops-api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./data:/app/data    # SQLite persistence
```

`Dockerfile` uses `python:3.11-slim` with:
- `apt-get install tesseract-ocr poppler-utils` (OCR support)
- Multi-stage not used (single layer for simplicity)

### Production-Ready Additions (not yet implemented)

| Component | Recommended Addition |
|-----------|---------------------|
| Database | Switch `DATABASE_URL` to PostgreSQL (asyncpg) |
| Auth | Replace mocked auth with JWT (fastapi-users) |
| Rate limiting | Already present via slowapi — tune limits |
| HTTPS | Terminate at nginx/Caddy reverse proxy |
| Gemini | Add retry with exponential backoff |
| Monitoring | Add Prometheus metrics endpoint |
| Flutter Web | Deploy to Firebase Hosting or Vercel |

---

## Quick Reference: Key Files

| File | Lines | Role |
|------|-------|------|
| `newsops/agents/orchestrator.py` | 215 | Pipeline runner |
| `newsops/agents/decision_agent.py` | 569 | Action ranking (largest agent) |
| `newsops/agents/execution_agent.py` | 477 | Mock API executor |
| `newsops/agents/analysis_agent.py` | 311 | KPI scoring |
| `newsops/agents/mock_responses.py` | 1023 | Fallback responses |
| `newsops/parsers/document_intelligence.py` | 683 | Parser router |
| `newsops/mock_api/endpoints.py` | ~500 | 30+ Mock API routes |
| `nexus_ai/lib/presentation/providers/analysis_provider.dart` | — | Central Flutter state |
| `nexus_ai/lib/data/services/api_service.dart` | — | Dio HTTP client |
| `nexus_web/js/state.js` | — | localStorage state |
| `nexus_web/js/api.js` | — | Web HTTP client |

---

*Generated for AI Seekho Hackathon — Nexus AI by Aafreen Zahra Kazmi*
