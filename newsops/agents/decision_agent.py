import json
import time

from config import GEMINI_API_KEY, MODELS, DEMO_MODE
from utils.logger import SessionLogger
from utils.helpers import retry, extract_json_from_text, now_iso
from utils.gemini_client import call_gemini


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
            "api_endpoint": "POST /api/logistics/pricing",
            "payload_template": {
                "route_id": "<route>",
                "price_increase_pct": "<number>",
                "effective_date": "<ISO>",
                "reason": "<string>",
            },
            "success_metric": "New pricing visible in GET /api/logistics/pricing within 60s",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A2",
            "action_type": "reroute_shipments",
            "api_endpoint": "POST /api/logistics/reroute",
            "payload_template": {
                "affected_route": "<route>",
                "new_route": "<route>",
                "shipment_ids": ["<id>"],
                "reason": "<string>",
            },
            "success_metric": "Affected shipments show new route in GET /api/logistics/shipments",
            "time_to_execute": "2-4 hours",
        },
        {
            "action_id": "A3",
            "action_type": "notify_logistics_manager",
            "api_endpoint": "POST /api/notifications/send",
            "payload_template": {
                "recipient_role": "logistics_manager",
                "channel": "email",
                "subject": "<string>",
                "body": "<string>",
                "priority": "high",
            },
            "success_metric": "Notification status = delivered in GET /api/notifications",
            "time_to_execute": "< 15 minutes",
        },
        {
            "action_id": "A4",
            "action_type": "adjust_fuel_surcharge",
            "api_endpoint": "POST /api/logistics/surcharge",
            "payload_template": {
                "surcharge_pct": "<number>",
                "applies_to": "all_routes",
                "effective_date": "<ISO>",
            },
            "success_metric": "Surcharge reflected in next pricing calculation",
            "time_to_execute": "< 30 minutes",
        },
        {
            "action_id": "A5",
            "action_type": "flag_for_review",
            "api_endpoint": "POST /api/sessions/flag",
            "payload_template": {
                "session_id": "<id>",
                "flag_reason": "<string>",
                "severity": "<number>",
                "assigned_to": "operations_team",
            },
            "success_metric": "Flag visible in GET /api/sessions/{id}",
            "time_to_execute": "Immediate",
        },
    ],
    "business": [
        {
            "action_id": "A1",
            "action_type": "launch_retention_campaign",
            "api_endpoint": "POST /api/business/campaigns",
            "payload_template": {
                "campaign_name": "<string>",
                "target_segment": "<string>",
                "discount_pct": "<number>",
                "budget_pkr": "<number>",
                "start_date": "<ISO>",
                "end_date": "<ISO>",
            },
            "success_metric": "Campaign active in GET /api/business/campaigns",
            "time_to_execute": "< 2 hours",
        },
        {
            "action_id": "A2",
            "action_type": "update_regional_pricing",
            "api_endpoint": "POST /api/business/pricing",
            "payload_template": {
                "region": "<string>",
                "price_adjustment_pct": "<number>",
                "sku_ids": ["<id>"],
                "effective_date": "<ISO>",
            },
            "success_metric": "Pricing updated in GET /api/business/products",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A3",
            "action_type": "escalate_to_sales_manager",
            "api_endpoint": "POST /api/notifications/send",
            "payload_template": {
                "recipient_role": "sales_manager",
                "channel": "sms",
                "subject": "<string>",
                "body": "<string>",
                "priority": "high",
            },
            "success_metric": "Notification delivered",
            "time_to_execute": "< 10 minutes",
        },
        {
            "action_id": "A4",
            "action_type": "increase_crm_outreach",
            "api_endpoint": "POST /api/business/crm/outreach",
            "payload_template": {
                "segment": "<string>",
                "outreach_type": "email_sequence",
                "sequence_id": "<string>",
                "target_count": "<number>",
            },
            "success_metric": "Outreach sequence active in CRM",
            "time_to_execute": "< 3 hours",
        },
        {
            "action_id": "A5",
            "action_type": "generate_performance_report",
            "api_endpoint": "POST /api/business/reports",
            "payload_template": {
                "report_type": "regional_performance",
                "region": "<string>",
                "period": "<string>",
                "format": "pdf",
            },
            "success_metric": "Report downloadable from GET /api/business/reports",
            "time_to_execute": "< 30 minutes",
        },
    ],
    "finance": [
        {
            "action_id": "A1",
            "action_type": "set_fx_alert",
            "api_endpoint": "POST /api/finance/alerts",
            "payload_template": {
                "currency_pair": "USD/PKR",
                "threshold_rate": "<number>",
                "direction": "<above|below>",
                "notify_role": "finance_manager",
            },
            "success_metric": "Alert active in GET /api/finance/alerts",
            "time_to_execute": "Immediate",
        },
        {
            "action_id": "A2",
            "action_type": "update_hedging_position",
            "api_endpoint": "POST /api/finance/hedging",
            "payload_template": {
                "exposure_usd": "<number>",
                "hedge_ratio_pct": "<number>",
                "instrument": "forward_contract",
                "maturity_date": "<ISO>",
            },
            "success_metric": "Hedge position updated in GET /api/finance/hedging",
            "time_to_execute": "< 4 hours",
        },
        {
            "action_id": "A3",
            "action_type": "revalue_portfolio",
            "api_endpoint": "POST /api/finance/portfolio/revalue",
            "payload_template": {
                "portfolio_id": "<id>",
                "new_rate": "<number>",
                "revalue_date": "<ISO>",
            },
            "success_metric": "Portfolio shows updated valuation",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A4",
            "action_type": "notify_finance_team",
            "api_endpoint": "POST /api/notifications/send",
            "payload_template": {
                "recipient_role": "finance_team",
                "channel": "email",
                "subject": "<string>",
                "body": "<string>",
                "priority": "urgent",
            },
            "success_metric": "Notification delivered",
            "time_to_execute": "< 10 minutes",
        },
        {
            "action_id": "A5",
            "action_type": "flag_for_board_review",
            "api_endpoint": "POST /api/sessions/flag",
            "payload_template": {
                "session_id": "<id>",
                "flag_reason": "<string>",
                "severity": "<number>",
                "assigned_to": "board",
            },
            "success_metric": "Flag visible in session record",
            "time_to_execute": "Immediate",
        },
    ],
    "policy": [
        {
            "action_id": "A1",
            "action_type": "update_compliance_checklist",
            "api_endpoint": "POST /api/policy/compliance",
            "payload_template": {
                "regulation_name": "<string>",
                "effective_date": "<ISO>",
                "affected_departments": ["<dept>"],
                "checklist_items": ["<item>"],
            },
            "success_metric": "Checklist active in GET /api/policy/compliance",
            "time_to_execute": "< 2 hours",
        },
        {
            "action_id": "A2",
            "action_type": "notify_legal_team",
            "api_endpoint": "POST /api/notifications/send",
            "payload_template": {
                "recipient_role": "legal_team",
                "channel": "email",
                "subject": "<string>",
                "body": "<string>",
                "priority": "high",
            },
            "success_metric": "Notification delivered",
            "time_to_execute": "< 10 minutes",
        },
        {
            "action_id": "A3",
            "action_type": "adjust_pricing_for_duty_change",
            "api_endpoint": "POST /api/business/pricing",
            "payload_template": {
                "adjustment_reason": "duty_change",
                "price_adjustment_pct": "<number>",
                "effective_date": "<ISO>",
                "sku_ids": ["all"],
            },
            "success_metric": "Pricing updated across all SKUs",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A4",
            "action_type": "schedule_compliance_audit",
            "api_endpoint": "POST /api/policy/audits",
            "payload_template": {
                "regulation_name": "<string>",
                "audit_date": "<ISO>",
                "auditor_team": "internal_compliance",
            },
            "success_metric": "Audit scheduled in GET /api/policy/audits",
            "time_to_execute": "< 1 day",
        },
        {
            "action_id": "A5",
            "action_type": "flag_for_review",
            "api_endpoint": "POST /api/sessions/flag",
            "payload_template": {
                "session_id": "<id>",
                "flag_reason": "<string>",
                "severity": "<number>",
                "assigned_to": "compliance_officer",
            },
            "success_metric": "Flag visible in session",
            "time_to_execute": "Immediate",
        },
    ],
    "healthcare": [
        {
            "action_id": "A1",
            "action_type": "trigger_emergency_procurement",
            "api_endpoint": "POST /api/healthcare/procurement",
            "payload_template": {
                "drug_name": "<string>",
                "quantity_units": "<number>",
                "urgency": "emergency",
                "supplier_tier": "tier_1",
                "budget_pkr": "<number>",
            },
            "success_metric": "Procurement order in GET /api/healthcare/procurement",
            "time_to_execute": "< 2 hours",
        },
        {
            "action_id": "A2",
            "action_type": "notify_clinical_staff",
            "api_endpoint": "POST /api/notifications/send",
            "payload_template": {
                "recipient_role": "clinical_staff",
                "channel": "sms",
                "subject": "<string>",
                "body": "<string>",
                "priority": "urgent",
            },
            "success_metric": "Notification delivered",
            "time_to_execute": "< 5 minutes",
        },
        {
            "action_id": "A3",
            "action_type": "activate_substitute_protocol",
            "api_endpoint": "POST /api/healthcare/protocols",
            "payload_template": {
                "primary_drug": "<string>",
                "substitute_drug": "<string>",
                "effective_immediately": True,
                "approved_by": "chief_pharmacist",
            },
            "success_metric": "Protocol active in GET /api/healthcare/protocols",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A4",
            "action_type": "update_formulary",
            "api_endpoint": "POST /api/healthcare/formulary",
            "payload_template": {
                "drug_name": "<string>",
                "status": "<available|shortage|unavailable>",
                "notes": "<string>",
            },
            "success_metric": "Formulary status updated",
            "time_to_execute": "< 30 minutes",
        },
        {
            "action_id": "A5",
            "action_type": "report_to_drap",
            "api_endpoint": "POST /api/healthcare/regulatory_report",
            "payload_template": {
                "report_type": "shortage_notification",
                "drug_name": "<string>",
                "shortage_quantity": "<number>",
                "facility": "<string>",
            },
            "success_metric": "Report filed in regulatory log",
            "time_to_execute": "< 4 hours",
        },
    ],
    "urban": [
        {
            "action_id": "A1",
            "action_type": "dispatch_maintenance_team",
            "api_endpoint": "POST /api/urban/maintenance",
            "payload_template": {
                "zone": "<string>",
                "issue_type": "<string>",
                "team_size": "<number>",
                "priority": "high",
                "eta_hours": "<number>",
            },
            "success_metric": "Team dispatched in GET /api/urban/maintenance",
            "time_to_execute": "< 1 hour",
        },
        {
            "action_id": "A2",
            "action_type": "issue_public_alert",
            "api_endpoint": "POST /api/urban/alerts",
            "payload_template": {
                "alert_type": "<string>",
                "affected_zone": "<string>",
                "message": "<string>",
                "channels": ["sms", "app"],
                "duration_hours": "<number>",
            },
            "success_metric": "Alert live in GET /api/urban/alerts",
            "time_to_execute": "< 15 minutes",
        },
        {
            "action_id": "A3",
            "action_type": "reroute_traffic",
            "api_endpoint": "POST /api/urban/traffic",
            "payload_template": {
                "blocked_zone": "<string>",
                "alternate_routes": ["<route>"],
                "effective_from": "<ISO>",
                "effective_until": "<ISO>",
            },
            "success_metric": "Traffic plan active in GET /api/urban/traffic",
            "time_to_execute": "< 30 minutes",
        },
        {
            "action_id": "A4",
            "action_type": "notify_utility_provider",
            "api_endpoint": "POST /api/notifications/send",
            "payload_template": {
                "recipient_role": "utility_provider",
                "channel": "email",
                "subject": "<string>",
                "body": "<string>",
                "priority": "urgent",
            },
            "success_metric": "Notification delivered",
            "time_to_execute": "< 10 minutes",
        },
        {
            "action_id": "A5",
            "action_type": "update_infrastructure_status",
            "api_endpoint": "POST /api/urban/infrastructure",
            "payload_template": {
                "asset_id": "<string>",
                "zone": "<string>",
                "status": "<operational|degraded|offline>",
                "notes": "<string>",
            },
            "success_metric": "Status updated in infrastructure log",
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
            return await call_gemini(
                system_prompt=DECISION_SYSTEM_PROMPT,
                user_message=user_message,
                model=self.model,
                temperature=0.4,
                expect_json=True,
            )
        except Exception as e:
            import logging
            logging.warning(f"Gemini call failed: {e}. Using mock response.")
            return self._get_mock_response(domain)

    async def run(self, signals: dict, impact: dict, domain: str = "logistics", session_id: str = None, **kwargs) -> dict:
        session_id = session_id or getattr(self, "session_id", None) or "session-default"
        logger = SessionLogger(session_id)
        logger.log("decision_agent", "start", {"domain": domain, "timestamp": now_iso()})

        start_time = time.time()
        try:
            result = await self._call_llm(signals, impact, domain)
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

        return result
