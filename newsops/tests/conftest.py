import asyncio
import io
import os
import sys
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport

# ── Path & env setup (must happen before project imports) ────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "AIzaSy_mock_gemini_api_key_placeholder"))
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_newsops.db")
os.environ.setdefault("DEBUG", "true")

from main import app  # noqa: E402 — env vars must be set first
from database.db import create_tables  # noqa: E402
from mock_api.state_store import reset_state  # noqa: E402

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ── DB setup ─────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    await create_tables()
    yield
    db_path = Path("test_newsops.db")
    if db_path.exists():
        db_path.unlink(missing_ok=True)


# ── HTTP client ───────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── State reset between tests ─────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_mock_state():
    reset_state()
    yield
    reset_state()


# ── Sample data fixtures ──────────────────────────────────────────────────────
@pytest.fixture
def sample_text():
    return (FIXTURES_DIR / "sample.txt").read_text()


@pytest.fixture
def sample_csv_bytes():
    return (FIXTURES_DIR / "sample.csv").read_bytes()


@pytest.fixture
def sample_pdf_bytes():
    pdf_path = FIXTURES_DIR / "sample.pdf"
    if not pdf_path.exists():
        pytest.skip("sample.pdf not found — run tests/fixtures/generate_fixtures.py first")
    return pdf_path.read_bytes()


@pytest.fixture
def sample_docx_bytes():
    docx_path = FIXTURES_DIR / "sample.docx"
    if not docx_path.exists():
        pytest.skip("sample.docx not found — run tests/fixtures/generate_fixtures.py first")
    return docx_path.read_bytes()


@pytest.fixture
def sample_excel_bytes():
    import pandas as pd
    df = pd.read_csv(FIXTURES_DIR / "sample.csv")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Sales Data", index=False)
        df.groupby("region").sum(numeric_only=True).to_excel(
            writer, sheet_name="Summary", index=True
        )
    return buf.getvalue()


@pytest.fixture
def session_id():
    from utils.helpers import generate_uuid
    return generate_uuid()
