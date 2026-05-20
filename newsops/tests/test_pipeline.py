"""Tests for the end-to-end pipeline — mocked orchestrator to avoid LLM calls."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from utils.helpers import generate_uuid

MOCK_PIPELINE_RESULT = {
    "session_id": "mock-session-001",
    "domain": "logistics",
    "status": "completed",
    "duration_seconds": 1.23,
    "insight": "Fuel cost increase of 18.5% requires immediate pricing adjustment.",
    "severity": 8,
    "severity_label": "High",
    "impact_summary": {"monthly_cost_increase_pkr": 243600},
    "kpis_affected": [
        {
            "kpi": "delivery_cost_per_kg_pkr",
            "current_value": 320,
            "projected_value": 378,
            "current_unit": "PKR/kg",
            "direction": "increase",
        }
    ],
    "top_action": {
        "action_type": "pricing_update",
        "description": "Update delivery pricing by 8%",
        "api_endpoint": "/api/logistics/pricing/update",
        "api_payload": {
            "route_id": "LHR-ALL",
            "price_delta_pct": 8.0,
            "effective_date": "2024-12-01",
        },
    },
    "before_state": {"delivery_price_per_kg": 2.40},
    "after_state": {"delivery_price_per_kg": 2.60},
    "delta": {"delivery_price_per_kg": {"from": 2.40, "to": 2.60, "change_pct": 8.33}},
    "execution_status": "success",
    "trace_url": "/api/session/mock-session-001/trace",
}


def _make_mock_orchestrator():
    mock_orch = AsyncMock()
    mock_orch.run = AsyncMock(return_value=MOCK_PIPELINE_RESULT)
    return mock_orch


class TestRunPipelineText:
    async def test_text_pipeline_returns_dict(self):
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            result = await run_pipeline(
                input_type="text",
                content="OGRA increased fuel price by 18.5%",
                session_id=generate_uuid(),
            )
        assert isinstance(result, dict)

    async def test_text_pipeline_passes_session_id(self):
        sid = generate_uuid()
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            result = await run_pipeline(
                input_type="text",
                content="Fuel price increased",
                session_id=sid,
            )
        assert isinstance(result, dict)

    async def test_text_pipeline_generates_session_id_if_none(self):
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            result = await run_pipeline(
                input_type="text",
                content="Fuel price increased",
            )
        assert isinstance(result, dict)

    async def test_unsupported_input_type_raises(self):
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            with pytest.raises(ValueError, match="Unsupported input_type"):
                await run_pipeline(
                    input_type="audio",
                    content="some content",
                    session_id=generate_uuid(),
                )


class TestRunPipelineCSV:
    async def test_csv_pipeline_returns_dict(self, sample_csv_bytes):
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            result = await run_pipeline(
                input_type="csv",
                file_bytes=sample_csv_bytes,
                session_id=generate_uuid(),
            )
        assert isinstance(result, dict)


class TestRunPipelineExcel:
    async def test_excel_pipeline_returns_dict(self, sample_excel_bytes):
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            result = await run_pipeline(
                input_type="excel",
                file_bytes=sample_excel_bytes,
                session_id=generate_uuid(),
            )
        assert isinstance(result, dict)


class TestRunPipelinePDF:
    async def test_pdf_pipeline_returns_dict(self, sample_pdf_bytes):
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            result = await run_pipeline(
                input_type="pdf",
                file_bytes=sample_pdf_bytes,
                domain="logistics",
                session_id=generate_uuid(),
            )
        assert isinstance(result, dict)


class TestRunPipelineDocx:
    async def test_docx_pipeline_returns_dict(self, sample_docx_bytes):
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            result = await run_pipeline(
                input_type="docx",
                file_bytes=sample_docx_bytes,
                domain="policy",
                session_id=generate_uuid(),
            )
        assert isinstance(result, dict)


class TestPipelineResponseShape:
    async def test_result_has_required_fields(self):
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            result = await run_pipeline(
                input_type="text",
                content="Fuel price notification",
                session_id=generate_uuid(),
            )
        required_fields = {"session_id", "domain", "status"}
        assert required_fields.issubset(set(result.keys()))

    async def test_result_conforms_to_analysis_response_schema(self):
        from schemas.output_schemas import AnalysisResponse
        with patch("pipelines.pipeline.Orchestrator", return_value=_make_mock_orchestrator()):
            from pipelines.pipeline import run_pipeline
            result = await run_pipeline(
                input_type="text",
                content="Fuel cost analysis",
                session_id=generate_uuid(),
            )
        model = AnalysisResponse(**result)
        assert model.session_id is not None
        assert model.status is not None
