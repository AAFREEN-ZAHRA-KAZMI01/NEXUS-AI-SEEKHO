# NewsOps — Autonomous Multi-Agent Intelligence System

NewsOps is a production-grade FastAPI backend that ingests any news article, document, URL, or data file, runs it through a multi-agent AI pipeline, and autonomously produces domain-specific business actions — from repricing logistics routes to creating CRM campaigns and booking FX hedges.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI  (:8000)                         │
│   POST /api/analyse/text   POST /api/analyse/url                │
│   POST /api/analyse/file   GET  /api/session/{id}/trace         │
│   GET  /api/state/{domain} POST /api/state/reset                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      run_pipeline()                             │
│   Parsers: text | url | pdf | docx | csv | excel                │
│   → save_session()  →  Orchestrator.run()                       │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────┐
│               Orchestrator                      │
│  ┌──────────────┐   ┌──────────────┐           │
│  │IngestionAgent│   │ ResearchAgent│  (parallel)│
│  └──────┬───────┘   └──────┬───────┘           │
│         └──────────┬───────┘                   │
│                    ▼                            │
│            ┌───────────────┐                   │
│            │AnalysisAgent  │  (sequential)      │
│            └───────┬───────┘                   │
│                    ▼                            │
│            ┌───────────────┐                   │
│            │ DecisionAgent │  (sequential)      │
│            └───────┬───────┘                   │
│                    ▼                            │
│            ┌───────────────┐                   │
│            │merge_artifacts│  (pure Python)     │
│            └───────┬───────┘                   │
│                    ▼                            │
│            ┌───────────────┐                   │
│            │ExecutionAgent │  (calls Mock API)  │
│            └───────────────┘                   │
└────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────┐
│           Mock API  (/api/*)                    │
│   Stateful domain stores: logistics, business,  │
│   finance, policy, healthcare, urban            │
└────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────┐
│       PostgreSQL  (asyncpg + SQLAlchemy)        │
│   analysis_sessions  agent_artifacts  state_logs│
└────────────────────────────────────────────────┘
```

---

## Docker

### Prerequisites

Create a `.env` file before running any Docker command:

```bash
cp .env.example .env
# Then open .env and add your GEMINI_API_KEY
```

### Development (hot reload, source mounted)

```bash
docker compose -f docker-compose.dev.yml up --build
```

### Production

```bash
docker compose up --build -d
```

### View logs

```bash
docker compose logs -f newsops-api
```

### Stop

```bash
docker compose down
```

### Reset state (clear mock API state)

```bash
curl -X POST http://localhost:8000/api/state/reset
```

### Shell into container

```bash
docker exec -it newsops-api bash
```

### Rebuild after code change (prod)

```bash
docker compose up --build -d
```

### Check health

```bash
curl http://localhost:8000/
```

---

## Installation

### 1. Clone & create virtualenv

```bash
git clone <repo-url>
cd newsops
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

`.env` contents:

```env
GEMINI_API_KEY=AIzaSy...
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/newsops
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true

# Optional model overrides
MODEL_ORCHESTRATOR=gemini-1.5-pro
MODEL_INGESTION=gemini-1.5-flash
MODEL_ANALYSIS=gemini-1.5-flash
MODEL_DECISION=gemini-1.5-pro
MODEL_RESEARCH=gemini-1.5-flash
MODEL_EXECUTION=gemini-1.5-flash
MODEL_INPUT_PARSER=gemini-1.5-flash
```

### 4. Start PostgreSQL

```bash
# Docker (quickest)
docker run -d \
  --name newsops-db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=newsops \
  -p 5432:5432 \
  postgres:15
```

Tables are created automatically on first startup.

### 5. Run the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs available at: `http://localhost:8000/docs`

---

## All API Endpoints

### Health

```bash
curl http://localhost:8000/
```

---

### Analysis Endpoints

#### Analyse raw text

```bash
curl -X POST http://localhost:8000/api/analyse/text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "OGRA has increased petroleum prices by 12% effective immediately, raising fuel costs across all transport sectors."
  }'
```

#### Analyse a URL

```bash
curl -X POST http://localhost:8000/api/analyse/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.dawn.com/news/1234567"
  }'
```

#### Analyse a file (PDF / DOCX / CSV / Excel)

```bash
curl -X POST http://localhost:8000/api/analyse/file \
  -F "file=@report.pdf" \
  -F "input_type=pdf"
```

```bash
curl -X POST http://localhost:8000/api/analyse/file \
  -F "file=@sales_data.csv" \
  -F "input_type=csv"
```

---

### Session Endpoints

#### Get pipeline trace (all agent artifacts)

```bash
curl http://localhost:8000/api/session/<session_id>/trace
```

#### Get session status

```bash
curl http://localhost:8000/api/session/<session_id>/status
```

---

### State Endpoints

#### Read current mock state for a domain

```bash
curl http://localhost:8000/api/state/logistics
curl http://localhost:8000/api/state/finance
curl http://localhost:8000/api/state/healthcare
```

#### Reset all domain states to defaults

```bash
curl -X POST http://localhost:8000/api/state/reset
```

---

### Mock API — Logistics

```bash
# Update route pricing
curl -X POST http://localhost:8000/api/logistics/pricing/update \
  -H "Content-Type: application/json" \
  -d '{"route_id":"R-001","price_delta_pct":5.0,"effective_date":"2026-06-01","session_id":"test"}'

# Optimise route fuel
curl -X POST http://localhost:8000/api/logistics/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{"current_route_id":"R-001","optimization_target":"fuel","session_id":"test"}'

# Bulk notify buyers
curl -X POST http://localhost:8000/api/notifications/bulk_send \
  -H "Content-Type: application/json" \
  -d '{"template":"price_change","recipient_list":["buyer1","buyer2"],"effective_date":"2026-06-01","session_id":"test"}'

# Warehouse reallocation
curl -X POST http://localhost:8000/api/warehouse/reallocation \
  -H "Content-Type: application/json" \
  -d '{"source_warehouse_id":"WH-1","target_warehouse_id":"WH-2","sku_list":["SKU-001","SKU-002"],"session_id":"test"}'
```

### Mock API — Business

```bash
# Create CRM campaign
curl -X POST http://localhost:8000/api/crm/campaigns/create \
  -H "Content-Type: application/json" \
  -d '{"region":"Lahore","discount_pct":10.0,"target_segment":"premium","duration_days":14,"budget_pkr":500000,"session_id":"test"}'

# Update catalog pricing
curl -X POST http://localhost:8000/api/catalog/pricing/update \
  -H "Content-Type: application/json" \
  -d '{"region":"Karachi","category":"electronics","price_delta_pct":3.5,"effective_date":"2026-06-01","session_id":"test"}'

# Trigger CRM retention workflow
curl -X POST http://localhost:8000/api/crm/workflows/trigger \
  -H "Content-Type: application/json" \
  -d '{"workflow_id":"WF-CHURN-01","segment":"at_risk","message_template":"retention_offer","session_id":"test"}'
```

### Mock API — Finance

```bash
# Book FX hedge
curl -X POST http://localhost:8000/api/finance/hedging/book \
  -H "Content-Type: application/json" \
  -d '{"currency_pair":"USD/PKR","amount_usd":100000,"duration_days":90,"rate":278.5,"session_id":"test"}'

# Flag portfolio for rebalance
curl -X POST http://localhost:8000/api/portfolio/rebalance/flag \
  -H "Content-Type: application/json" \
  -d '{"affected_instruments":["ENGRO","PSO"],"reason":"rate_shock","urgency":"high","session_id":"test"}'
```

### Mock API — Healthcare

```bash
# Place emergency procurement order
curl -X POST http://localhost:8000/api/procurement/emergency_order \
  -H "Content-Type: application/json" \
  -d '{"item_id":"DRUG-001","quantity":5000,"urgency":"critical","supplier_shortlist":["SupplierA","SupplierB"],"session_id":"test"}'

# Send clinical staff alert
curl -X POST http://localhost:8000/api/notifications/clinical_alert \
  -H "Content-Type: application/json" \
  -d '{"alert_type":"shortage","affected_drug_or_procedure":"Paracetamol","guidance":"use alternative","recipients":["dr.ali","dr.sara"],"session_id":"test"}'
```

### Mock API — Urban

```bash
# Dispatch repair crew
curl -X POST http://localhost:8000/api/operations/dispatch \
  -H "Content-Type: application/json" \
  -d '{"fault_location":"Gulberg Grid","crew_type":"electrical","priority":"urgent","eta_minutes":25,"session_id":"test"}'

# Publish public advisory
curl -X POST http://localhost:8000/api/communications/public_advisory \
  -H "Content-Type: application/json" \
  -d '{"zone_id":"Z-03","issue_type":"power_outage","severity":"high","guidance_text":"Avoid area","channels":["sms","twitter"],"session_id":"test"}'
```

---

## How the Pipeline Works

```
Step 1 — INPUT PARSING
  The raw input (text / URL / file) is passed to the matching parser.
  Output: { clean_text, word_count, source_type, ... }

Step 2 — SESSION CREATED
  A new AnalysisSession row is inserted (status: pending).

Step 3 — DOMAIN DETECTION
  detect_domain() scores the clean_text against keyword lists for all
  6 domains and returns the best match.

Step 4 — TASK PLAN
  Orchestrator records which agents will run, in what order, with what
  model. Saved as an AgentArtifact.

Step 5 — PARALLEL: Ingestion + Research
  IngestionAgent: extracts facts, entities, numbers, confidence.
  ResearchAgent:  verifies credibility, adds Pakistan-specific context.
  Both run with asyncio.gather() — no sequential wait.

Step 6 — SEQUENTIAL: Analysis
  AnalysisAgent:  maps facts → domain KPIs, scores severity 1-10,
  quantifies financial impact in PKR.

Step 7 — SEQUENTIAL: Decision
  DecisionAgent:  selects top-3 ranked actions from a domain catalogue,
  scores each on feasibility × impact, builds complete API payloads.

Step 8 — MERGE
  Orchestrator.merge_artifacts() combines all four outputs into a single
  master_brief dict — pure Python, no LLM call.

Step 9 — EXECUTION
  ExecutionAgent: reads state_before, calls the top action's Mock API
  endpoint, reads state_after, computes delta, sends notification log.

Step 10 — RESPONSE
  Final JSON returned with insight, severity, KPIs, actions, state
  delta, notifications, and a trace URL.
```

---

## Quick Test

```bash
curl -s -X POST http://localhost:8000/api/analyse/text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Pakistan State Oil reports fuel prices have surged 18% this week following a PKR devaluation. Logistics companies across Lahore and Karachi are facing increased delivery costs. Several carriers have paused new shipment agreements pending a pricing review."
  }' | python -m json.tool
```

Expected response keys: `session_id`, `domain` (`logistics`), `severity`, `severity_label`, `insight`, `top_action`, `before_state`, `after_state`, `delta`, `trace_url`.

---

## Supported Domains

| Domain | What It Analyses |
|---|---|
| **logistics** | Fuel prices, shipment costs, route efficiency, warehouse load, carrier disruptions |
| **business** | Revenue trends, customer churn, regional sales, CRM campaigns, SKU pricing |
| **finance** | PKR/USD rates, KSE movements, FX exposure, portfolio risk, SBP policy |
| **policy** | OGRA/SECP/SBP regulations, gazette notifications, compliance deadlines, duty changes |
| **healthcare** | Drug shortages, DRAP advisories, WHO alerts, formulary changes, procurement gaps |
| **urban** | Power outages (LESCO/WAPDA), water faults (WASA), traffic disruptions, CDA zone issues |

---

## Agent Descriptions

| Agent | Model | Role |
|---|---|---|
| **IngestionAgent** | gemini-1.5-flash | Extracts facts, entities, numbers, and directional signals from raw content |
| **ResearchAgent** | gemini-1.5-flash | Verifies credibility against Pakistan business context, flags contradictions |
| **AnalysisAgent** | gemini-1.5-flash | Maps signals to domain KPIs, scores severity 1–10, quantifies PKR impact |
| **DecisionAgent** | gemini-1.5-pro | Selects and ranks top-3 actions from domain catalogues with full API payloads |
| **ExecutionAgent** | — | Calls Mock API endpoints, captures state delta, sends notification log |
| **Orchestrator** | gemini-1.5-pro | Coordinates all agents, merges outputs, saves artifacts to PostgreSQL |

---

## Mock API State Reset

After running the pipeline, domain states are mutated (e.g. fuel ratios change, campaigns are created). To restore all domains to their default values:

```bash
curl -X POST http://localhost:8000/api/state/reset
```

To inspect the current state of a specific domain before/after a pipeline run:

```bash
# Before
curl http://localhost:8000/api/state/logistics

# Run pipeline...

# After
curl http://localhost:8000/api/state/logistics
```

---

## Project Structure

```
newsops/
├── main.py                  # FastAPI app, lifespan, router wiring
├── config.py                # Models, domains, severity labels, env vars
├── requirements.txt
├── .env.example
├── agents/
│   ├── orchestrator.py      # Orchestrator class — pipeline coordinator
│   ├── ingestion_agent.py   # Signal extraction via LLM
│   ├── analysis_agent.py    # KPI impact analysis via LLM
│   ├── decision_agent.py    # Action ranking via LLM
│   ├── research_agent.py    # Context & credibility via LLM
│   └── execution_agent.py   # Mock API caller, state delta
├── pipelines/
│   └── pipeline.py          # run_pipeline() — parse → session → orchestrate
├── parsers/
│   ├── text_parser.py
│   ├── pdf_parser.py
│   ├── docx_parser.py
│   ├── csv_parser.py
│   └── excel_parser.py
├── routers/
│   ├── analysis.py          # POST /api/analyse/*
│   ├── session.py           # GET  /api/session/*
│   └── state.py             # GET/POST /api/state/*
├── mock_api/
│   ├── state_store.py       # In-memory domain state (numeric)
│   └── endpoints.py         # 30 mock action endpoints at /api/*
├── database/
│   ├── db.py                # Async SQLAlchemy engine + get_db()
│   └── models.py            # AnalysisSession, AgentArtifact, StateLog
├── schemas/
│   ├── input_schemas.py     # TextAnalysisRequest, UrlAnalysisRequest, FileAnalysisRequest
│   └── output_schemas.py    # AnalysisResponse, TraceResponse, and sub-models
└── utils/
    ├── helpers.py            # generate_uuid, now_iso, detect_domain, compute_delta
    └── logger.py             # SessionLogger (structured JSON to stdout)
```
