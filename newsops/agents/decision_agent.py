import json
import time

from config import GEMINI_API_KEY, MODELS, DEMO_MODE
from utils.logger import SessionLogger
from utils.helpers import retry, extract_json_from_text, now_iso
from utils.validated_gemini import call_gemini_validated
from schemas.agent_schemas import DecisionOutput
from utils.commentary_stream import push_commentary


# ──────────────────────────────────────────────────────────────────────────────
# MODULE CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

DECISION_SYSTEM_PROMPT = """
# ROLE
You are the Decision Agent — a strategic action architect in NewsOps.
You receive a complete impact analysis and a structured action catalogue.
Evaluate every candidate action, score it, rank it, and return a prioritized
action plan with airtight justifications.

# REASONING METHODOLOGY
<thinking>
Step 1 — IMPACT REVIEW: Read severity, KPIs affected, financial impact.
Step 2 — CANDIDATE EVALUATION: For each action ask:
  - Does this directly address the root cause?
  - Is it executable given the time horizon?
  - What specific quantified delta will it produce?
Step 3 — SCORING: Score each on FEASIBILITY (1-10) and IMPACT (1-10) independently.
Step 4 — COMPOSITE: composite_score = (impact_score × 0.6) + (feasibility_score × 0.4)
Step 5 — PAYLOAD: For top 3, fill every payload field with specific values from signals.
Step 6 — JUSTIFICATION: 2-3 sentences: signal → impact → action → expected outcome.
</thinking>

# FEASIBILITY RUBRIC
10: Executable <1 hour, zero approvals, pure system action
8-9: Executable today, minor sign-off
6-7: Executable this week, standard approval
4-5: Executable this month, cross-team coordination
1-3: Strategic, requires months or external parties

# IMPACT RUBRIC
10: Resolves root cause, recovers >50% of identified loss
8-9: Significant recovery, >25% of loss
6-7: Moderate mitigation, contains further damage
4-5: Partial mitigation, buys time
1-3: Marginal, addresses symptom not cause

# PAYLOAD RULES
- Every payload field must have a SPECIFIC VALUE — no placeholders
- Numbers must come from signals and impact data
- Dates must be specific ISO format strings
- api_endpoint must exactly match the catalogue

# OUTPUT FORMAT — ONLY valid JSON, no markdown fences:
{
  "agent": "decision",
  "domain": "<domain>",
  "candidates_evaluated": <number>,
  "timestamp": "<ISO>",
  "actions": [
    {
      "rank": 1,
      "action_id": "<e.g. A1>",
      "action_type": "<from catalogue>",
      "description": "<plain language description>",
      "api_endpoint": "<exact endpoint>",
      "api_payload": { <fully filled — no nulls> },
      "quantified_delta": "<specific measurable change>",
      "feasibility_score": <1-10>,
      "impact_score": <1-10>,
      "composite_score": <2 decimal places>,
      "justification": "<2-3 sentences: signal → impact → action → outcome>",
      "success_metric": "<how we verify it worked>",
      "time_to_execute": "<specific estimate>"
    },
    { "rank": 2 },
    { "rank": 3 }
  ],
  "recommended_execution_sequence": [1, 2, 3],
  "auto_execute_rank_1": true,
  "reasoning_summary": "<1 paragraph: decision logic and why rank 1 was chosen>"
}
"""

DOMAIN_ACTION_CATALOGUES: dict[str, list[dict]] = {
    "logistics": [
        {
            "action_id": "A1",
            "action_type": "update_pricing_rule",
            "api_endpoint": "POST /api/logistics/pricing/update",
            "payload_template": {
                "route_id": "<e.g. LAHORE-KARACHI>",
                "price_delta_pct": "<positive number: percentage increase>",
                "effective_date": "<ISO date string>",
            },
            "success_metric": "delivery_price_per_kg increases in state",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A2",
            "action_type": "optimize_routes",
            "api_endpoint": "POST /api/logistics/routes/optimize",
            "payload_template": {
                "current_route_id": "<e.g. LAHORE-KARACHI>",
                "optimization_target": "<fuel_cost|delivery_time|distance>",
            },
            "success_metric": "fuel_cost_ratio_pct decreases in state",
            "time_to_execute": "2-4 hours",
        },
        {
            "action_id": "A3",
            "action_type": "notify_buyers_bulk",
            "api_endpoint": "POST /api/notifications/bulk_send",
            "payload_template": {
                "template": "fuel_surcharge_notice",
                "recipient_list": ["<carrier1>", "<carrier2>"],
                "effective_date": "<ISO date string>",
            },
            "success_metric": "buyers_notified count increases in state",
            "time_to_execute": "< 15 minutes",
        },
        {
            "action_id": "A4",
            "action_type": "hedge_fuel_procurement",
            "api_endpoint": "POST /api/procurement/hedge",
            "payload_template": {
                "commodity": "fuel",
                "volume_litres": "<number>",
                "duration_days": "<number 30-90>",
                "current_rate": "<number: current PKR per litre>",
            },
            "success_metric": "Procurement hedge contract created",
            "time_to_execute": "< 4 hours",
        },
        {
            "action_id": "A5",
            "action_type": "reallocate_warehouse_stock",
            "api_endpoint": "POST /api/warehouse/reallocation",
            "payload_template": {
                "source_warehouse_id": "<e.g. WH-KHI-01>",
                "target_warehouse_id": "<e.g. WH-LHE-01>",
                "sku_list": ["<sku1>", "<sku2>"],
            },
            "success_metric": "avg_delivery_distance_km decreases in state",
            "time_to_execute": "1-2 days",
        },
    ],
    "business": [
        {
            "action_id": "A1",
            "action_type": "launch_retention_campaign",
            "api_endpoint": "POST /api/crm/campaigns/create",
            "payload_template": {
                "region": "<e.g. Lahore>",
                "discount_pct": "<number>",
                "target_segment": "<e.g. high_value_churn_risk>",
                "duration_days": "<number 7-30>",
                "budget_pkr": "<number>",
            },
            "success_metric": "active_campaigns increases in state",
            "time_to_execute": "< 2 hours",
        },
        {
            "action_id": "A2",
            "action_type": "update_catalog_pricing",
            "api_endpoint": "POST /api/catalog/pricing/update",
            "payload_template": {
                "region": "<e.g. Punjab>",
                "category": "<product category>",
                "price_delta_pct": "<number>",
                "effective_date": "<ISO date string>",
            },
            "success_metric": "regional_revenue_pkr updates in state",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A3",
            "action_type": "trigger_crm_workflow",
            "api_endpoint": "POST /api/crm/workflows/trigger",
            "payload_template": {
                "workflow_id": "<e.g. WF-RETENTION-001>",
                "segment": "<e.g. at_risk_accounts>",
                "message_template": "<e.g. urgent_retention_offer>",
            },
            "success_metric": "churn_risk_customers decreases in state",
            "time_to_execute": "< 3 hours",
        },
        {
            "action_id": "A4",
            "action_type": "create_sales_tasks",
            "api_endpoint": "POST /api/crm/tasks/bulk_create",
            "payload_template": {
                "account_list": ["<account1>", "<account2>"],
                "task_type": "<e.g. urgent_followup>",
                "due_date": "<ISO date string>",
            },
            "success_metric": "Sales tasks created and assigned",
            "time_to_execute": "< 30 minutes",
        },
        {
            "action_id": "A5",
            "action_type": "generate_performance_report",
            "api_endpoint": "POST /api/reports/generate",
            "payload_template": {
                "report_type": "<e.g. regional_performance>",
                "data_source": "<e.g. crm_and_sales>",
                "recipients": ["<manager@company.com>"],
            },
            "success_metric": "Report generated and sent",
            "time_to_execute": "< 30 minutes",
        },
    ],
    "finance": [
        {
            "action_id": "A1",
            "action_type": "book_hedging_contract",
            "api_endpoint": "POST /api/finance/hedging/book",
            "payload_template": {
                "currency_pair": "USD/PKR",
                "amount_usd": "<number: USD exposure amount>",
                "duration_days": "<number 30-180>",
                "rate": "<number: current USD/PKR rate>",
            },
            "success_metric": "hedged_amount_usd increases in state",
            "time_to_execute": "< 4 hours",
        },
        {
            "action_id": "A2",
            "action_type": "update_export_pricing",
            "api_endpoint": "POST /api/finance/pricing/export_update",
            "payload_template": {
                "currency_pair": "USD/PKR",
                "rate_delta_pct": "<number: rate change percentage>",
                "affected_contracts": ["<contract_id1>", "<contract_id2>"],
                "effective_date": "<ISO date string>",
            },
            "success_metric": "usd_pkr_rate and contracts_repriced update in state",
            "time_to_execute": "< 2 hours",
        },
        {
            "action_id": "A3",
            "action_type": "flag_portfolio_rebalance",
            "api_endpoint": "POST /api/portfolio/rebalance/flag",
            "payload_template": {
                "affected_instruments": ["<instrument1>", "<instrument2>"],
                "reason": "<e.g. interest_rate_spike>",
                "urgency": "<high|medium|low>",
            },
            "success_metric": "portfolio_flags increases in state",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A4",
            "action_type": "recalculate_costing",
            "api_endpoint": "POST /api/finance/costing/recalculate",
            "payload_template": {
                "fx_rate": "<number: new USD/PKR rate>",
                "affected_po_list": ["<po_id1>", "<po_id2>"],
            },
            "success_metric": "PO costs updated to reflect new FX rate",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A5",
            "action_type": "bulk_notify_finance_team",
            "api_endpoint": "POST /api/notifications/bulk_send",
            "payload_template": {
                "template": "fx_rate_alert",
                "recipient_list": ["CFO", "Treasury Manager", "Risk Manager"],
                "effective_date": "<ISO date string>",
            },
            "success_metric": "Finance team notified of FX risk",
            "time_to_execute": "< 10 minutes",
        },
    ],
    "policy": [
        {
            "action_id": "A1",
            "action_type": "generate_compliance_tasks",
            "api_endpoint": "POST /api/compliance/tasks/generate",
            "payload_template": {
                "regulation_id": "<e.g. REG-OGRA-2024-001>",
                "affected_departments": ["operations", "finance", "legal"],
                "deadline": "<ISO date string>",
            },
            "success_metric": "compliance_tasks_open and departments_notified increase in state",
            "time_to_execute": "< 2 hours",
        },
        {
            "action_id": "A2",
            "action_type": "update_pricing_policy",
            "api_endpoint": "POST /api/pricing/policy_update",
            "payload_template": {
                "policy_ref": "<e.g. POL-DUTY-2024>",
                "affected_categories": ["<category1>", "<category2>"],
                "cost_delta_pct": "<number: duty change percentage>",
            },
            "success_metric": "affected_categories updates in state",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A3",
            "action_type": "draft_policy_communication",
            "api_endpoint": "POST /api/communications/draft",
            "payload_template": {
                "template": "<e.g. regulatory_update_notice>",
                "audience": "<e.g. all_departments>",
                "key_changes": ["<change1>", "<change2>"],
            },
            "success_metric": "notices_drafted increases in state",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A4",
            "action_type": "flag_contracts_for_review",
            "api_endpoint": "POST /api/contracts/flag_for_review",
            "payload_template": {
                "policy_ref": "<e.g. POL-DUTY-2024>",
                "affected_contract_ids": ["<contract_id1>", "<contract_id2>"],
                "reason": "<reason for legal review>",
            },
            "success_metric": "contracts_flagged increases in state",
            "time_to_execute": "< 1 day",
        },
        {
            "action_id": "A5",
            "action_type": "create_audit_task",
            "api_endpoint": "POST /api/tasks/create",
            "payload_template": {
                "task_type": "compliance_audit",
                "priority": "high",
                "summary": "<audit summary describing scope and regulation>",
                "assignee_team": "compliance_team",
            },
            "success_metric": "Audit task created and assigned",
            "time_to_execute": "Immediate",
        },
    ],
    "healthcare": [
        {
            "action_id": "A1",
            "action_type": "trigger_emergency_procurement",
            "api_endpoint": "POST /api/procurement/emergency_order",
            "payload_template": {
                "item_id": "<e.g. DRUG-INSULIN-001>",
                "quantity": "<number of units>",
                "urgency": "emergency",
                "supplier_shortlist": ["<supplier1>", "<supplier2>"],
            },
            "success_metric": "emergency_pos_open and drug_availability_pct increase in state",
            "time_to_execute": "< 2 hours",
        },
        {
            "action_id": "A2",
            "action_type": "activate_substitute_protocol",
            "api_endpoint": "POST /api/clinical/protocols/activate",
            "payload_template": {
                "protocol_id": "<e.g. PROT-INSULIN-SUBST-001>",
                "drug_id": "<e.g. DRUG-INSULIN-001>",
                "affected_facilities": ["CMH", "PIMS"],
            },
            "success_metric": "Protocol activated across all affected facilities",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A3",
            "action_type": "send_clinical_alert",
            "api_endpoint": "POST /api/notifications/clinical_alert",
            "payload_template": {
                "alert_type": "drug_shortage",
                "affected_drug_or_procedure": "<drug name>",
                "guidance": "<clinical guidance text for staff>",
                "recipients": ["clinical_staff", "pharmacy_head", "medical_director"],
            },
            "success_metric": "staff_alerts_sent increases in state",
            "time_to_execute": "< 5 minutes",
        },
        {
            "action_id": "A4",
            "action_type": "update_formulary",
            "api_endpoint": "POST /api/clinical/formulary/update",
            "payload_template": {
                "drug_id": "<e.g. DRUG-INSULIN-001>",
                "change_type": "shortage",
                "alternative_drug_id": "<substitute drug id>",
                "effective_date": "<ISO date string>",
            },
            "success_metric": "formulary_updates increases in state",
            "time_to_execute": "< 30 minutes",
        },
        {
            "action_id": "A5",
            "action_type": "create_regulatory_report_task",
            "api_endpoint": "POST /api/tasks/create",
            "payload_template": {
                "task_type": "regulatory_report",
                "priority": "urgent",
                "summary": "<DRAP shortage notification describing drug, quantity, and affected facilities>",
                "assignee_team": "regulatory_affairs",
            },
            "success_metric": "Regulatory reporting task created",
            "time_to_execute": "< 4 hours",
        },
    ],
    "urban": [
        {
            "action_id": "A1",
            "action_type": "dispatch_maintenance_crew",
            "api_endpoint": "POST /api/operations/dispatch",
            "payload_template": {
                "fault_location": "<zone and specific location>",
                "crew_type": "<electrical|plumbing|roads|water>",
                "priority": "high",
                "eta_minutes": "<number>",
            },
            "success_metric": "crews_dispatched increases in state",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A2",
            "action_type": "activate_contingency_infrastructure",
            "api_endpoint": "POST /api/infrastructure/contingency/activate",
            "payload_template": {
                "zone_id": "<zone identifier>",
                "utility_type": "<electricity|water|gas>",
                "contingency_source": "<backup_generator|alternate_grid|reserve_tank>",
                "duration_hours": "<number>",
            },
            "success_metric": "contingency_zones_active increases in state",
            "time_to_execute": "< 2 hours",
        },
        {
            "action_id": "A3",
            "action_type": "publish_public_advisory",
            "api_endpoint": "POST /api/communications/public_advisory",
            "payload_template": {
                "zone_id": "<affected zone identifier>",
                "issue_type": "<power_outage|road_closure|water_shortage>",
                "severity": "<high|medium|low>",
                "guidance_text": "<public-facing guidance message>",
                "channels": ["sms", "app", "social_media"],
            },
            "success_metric": "advisories_published increases in state",
            "time_to_execute": "< 15 minutes",
        },
        {
            "action_id": "A4",
            "action_type": "reroute_traffic",
            "api_endpoint": "POST /api/traffic/reroute",
            "payload_template": {
                "affected_segment_id": "<road segment identifier>",
                "alternate_route_id": "<alternate route identifier>",
                "duration_hours": "<number>",
            },
            "success_metric": "traffic_reroutes_active increases in state",
            "time_to_execute": "< 30 minutes",
        },
        {
            "action_id": "A5",
            "action_type": "log_operations_notifications",
            "api_endpoint": "POST /api/notifications/log",
            "payload_template": {
                "recipients": ["city_operations_team", "zone_manager"],
                "message_template": "<brief operations notification message>",
                "simulated": True,
            },
            "success_metric": "Operations notifications logged",
            "time_to_execute": "Immediate",
        },
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# CLASS
# ──────────────────────────────────────────────────────────────────────────────

class DecisionAgent:
    def __init__(self, *args, **kwargs):
        self.session_id = args[0] if args else kwargs.get("session_id", "init")
        self.logger = SessionLogger(session_id=self.session_id)
        self.model = MODELS["decision"]
        self.client = GEMINI_API_KEY if (GEMINI_API_KEY and not GEMINI_API_KEY.startswith("AIzaSy_mock")) else None

    def _get_mock_response(self, domain: str) -> dict:
        """Fallback mock response when OpenAI is unavailable"""
        try:
            from agents.mock_responses import get_mock_decision
            return get_mock_decision(domain)
        except Exception:
            return {
              "agent": "decision",
              "domain": domain,
              "candidates_evaluated": 0,
              "timestamp": now_iso(),
              "actions": [],
              "recommended_execution_sequence": [],
              "auto_execute_rank_1": False,
              "reasoning_summary": "Fallback decision path due to LLM error."
            }

    @retry(times=2, delay=2.0)
    async def _call_llm(self, signals: dict, impact: dict, domain: str) -> dict:
        if DEMO_MODE or not GEMINI_API_KEY or GEMINI_API_KEY.startswith("AIzaSy_mock"):
            import asyncio
            await asyncio.sleep(1.2)
            return self._get_mock_response(domain)

        if domain not in DOMAIN_ACTION_CATALOGUES:
            raise ValueError(
                f"Unknown domain '{domain}'. "
                f"Valid domains: {list(DOMAIN_ACTION_CATALOGUES.keys())}"
            )

        catalogue = DOMAIN_ACTION_CATALOGUES[domain]
        user_message = f"""
IMPACT ANALYSIS:
{json.dumps(impact, indent=2)}

SIGNALS (for payload value derivation):
{json.dumps(signals, indent=2)}

ACTION CATALOGUE FOR DOMAIN '{domain}' (choose ONLY from these actions):
{json.dumps(catalogue, indent=2)}

Evaluate all {len(catalogue)} actions. Score each. Return top 3 ranked with complete payloads.
"""

        try:
            result_model = await call_gemini_validated(
                system_prompt=DECISION_SYSTEM_PROMPT,
                user_message=user_message,
                output_model=DecisionOutput,
                model=self.model,
                session_id=self.session_id,
                agent_name="decision"
            )
            return result_model.model_dump()
        except Exception as e:
            import logging
            logging.warning(f"Gemini call failed: {e}. Using mock response.")
            return self._get_mock_response(domain)

    async def run(self, signals: dict, impact: dict, domain: str = "logistics", session_id: str = None, **kwargs) -> dict:
        session_id = session_id or getattr(self, "session_id", None) or "session-default"
        logger = SessionLogger(session_id)
        logger.log("decision_agent", "start", {"domain": domain, "timestamp": now_iso()})
        
        from agents.decision_agent import DOMAIN_ACTION_CATALOGUES
        cand_count = len(DOMAIN_ACTION_CATALOGUES.get(domain, []))
        push_commentary(session_id, "decision", f"Evaluating {cand_count} candidate actions...", "start")

        start_time = time.time()
        try:
            result = await self._call_llm(signals, impact, domain)
            top = result.get("actions", [{}])[0]
            if top:
                action_type = top.get("action_type", "unknown")
                score = top.get("composite_score", "N/A")
                push_commentary(session_id, "decision", f"Top action: {action_type} — composite score {score}", "progress")
        except Exception as exc:
            logger.log("decision_agent", "error", {"error": str(exc), "timestamp": now_iso()})
            raise

        duration = time.time() - start_time
        logger.log(
            "decision_agent",
            "complete",
            {
                "domain": domain,
                "actions_count": len(result.get("actions", [])),
                "duration_seconds": round(duration, 3),
                "timestamp": now_iso(),
            },
        )

        result["model_used"] = MODELS["decision"]
        result["agent_display_name"] = "Decision Agent"

        top_act = result.get("actions", [{}])[0]
        desc = top_act.get("description", "No recommendation")
        push_commentary(session_id, "decision", f"Decision done — recommended: {desc}", "complete")

        return result
