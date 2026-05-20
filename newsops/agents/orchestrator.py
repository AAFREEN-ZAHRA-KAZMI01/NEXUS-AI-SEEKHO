import asyncio
import time

from config import MODELS
from utils.helpers import now_iso, detect_domain
from utils.logger import SessionLogger
from database.models import save_artifact, update_session_status, save_state_log, save_session
from agents.ingestion_agent import IngestionAgent
from agents.analysis_agent import AnalysisAgent
from agents.decision_agent import DecisionAgent
from agents.research_agent import ResearchAgent
from agents.execution_agent import ExecutionAgent


class Orchestrator:
    def __init__(self, *args, **kwargs):
        self.ingestion = IngestionAgent()
        self.analysis = AnalysisAgent()
        self.decision = DecisionAgent()
        self.research = ResearchAgent()
        self.execution = ExecutionAgent()
        
        # Compatibility aliases for test suite expectations
        self.ingestion_agent = self.ingestion
        self.analysis_agent = self.analysis
        self.decision_agent = self.decision
        self.research_agent = self.research
        self.execution_agent = self.execution

    def detect_domain(self, text: str) -> str:
        return detect_domain(text)

    def build_task_plan(self, session_id, domain, input_type, _parsed_input) -> dict:
        return {
            "agent": "orchestrator",
            "session_id": session_id,
            "timestamp": now_iso(),
            "input_type": input_type,
            "domain": domain,
            "agents_to_spawn": ["ingestion", "research", "analysis", "decision", "execution"],
            "parallel_group_1": ["ingestion", "research"],
            "sequential_after_ingestion": ["analysis"],
            "sequential_after_analysis": ["decision"],
            "final_step": "execution",
            "estimated_duration_seconds": 30,
            "orchestrator_model": MODELS["orchestrator"],
            "agent_models": {
                "ingestion":  MODELS["ingestion"],
                "analysis":   MODELS["analysis"],
                "decision":   MODELS["decision"],
                "research":   MODELS["research"],
                "execution":  "python_executor",
            },
            "platform": "Google Antigravity",
        }

    def merge_artifacts(self, session_id, domain, signals, impact, actions, context) -> dict:
        top_action_data = actions["actions"][0] if actions.get("actions") else {}
        kpis = impact.get("kpis_affected", [])
        
        # Map LLM keys to target schema
        mapped_kpis = []
        for k in kpis:
            mapped_kpis.append({
                "kpi": k.get("kpi", ""),
                "current_value": k.get("current_value"),
                "projected_value": k.get("projected_value"),
                "current_unit": k.get("current_unit") or k.get("unit"),
                "direction": k.get("direction") or k.get("impact_direction") or "stable",
                "delta": k.get("delta"),
                "delta_pct": k.get("delta_pct")
            })
            
        first_kpi = mapped_kpis[0] if mapped_kpis else {}
        return {
            "agent": "orchestrator",
            "session_id": session_id,
            "domain": domain,
            "timestamp": now_iso(),
            "mock_mode_active": signals.get("mock_mode_active", False),
            "insight": self._extract_insight(signals),
            "severity": impact.get("severity", 5),
            "severity_label": impact.get("severity_label", "Medium"),
            "impact_summary": impact.get("total_impact", {}),
            "kpis_affected": mapped_kpis,
            "top_action": top_action_data,
            "alternative_actions": actions.get("actions", [])[1:3],
            "context": context.get("additional_context", ""),
            "corroboration": context.get("corroboration", "unconfirmed"),
            "ready_for_execution": True,
            "projected_outcome": {
                "metric": first_kpi.get("kpi", ""),
                "current": first_kpi.get("current_value"),
                "projected_30_day": first_kpi.get("projected_value"),
                "recovery_pct": None,
            },
        }

    def _extract_insight(self, signals) -> str:
        insight_str = "No specific facts could be extracted from the input."
        facts = signals.get("facts", [])
        if facts:
            if len(facts) == 1:
                insight_str = f"{facts[0].get('text', '')}."
            else:
                insight_str = f"{facts[0].get('text', '')}. Additionally, {facts[1].get('text', '')}."
        
        if signals.get("mock_mode_active"):
            insight_str = "⚠️ MOCK DATA MODE ACTIVATED: " + insight_str
            
        return insight_str

    async def run(self, parsed_input: dict, input_type: str, session_id: str) -> dict:
        logger = SessionLogger(session_id)
        start_time = time.time()

        domain = self.detect_domain(parsed_input["clean_text"])
        await save_session({
            "id": session_id,
            "domain": domain,
            "input_type": input_type,
            "input_preview": parsed_input["clean_text"][:300],
            "status": "pending",
        })
        await update_session_status(session_id, "ingesting")
        await asyncio.sleep(1.0)
        logger.log("orchestrator", "domain_detected", {"domain": domain})

        task_plan = self.build_task_plan(session_id, domain, input_type, parsed_input)
        await save_artifact(session_id, "orchestrator", "task_plan", task_plan)
        logger.log("orchestrator", "task_plan_created")

        try:
            logger.log("orchestrator", "parallel_start", {"agents": ["ingestion", "research"]})
            signals, context = await asyncio.gather(
                self.ingestion.run(parsed_input, domain, session_id),
                self.research.run(parsed_input, domain, session_id),
            )
            await save_artifact(session_id, "ingestion", "signals", signals)
            await save_artifact(session_id, "research", "context", context)
            logger.log("orchestrator", "parallel_complete")

            await update_session_status(session_id, "researching")
            await asyncio.sleep(1.0) # subtle pause for smooth UI rendering

            await update_session_status(session_id, "analysing")
            await asyncio.sleep(1.0)
            logger.log("orchestrator", "analysis_start")
            impact = await self.analysis.run(signals, domain, session_id)
            await save_artifact(session_id, "analysis", "impact", impact)

            await update_session_status(session_id, "deciding")
            await asyncio.sleep(1.0)
            logger.log("orchestrator", "decision_start")
            actions = await self.decision.run(signals, impact, domain, session_id)
            await save_artifact(session_id, "decision", "actions", actions)

            master_brief = self.merge_artifacts(session_id, domain, signals, impact, actions, context)
            await save_artifact(session_id, "orchestrator", "master_brief", master_brief)
            logger.log("orchestrator", "master_brief_created")

            await update_session_status(session_id, "executing")
            await asyncio.sleep(1.0)
            logger.log("orchestrator", "execution_start")
            exec_log = await self.execution.run(master_brief, session_id)
            await save_artifact(session_id, "execution", "exec_log", exec_log)

            await save_state_log(
                session_id,
                domain,
                exec_log["state_before"],
                exec_log["state_after"],
                master_brief["top_action"].get("action_type", ""),
                exec_log["delta"],
            )

            duration = round(time.time() - start_time, 2)
            await update_session_status(session_id, "complete", duration=duration)
            logger.log("orchestrator", "pipeline_complete", {"duration_seconds": duration})

            return {
                "session_id": session_id,
                "domain": domain,
                "status": "complete",
                "duration_seconds": duration,
                "insight": master_brief["insight"],
                "severity": master_brief["severity"],
                "severity_label": master_brief["severity_label"],
                "impact_summary": master_brief["impact_summary"],
                "kpis_affected": master_brief["kpis_affected"],
                "top_action": master_brief["top_action"],
                "alternative_actions": master_brief["alternative_actions"],
                "before_state": exec_log["state_before"],
                "after_state": exec_log["state_after"],
                "delta": exec_log["delta"],
                "notifications_sent": exec_log["notifications_sent"],
                "execution_status": exec_log["execution_status"],
                "corroboration": master_brief["corroboration"],
                "context": master_brief["context"],
                "trace_url": f"/api/session/{session_id}/trace",
                "artifacts": {
                    "task_plan": task_plan,
                    "signals": signals,
                    "impact": impact,
                    "actions": actions,
                    "context": context,
                    "master_brief": master_brief,
                    "exec_log": exec_log,
                },
            }

        except Exception as e:
            await update_session_status(session_id, "failed", error=str(e))
            logger.log("orchestrator", "pipeline_failed", {"error": str(e)})
            raise
