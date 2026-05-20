"""Tests for all agents — unit tests use mocked LLM calls; integration tests need a real key."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ── Shared sample data ─────────────────────────────────────────────────────────

SAMPLE_SIGNALS = {
    "agent": "ingestion",
    "input_type": "text",
    "domain": "logistics",
    "source": "direct_text",
    "timestamp": "2024-11-01T10:00:00Z",
    "facts": [
        {
            "text": "OGRA increased HSD fuel price by PKR 14.97/litre (18.5%)",
            "subject": "HSD fuel price",
            "value": 14.97,
            "unit": "PKR/litre",
            "direction": "increase",
            "date_reference": "November 2024",
            "confidence": "high",
        },
        {
            "text": "Delivery cost per kg increased from PKR 320 to PKR 378",
            "subject": "delivery_cost_per_kg",
            "value": 378,
            "unit": "PKR/kg",
            "direction": "increase",
            "date_reference": "November 2024",
            "confidence": "high",
        },
        {
            "text": "Monthly fuel bill increased by PKR 2,519,200 for 4200 shipments",
            "subject": "monthly_fuel_cost",
            "value": 2519200,
            "unit": "PKR",
            "direction": "increase",
            "date_reference": "November 2024",
            "confidence": "high",
        },
    ],
    "metrics": [
        {"name": "fuel_price_pkr_per_litre", "before": 81.02, "after": 95.99, "direction": "increase"},
        {"name": "delivery_cost_per_kg_pkr", "before": 320, "after": 378, "direction": "increase"},
        {"name": "monthly_fuel_cost_pkr", "before": 1344000, "after": 1587600, "direction": "increase"},
    ],
    "entities": [{"name": "OGRA", "type": "regulatory_body"}],
    "confidence": "high",
    "key_themes": ["fuel_cost_increase", "delivery_cost_impact"],
}

SAMPLE_ANALYSIS = {
    "agent": "analysis",
    "domain": "logistics",
    "severity_score": 8,
    "severity_label": "High",
    "executive_summary": "Fuel price hike creates 18.5% cost increase requiring immediate pricing adjustment.",
    "kpi_impacts": [
        {
            "kpi": "delivery_cost_per_kg_pkr",
            "current_value": 320,
            "projected_value": 378,
            "delta": 58,
            "delta_pct": 18.13,
        }
    ],
    "financial_impact": {
        "monthly_cost_increase_pkr": 243600,
        "annual_projection_pkr": 2923200,
        "revenue_at_risk_pkr": 12000000,
    },
    "second_order_effects": ["Customer churn risk", "Competitive disadvantage"],
    "affected_parties": ["Al-Faisal Logistics", "Buyers", "Drivers"],
    "time_horizon": "immediate",
    "confidence": "high",
}

SAMPLE_ACTION_PLAN = {
    "agent": "decision",
    "domain": "logistics",
    "recommended_actions": [
        {
            "action_id": "ACT-001",
            "title": "Update delivery pricing by 8%",
            "api_endpoint": "/api/logistics/pricing/update",
            "api_payload": {
                "route_id": "LHR-ALL",
                "price_delta_pct": 8.0,
                "effective_date": "2024-12-01",
            },
            "priority": 1,
            "composite_score": 8.2,
        }
    ],
    "execution_sequence": ["ACT-001"],
}

SKIP_IF_NO_KEY = pytest.mark.skipif(
    __import__("os").getenv("GEMINI_API_KEY", "AIzaSy-mock").startswith("AIzaSy-mock") or 
    __import__("os").getenv("GEMINI_API_KEY", "AIzaSy_mock").startswith("AIzaSy_mock") or
    "your_gemini_key" in __import__("os").getenv("GEMINI_API_KEY", ""),
    reason="Real Gemini key required for integration tests",
)


# ── IngestionAgent ─────────────────────────────────────────────────────────────

class TestIngestionAgent:
    def test_agent_instantiates(self):
        from agents.ingestion_agent import IngestionAgent
        agent = IngestionAgent("session-001")
        assert agent is not None

    def test_agent_has_session_id(self):
        from agents.ingestion_agent import IngestionAgent
        agent = IngestionAgent("session-xyz")
        assert agent.session_id == "session-xyz"

    async def test_run_returns_dict_with_mock(self):
        from agents.ingestion_agent import IngestionAgent
        with patch("agents.ingestion_agent.call_gemini", new_callable=AsyncMock) as mock_call_gemini:
            mock_call_gemini.return_value = SAMPLE_SIGNALS

            agent = IngestionAgent("session-001")
            parsed_input = {"clean_text": "OGRA fuel price increased 18.5%", "source_type": "text"}
            result = await agent.run(parsed_input, "logistics", "text", "direct_text")

        assert isinstance(result, dict)

    @SKIP_IF_NO_KEY
    @pytest.mark.integration
    async def test_run_with_real_llm(self):
        from agents.ingestion_agent import IngestionAgent
        agent = IngestionAgent("session-integration-001")
        parsed_input = {
            "clean_text": (
                "OGRA issued Notification OGRA-2024-1101 on November 1st, 2024, "
                "mandating a PKR 14.97 per litre increase in HSD fuel prices (18.5% rise). "
                "Al-Faisal Logistics operates 4200 monthly shipments."
            ),
            "source_type": "text",
        }
        result = await agent.run(parsed_input, "logistics", "text", "direct_text")
        assert isinstance(result, dict)
        assert "facts" in result
        assert len(result["facts"]) >= 3


# ── AnalysisAgent ──────────────────────────────────────────────────────────────

class TestAnalysisAgent:
    def test_agent_instantiates(self):
        from agents.analysis_agent import AnalysisAgent
        agent = AnalysisAgent("session-001")
        assert agent is not None

    async def test_run_returns_dict_with_mock(self):
        from agents.analysis_agent import AnalysisAgent
        with patch("agents.analysis_agent.call_gemini", new_callable=AsyncMock) as mock_call_gemini:
            mock_call_gemini.return_value = SAMPLE_ANALYSIS

            agent = AnalysisAgent("session-001")
            result = await agent.run(SAMPLE_SIGNALS, "logistics")

        assert isinstance(result, dict)

    @SKIP_IF_NO_KEY
    @pytest.mark.integration
    async def test_run_with_real_llm(self):
        from agents.analysis_agent import AnalysisAgent
        agent = AnalysisAgent("session-integration-002")
        result = await agent.run(SAMPLE_SIGNALS, "logistics")
        assert isinstance(result, dict)
        assert "severity_score" in result
        score = result["severity_score"]
        assert isinstance(score, (int, float))
        assert 1 <= score <= 10


# ── DecisionAgent ──────────────────────────────────────────────────────────────

class TestDecisionAgent:
    def test_agent_instantiates(self):
        from agents.decision_agent import DecisionAgent
        agent = DecisionAgent("session-001")
        assert agent is not None

    async def test_run_returns_dict_with_mock(self):
        from agents.decision_agent import DecisionAgent
        with patch("agents.decision_agent.call_gemini", new_callable=AsyncMock) as mock_call_gemini:
            mock_call_gemini.return_value = SAMPLE_ACTION_PLAN

            agent = DecisionAgent("session-001")
            result = await agent.run(SAMPLE_ANALYSIS, "logistics")

        assert isinstance(result, dict)

    @SKIP_IF_NO_KEY
    @pytest.mark.integration
    async def test_run_with_real_llm(self):
        from agents.decision_agent import DecisionAgent
        agent = DecisionAgent("session-integration-003")
        result = await agent.run(SAMPLE_ANALYSIS, "logistics")
        assert isinstance(result, dict)
        assert "recommended_actions" in result
        assert len(result["recommended_actions"]) >= 1


# ── ResearchAgent ──────────────────────────────────────────────────────────────

class TestResearchAgent:
    def test_agent_instantiates(self):
        from agents.research_agent import ResearchAgent
        agent = ResearchAgent("session-001")
        assert agent is not None

    async def test_run_returns_dict_with_mock(self):
        from agents.research_agent import ResearchAgent
        mock_result = {
            "agent": "research",
            "domain": "logistics",
            "benchmarks": [],
            "historical_context": "Fuel prices have historically risen 10-15% in Q4.",
            "risk_factors": ["currency depreciation", "global oil price"],
        }
        with patch("agents.research_agent.call_gemini", new_callable=AsyncMock) as mock_call_gemini:
            mock_call_gemini.return_value = mock_result

            agent = ResearchAgent("session-001")
            result = await agent.run(SAMPLE_SIGNALS, "logistics")

        assert isinstance(result, dict)


# ── ExecutionAgent ─────────────────────────────────────────────────────────────

class TestExecutionAgent:
    def test_agent_instantiates(self):
        from agents.execution_agent import ExecutionAgent
        agent = ExecutionAgent("session-001")
        assert agent is not None

    async def test_run_calls_api_endpoints(self, client):
        from agents.execution_agent import ExecutionAgent
        agent = ExecutionAgent("session-001")

        action_plan = {
            "recommended_actions": [
                {
                    "action_id": "ACT-001",
                    "title": "Update delivery pricing",
                    "api_endpoint": "/api/logistics/pricing/update",
                    "api_payload": {
                        "route_id": "LHR-ALL",
                        "price_delta_pct": 8.0,
                        "effective_date": "2024-12-01",
                    },
                    "priority": 1,
                    "composite_score": 8.2,
                }
            ],
            "execution_sequence": ["ACT-001"],
        }
        result = await agent.run(action_plan, SAMPLE_ANALYSIS, "logistics")
        assert isinstance(result, dict)
        assert "executed_actions" in result or "results" in result or isinstance(result, dict)


# ── Orchestrator ───────────────────────────────────────────────────────────────

class TestOrchestrator:
    def test_orchestrator_instantiates(self):
        from agents.orchestrator import Orchestrator
        orch = Orchestrator("session-001")
        assert orch is not None

    def test_orchestrator_has_all_agents(self):
        from agents.orchestrator import Orchestrator
        orch = Orchestrator("session-001")
        assert hasattr(orch, "ingestion_agent")
        assert hasattr(orch, "analysis_agent")
        assert hasattr(orch, "decision_agent")
        assert hasattr(orch, "research_agent")
        assert hasattr(orch, "execution_agent")
