from collections import defaultdict
from contextlib import asynccontextmanager
from time import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import ALLOWED_ORIGINS, APP_HOST, APP_PORT, GEMINI_API_KEY
from database.db import create_tables
from routers import analysis, session, state
from mock_api import endpoints as mock_api


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
    yield

app = FastAPI(
    title="NewsOps Intelligence API",
    version="1.0.0",
    description="Autonomous multi-agent content-to-action intelligence system",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — analysis and session/state registered first so they win on overlap
app.include_router(analysis.router)
app.include_router(session.router)
app.include_router(state.router)
app.include_router(mock_api.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "NewsOps", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check():
    from utils.helpers import now_iso
    return {"status": "ok", "service": "NewsOps", "version": "1.0.0", "timestamp": now_iso()}


if __name__ == "__main__":
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)
