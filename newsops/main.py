from collections import defaultdict
from contextlib import asynccontextmanager
from time import time

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import ALLOWED_ORIGINS, APP_API_KEY, APP_HOST, APP_PORT, GEMINI_API_KEY
from database.db import create_tables
from routers import analysis, session, state, alerts, outcomes, org
from mock_api import endpoints as mock_api
from utils.commentary_stream import create_stream, active_streams, close_stream
from database.models import get_session


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-process rate limiter: 60 requests per IP per minute."""

    def __init__(self, app, calls: int = None, period: int = 60):
        super().__init__(app)
        import os
        self.calls = calls if calls is not None else int(os.getenv("RATE_LIMIT_CALLS", "60"))
        self.period = period
        self._store: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time()
        timestamps = self._store[ip]
        timestamps[:] = [t for t in timestamps if now - t < self.period]
        if len(timestamps) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please slow down."},
            )
        timestamps.append(now)
        return await call_next(request)


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Optional X-API-Key guard.

    Active only when APP_API_KEY is set in the environment.  Health-check
    endpoints (/ and /health) are always allowed through so infrastructure
    probes never need a key.
    """

    # Paths that bypass the API-key check.
    _EXEMPT = {"/", "/health"}

    async def dispatch(self, request: Request, call_next):
        if APP_API_KEY is None:
            # Key guard disabled — local dev mode, pass through.
            return await call_next(request)

        if request.url.path in self._EXEMPT:
            return await call_next(request)

        provided = request.headers.get("X-API-Key", "")
        if provided != APP_API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid X-API-Key header."},
            )
        return await call_next(request)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key_here" or GEMINI_API_KEY.startswith("AIzaSy_mock"):
        print("\n" + "=" * 80)
        print("WARNING: GEMINI_API_KEY IS NOT SET OR IS SET TO DEFAULT PLACEHOLDER.")
        print("STARTING UP IN OFFLINE / MOCK DEMO MODE.")
        print("All multi-agent pipelines will return high-fidelity mock responses.")
        print("=" * 80 + "\n")
    else:
        print("\n" + "=" * 80)
        print("NEWS_OPS AGENT PIPELINE RUNNING ON LIVE GEMINI API KEYS")
        print("=" * 80 + "\n")
    await create_tables()

    # Monthly reset check
    from database.db import get_db
    from database.models import Config, Organisation
    from sqlalchemy import select, update
    from datetime import datetime, timezone
    
    async with get_db() as db:
        now_month = datetime.now(timezone.utc).strftime("%Y-%m")
        res = await db.execute(select(Config).where(Config.key == "last_reset_month"))
        config_entry = res.scalar_one_or_none()
        
        if not config_entry:
            db.add(Config(key="last_reset_month", value=now_month))
            await db.commit()
        elif config_entry.value != now_month:
            await db.execute(update(Organisation).values(monthly_analysis_count=0))
            config_entry.value = now_month
            await db.commit()

    try:
        from utils.seed_knowledge import seed_if_needed
        seed_if_needed()
    except Exception as se:
        print(f"Error seeding knowledge database: {se}")
    yield

app = FastAPI(
    title="NewsOps Intelligence API",
    version="1.0.0",
    description="Autonomous multi-agent content-to-action intelligence system",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(ApiKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,   # web + mobile don't use cookies; False allows wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — analysis and session/state registered first so they win on overlap
app.include_router(analysis.router)
app.include_router(session.router)
app.include_router(state.router)
app.include_router(alerts.router)
app.include_router(outcomes.router)
app.include_router(org.router, prefix="/api/org")
app.include_router(mock_api.router)

from config import DEBUG
if DEBUG:
    from routers import debug
    app.include_router(debug.router, prefix="/api/debug")



@app.websocket("/ws/session/{session_id}")
async def websocket_session(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Check if session is already complete in DB
    session_data = await get_session(session_id)
    is_complete = session_data and session_data.get("status") == "complete"
    
    queue = active_streams.get(session_id)
    if not queue:
        queue = create_stream(session_id)
        
    try:
        while True:
            # If session is complete and queue is empty, we can exit
            if is_complete and queue.empty():
                break
                
            msg = await queue.get()
            if msg.get("close"):
                break
            await websocket.send_json(msg)
            queue.task_done()
    except WebSocketDisconnect:
        pass
    finally:
        # Optional: clean up stream if disconnected and no agents are writing anymore
        # But for safety, we keep it alive unless explicitly closed by execution_agent
        pass



@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "NewsOps", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check():
    from utils.helpers import now_iso
    return {"status": "ok", "service": "NewsOps", "version": "1.0.0", "timestamp": now_iso()}


if __name__ == "__main__":
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)
