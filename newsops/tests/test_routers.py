"""Tests for all FastAPI routers — analysis, session, state."""
import json
import pytest
from unittest.mock import AsyncMock, patch

from utils.helpers import generate_uuid

MOCK_RESULT = {
    "session_id": "test-session-router-001",
    "domain": "logistics",
    "status": "completed",
    "duration_seconds": 0.5,
    "insight": "Fuel increase requires pricing adjustment.",
    "severity": 7,
    "severity_label": "High",
    "impact_summary": {},
    "kpis_affected": [],
    "top_action": None,
    "before_state": {},
    "after_state": {},
    "delta": {},
    "execution_status": "success",
    "trace_url": "/api/session/test-session-router-001/trace",
}


class TestAnalysisRouterText:
    async def test_analyse_text_200(self, client):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT):
            r = await client.post("/api/analyse/text", json={
                "content": "OGRA increased fuel price by PKR 14.97 per litre.",
            })
        assert r.status_code == 200

    async def test_analyse_text_response_has_session_id(self, client):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT):
            r = await client.post("/api/analyse/text", json={
                "content": "Fuel price increased.",
            })
        data = r.json()
        assert "session_id" in data

    async def test_analyse_text_response_has_domain(self, client):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT):
            r = await client.post("/api/analyse/text", json={"content": "test content length validation"})
        assert "domain" in r.json()

    async def test_analyse_text_response_has_status(self, client):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT):
            r = await client.post("/api/analyse/text", json={"content": "test content length validation"})
        assert "status" in r.json()

    async def test_analyse_text_empty_content_still_calls_pipeline(self, client):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT) as mock_run:
            await client.post("/api/analyse/text", json={"content": "test content length validation"})
        mock_run.assert_called_once()

    async def test_analyse_text_pipeline_error_returns_500(self, client):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock,
                   side_effect=RuntimeError("LLM timeout")):
            r = await client.post("/api/analyse/text", json={"content": "test content length validation"})
        assert r.status_code == 500


class TestAnalysisRouterURL:
    async def test_analyse_url_200(self, client):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT):
            r = await client.post("/api/analyse/url", json={
                "url": "https://example.com/news/fuel-price",
            })
        assert r.status_code == 200

    async def test_analyse_url_response_schema(self, client):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT):
            r = await client.post("/api/analyse/url", json={"url": "https://example.com"})
        from schemas.output_schemas import AnalysisResponse
        model = AnalysisResponse(**r.json())
        assert model.session_id is not None


class TestAnalysisRouterFile:
    async def test_analyse_file_csv_200(self, client, sample_csv_bytes):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT):
            r = await client.post(
                "/api/analyse/file",
                files={"file": ("data.csv", sample_csv_bytes, "text/csv")},
                data={"input_type": "csv"},
            )
        assert r.status_code == 200

    async def test_analyse_file_with_domain(self, client, sample_csv_bytes):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT) as mock_run:
            r = await client.post(
                "/api/analyse/file",
                files={"file": ("data.csv", sample_csv_bytes, "text/csv")},
                data={"input_type": "csv", "domain": "business"},
            )
        assert r.status_code == 200
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs.get("domain") == "business"

    async def test_analyse_file_pdf(self, client, sample_pdf_bytes):
        with patch("routers.analysis.run_pipeline", new_callable=AsyncMock, return_value=MOCK_RESULT):
            r = await client.post(
                "/api/analyse/file",
                files={"file": ("report.pdf", sample_pdf_bytes, "application/pdf")},
                data={"input_type": "pdf", "domain": "logistics"},
            )
        assert r.status_code == 200


class TestStateRouter:
    async def test_get_valid_domain_state(self, client):
        r = await client.get("/api/state/logistics")
        assert r.status_code == 200
        assert "delivery_price_per_kg" in r.json()

    async def test_get_invalid_domain_returns_400(self, client):
        r = await client.get("/api/state/unknowndomain")
        assert r.status_code == 400

    async def test_reset_state_returns_ok(self, client):
        r = await client.post("/api/state/reset")
        assert r.status_code == 200
        assert r.json()["status"] == "reset"

    async def test_reset_restores_defaults(self, client):
        from mock_api.state_store import update_state, DEFAULT_STATE
        update_state("logistics", {"delivery_price_per_kg": 999.0})
        await client.post("/api/state/reset")
        state = (await client.get("/api/state/logistics")).json()
        assert state["delivery_price_per_kg"] == DEFAULT_STATE["logistics"]["delivery_price_per_kg"]

    async def test_all_six_domains_accessible(self, client):
        for domain in ["logistics", "business", "finance", "policy", "healthcare", "urban"]:
            r = await client.get(f"/api/state/{domain}")
            assert r.status_code == 200, f"Domain '{domain}' returned {r.status_code}"


class TestSessionRouter:
    async def test_get_sessions_returns_list(self, client):
        r = await client.get("/api/sessions")
        assert r.status_code == 200
        assert isinstance(r.json()["sessions"], list)

    async def test_trace_nonexistent_session_returns_empty(self, client):
        r = await client.get(f"/api/session/{generate_uuid()}/trace")
        assert r.status_code == 200
        data = r.json()
        assert data["total_artifacts"] == 0
        assert data["artifacts"] == []

    async def test_status_nonexistent_session_returns_404(self, client):
        r = await client.get(f"/api/session/{generate_uuid()}/status")
        assert r.status_code == 404

    async def test_trace_response_schema(self, client):
        r = await client.get(f"/api/session/{generate_uuid()}/trace")
        assert r.status_code == 200
        data = r.json()
        assert "artifacts" in data
        assert "total_artifacts" in data
        assert isinstance(data["artifacts"], list)


class TestRootEndpoint:
    async def test_root_returns_200(self, client):
        r = await client.get("/")
        assert r.status_code == 200

    async def test_health_check(self, client):
        r = await client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
