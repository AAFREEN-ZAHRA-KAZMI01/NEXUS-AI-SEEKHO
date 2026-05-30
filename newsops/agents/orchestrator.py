import asyncio
import time

from config import MODELS
from utils.helpers import now_iso, detect_domain
from utils.logger import SessionLogger
from database.models import save_artifact, update_session_status, save_state_log, save_session, create_action_outcome
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

        # Calculate confidence score and label
        facts = signals.get("facts", [])
        total_facts = len(facts)
        high_facts = sum(1 for f in facts if isinstance(f, dict) and f.get("confidence") == "high")
        medium_facts = sum(1 for f in facts if isinstance(f, dict) and f.get("confidence") == "medium")
        
        if total_facts > 0:
            confidence_score = int((high_facts * 2 + medium_facts * 1) / (total_facts * 2) * 100)
        else:
            confidence_score = 0
            
        overall_conf = signals.get("overall_confidence", "low")
        confidence_label = "High" if overall_conf == "high" else "Medium" if overall_conf == "medium" else "Low"
        
        # Extract conflicts
        source_count = signals.get("source_count", 1)
        conflicts = signals.get("source_conflicts", [])
        conflict_warning = f"{len(conflicts)} conflicting signals detected — confidence reduced" if conflicts else None

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
            "corroboration": str(signals.get("corroboration_count", 0)),
            "confidence_score": confidence_score,
            "confidence_label": confidence_label,
            "source_count": source_count,
            "conflicts_detected": conflicts,
            "conflict_warning": conflict_warning,
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

            await update_session_status(session_id, "analysing")
            logger.log("orchestrator", "analysis_start")
            impact = await self.analysis.run(signals, domain, session_id)
            await save_artifact(session_id, "analysis", "impact", impact)

            await update_session_status(session_id, "deciding")
            logger.log("orchestrator", "decision_start")
            actions = await self.decision.run(signals, impact, domain, session_id)
            await save_artifact(session_id, "decision", "actions", actions)

            master_brief = self.merge_artifacts(session_id, domain, signals, impact, actions, context)
            await save_artifact(session_id, "orchestrator", "master_brief", master_brief)
            logger.log("orchestrator", "master_brief_created")

            # Check and trigger watchlist alerts asynchronously/await
            await check_and_trigger_alerts(master_brief, session_id)

            await update_session_status(session_id, "executing")
            logger.log("orchestrator", "execution_start")
            exec_log = await self.execution.run(master_brief, session_id)
            await save_artifact(session_id, "execution", "exec_log", exec_log)

            # Create ActionOutcome row (user_confirmed=False — user tracks it in the app)
            try:
                top_action = master_brief.get("top_action", {})
                first_kpi = master_brief.get("kpis_affected", [{}])[0] if master_brief.get("kpis_affected") else {}
                # Build a human-readable recommended_delta from the action or KPI delta
                delta_val = top_action.get("recommended_delta") or ""
                if not delta_val:
                    kpi_delta = first_kpi.get("delta_pct")
                    kpi_name_str = first_kpi.get("kpi", "")
                    delta_val = f"{kpi_delta:+.1f}% on {kpi_name_str}" if kpi_delta is not None else ""
                await create_action_outcome(
                    session_id=session_id,
                    domain=domain,
                    action_type=top_action.get("action_type", ""),
                    action_description=top_action.get("description", ""),
                    recommended_delta=delta_val,
                    kpi_name=first_kpi.get("kpi"),
                    projected_value=first_kpi.get("projected_value"),
                )
            except Exception as oe:
                logger.log("orchestrator", "outcome_creation_skipped", {"reason": str(oe)})

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

            # Store session knowledge in ChromaDB RAG store
            try:
                from utils.rag_store import add_session_knowledge
                add_session_knowledge(session_id, domain, master_brief)
            except Exception as re:
                logger.log("orchestrator", "rag_storage_failed", {"reason": str(re)})

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
                "confidence_score": master_brief["confidence_score"],
                "confidence_label": master_brief["confidence_label"],
                "context": master_brief["context"],
                "trace_url": f"/api/session/{session_id}/trace",
                "rag_sources_used": context.get("rag_sources_used", 0) if isinstance(context, dict) else 0,
                "rag_augmented": context.get("rag_augmented", False) if isinstance(context, dict) else False,
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
            from utils.validated_gemini import AgentValidationError
            if isinstance(e, AgentValidationError):
                logger.log("orchestrator", "validation_failed", {"agent": e.agent, "errors": e.validation_errors, "raw": e.raw_response})
                await update_session_status(session_id, "failed", error=f"Validation failed for agent {e.agent}: {e.validation_errors}")
                raise
            
            await update_session_status(session_id, "failed", error=str(e))
            logger.log("orchestrator", "pipeline_failed", {"error": str(e)})
            raise


async def check_and_trigger_alerts(master_brief: dict, session_id: str):
    import uuid
    from datetime import datetime, timezone
    from sqlalchemy import select
    from database.db import get_db
    from database.models import WatchlistAlert, AlertHistory
    from utils.commentary_stream import push_commentary

    domain = master_brief.get("domain")
    if not domain:
        return

    try:
        async with get_db() as db:
            result = await db.execute(
                select(WatchlistAlert)
                .where(WatchlistAlert.domain == domain)
                .where(WatchlistAlert.is_active == True)
            )
            active_alerts = result.scalars().all()

            for alert in active_alerts:
                triggered = False
                reason = ""
                
                if alert.condition_type == "severity_above":
                    try:
                        val = int(alert.condition_value)
                        sev = int(master_brief.get("severity", 5))
                        if sev > val:
                            triggered = True
                            reason = f"severity {sev} is above threshold {val}"
                    except Exception:
                        pass
                elif alert.condition_type == "kpi_change":
                    try:
                        val = float(alert.condition_value)
                        kpis = master_brief.get("kpis_affected", [])
                        for k in kpis:
                            dp = k.get("delta_pct")
                            if dp is not None:
                                dp_float = abs(float(dp))
                                if dp_float > val:
                                    triggered = True
                                    reason = f"KPI '{k.get('kpi')}' change of {dp}% (absolute) exceeds threshold of {val}%"
                                    break
                    except Exception:
                        pass
                elif alert.condition_type == "domain_keyword":
                    keyword = alert.keyword or alert.condition_value
                    insight = master_brief.get("insight", "")
                    if keyword and keyword.lower() in insight.lower():
                        triggered = True
                        reason = f"keyword '{keyword}' found in insight"

                if triggered:
                    # Update WatchlistAlert triggers
                    alert.last_triggered_at = datetime.now(timezone.utc)
                    alert.trigger_count += 1
                    
                    # Save history
                    history = AlertHistory(
                        id=str(uuid.uuid4()),
                        alert_id=alert.id,
                        session_id=session_id,
                        triggered_at=datetime.now(timezone.utc),
                        trigger_reason=reason
                    )
                    db.add(history)
                    
                    # Push stream commentary
                    alert_msg = f"🔔 Watchlist Alert triggered: '{alert.label}' ({reason})"
                    push_commentary(session_id, "watchlist", alert_msg, "progress")
    except Exception as e:
        print(f"Error executing alerts logic: {e}")

