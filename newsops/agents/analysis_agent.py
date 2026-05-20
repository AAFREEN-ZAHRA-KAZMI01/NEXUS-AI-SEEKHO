import json
import time

from config import GEMINI_API_KEY, MODELS, DEMO_MODE
from utils.logger import SessionLogger
from utils.helpers import retry, extract_json_from_text, now_iso
from utils.gemini_client import call_gemini


# ──────────────────────────────────────────────────────────────────────────────
# MODULE CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

ANALYSIS_BASE_SYSTEM_PROMPT = """
# ROLE
You are the Analysis Agent — a senior domain expert and quantitative analyst in the
NewsOps autonomous intelligence system. You receive structured signals and produce a
rigorous, evidence-based impact analysis.

# REASONING METHODOLOGY — MANDATORY
<thinking>
Step 1 — SIGNAL REVIEW: Read every fact. Identify the 3 most significant.
Step 2 — KPI MAPPING: For each significant fact, identify which KPIs are affected.
Step 3 — QUANTIFICATION: For each KPI compute: current_value, projected_value, delta, delta_pct.
Step 4 — SEVERITY SCORING: Apply the rubric below. Show which modifiers apply.
Step 5 — SECOND-ORDER EFFECTS: What downstream effects follow?
Step 6 — AFFECTED PARTIES: Who specifically bears the impact?
Step 7 — TIME HORIZON: immediate (<1 week), short-term (1-4 weeks), medium-term (1-3 months)?
</thinking>

# SEVERITY SCORING RUBRIC
Base score starts at 5. Apply modifiers:
+2 if confidence = "high"
+1 if any single directional change exceeds 15%
+1 if 3 or more facts point in the same direction
+1 if financial impact exceeds PKR 1,000,000
-1 if confidence = "low"
-1 if no numeric quantification exists
-2 if signals contain contradictory directions
Final score clamped between 1 and 10.

# SEVERITY LABELS
1-2: Low | 3-4: Low-Medium | 5-6: Medium | 7-8: High | 9-10: Critical

# CONSTRAINTS
- Never invent numbers not present or derivable from signals.
- Financial impacts must be in PKR.
- reasoning_chain must have minimum 4 entries.
- If a KPI value cannot be computed, set to null and note data gap.

# OUTPUT FORMAT — ONLY valid JSON, no markdown fences:
{
  "agent": "analysis",
  "domain": "<domain>",
  "severity": <1-10>,
  "severity_label": "<label>",
  "severity_reasoning": "<paragraph explaining score and modifiers>",
  "time_horizon": "<immediate|short_term|medium_term>",
  "kpis_affected": [
    {
      "kpi": "<name>",
      "current_value": <number or null>,
      "current_unit": "<unit>",
      "projected_value": <number or null>,
      "delta": <number or null>,
      "delta_pct": <number or null>,
      "direction": "<increase|decrease>"
    }
  ],
  "total_impact": {
    "financial_pkr": <number or null>,
    "operational": "<description>",
    "human": "<people affected or null>",
    "reputational": "<low|medium|high|null>"
  },
  "affected_parties": ["<party1>", "<party2>"],
  "second_order_effects": ["<effect1>", "<effect2>", "<effect3>"],
  "reasoning_chain": ["<step1>", "<step2>", "<step3>", "<step4>", "<step5>"],
  "data_gaps": ["<missing data point>"]
}
"""

DOMAIN_ANALYSIS_INSTRUCTIONS: dict[str, str] = {
    "logistics": """
DOMAIN: LOGISTICS / SUPPLY CHAIN
KPI CATALOGUE:
- delivery_cost_per_shipment (PKR)
- fuel_cost_ratio_pct (industry average: 35%)
- route_efficiency (deliveries per litre)
- on_time_delivery_rate_pct
- monthly_shipment_volume
- warehouse_utilization_pct

QUANTIFICATION FORMULAS:
- Fuel price increase X% → delivery cost increase = X% × 0.35
- Monthly financial impact = monthly_shipment_volume × delivery_cost × delta_pct
- If volume unknown: use 4,200 shipments/month (Pakistan medium logistics company)
- If delivery_cost unknown: use PKR 320/shipment

SECOND-ORDER EFFECTS:
1. Fuel cost → delivery cost → product retail price → consumer inflation
2. Higher delivery cost → reduced margins → reduced competitiveness
3. Fuel scarcity → route disruptions → delivery delays → customer dissatisfaction
""",
    "business": """
DOMAIN: BUSINESS OPERATIONS
KPI CATALOGUE:
- regional_revenue_pkr
- order_volume_monthly
- avg_order_value_pkr
- customer_acquisition_cost_pkr
- churn_rate_pct
- campaign_roi_pct
- sales_conversion_rate_pct

QUANTIFICATION FORMULAS:
- Revenue impact = order_delta × avg_order_value_pkr
- Example: 25% order decline, avg PKR 6,850, 1,240 orders → PKR 2,123,500/month
- Implied churn = (baseline_orders - current_orders) / baseline_orders × 100
- Campaign reach = budget_pkr × 3.2 (Pakistan digital benchmark)

SECOND-ORDER EFFECTS:
1. Revenue decline → cash flow pressure → delayed supplier payments
2. High churn → increased CAC → margin compression
3. Regional issue → may indicate broader national market signal
""",
    "finance": """
DOMAIN: FINANCE / INVESTMENT
KPI CATALOGUE:
- usd_pkr_rate
- interest_rate_pct
- export_revenue_pkr
- import_cost_pkr
- portfolio_value_pkr
- hedging_cost_pct
- net_fx_exposure_usd

QUANTIFICATION FORMULAS:
- PKR depreciation X% → exporters: revenue in PKR increases ~X% (beneficial)
- PKR depreciation X% → importers: costs in PKR increase ~X% (harmful)
- Net impact = (export_usd - import_usd) × fx_delta_pkr
- Flag: if net financial impact > PKR 5,000,000 → severity minimum 7

SECOND-ORDER EFFECTS:
1. PKR depreciation → import cost inflation → consumer prices rise
2. Interest rate change → business borrowing cost → investment decisions
3. FX volatility → contract pricing uncertainty → delayed procurement
""",
    "policy": """
DOMAIN: PUBLIC POLICY / REGULATION
KPI CATALOGUE:
- compliance_cost_pkr
- compliance_deadline_days
- affected_revenue_pct
- sector_impact_pkr
- regulatory_fine_risk_pkr
- operational_disruption_days

QUANTIFICATION FORMULAS:
- Sector-wide impact = total_sector_revenue × price_change_pct
- Pakistan textile sector: ~PKR 450 billion/year
- Pakistan logistics sector: ~PKR 200 billion/year
- Compliance cost estimate: 5-8 staff × 10 days × PKR 8,000/day + PKR 200,000 system changes

SECOND-ORDER EFFECTS:
1. Fuel/energy policy → ALL sectors affected (logistics → manufacturing → retail)
2. Import duty change → landed cost → retail price → demand reduction
3. Regulatory compliance → operational pause → supply disruption → contract penalties
""",
    "healthcare": """
DOMAIN: HEALTHCARE / PHARMA
KPI CATALOGUE:
- drug_availability_pct
- patients_at_risk
- treatment_cost_per_patient_pkr
- shortage_quantity
- procurement_cost_increase_pkr
- compliance_score_pct

QUANTIFICATION FORMULAS:
- Patients at risk = facility_daily_capacity × shortage_days × condition_prevalence_pct
- Emergency procurement premium: 25-40% above standard price
- If patients_at_risk > 1,000 → severity minimum 8
- If patients_at_risk > 10,000 → severity minimum 10

SECOND-ORDER EFFECTS:
1. Drug shortage → treatment delays → outcomes worsen → liability risk
2. Price increase → formulary change → prescribing disruption
3. Regulatory non-compliance → accreditation risk → patient trust
""",
    "urban": """
DOMAIN: URBAN SYSTEMS / SMART CITY
KPI CATALOGUE:
- affected_population
- infrastructure_downtime_hours
- economic_cost_pkr
- maintenance_cost_pkr
- public_complaint_index (1-10)
- service_restoration_eta_hours

QUANTIFICATION FORMULAS:
- Power outage cost = affected_businesses × PKR 15,000/hour × outage_hours
- Water shortage = affected_households × PKR 500/day × shortage_days
- Traffic disruption = vehicles/hour × avg_delay_hours × PKR 200/hour

SECOND-ORDER EFFECTS:
1. Power outage → business revenue loss → generator fuel demand spike
2. Water shortage → public health risk → hospital load increase
3. Infrastructure failure → city competitiveness → investment deterrence
""",
}


# ──────────────────────────────────────────────────────────────────────────────
# CLASS
# ──────────────────────────────────────────────────────────────────────────────

class AnalysisAgent:
    def __init__(self, *args, **kwargs):
        self.session_id = args[0] if args else kwargs.get("session_id", "init")
        self.logger = SessionLogger(session_id=self.session_id)
        self.model = MODELS["analysis"]
        self.client = GEMINI_API_KEY if (GEMINI_API_KEY and not GEMINI_API_KEY.startswith("AIzaSy_mock")) else None

    def _get_mock_response(self, domain: str) -> dict:
        """Fallback mock response when OpenAI is unavailable"""
        try:
            from agents.mock_responses import get_mock_analysis
            return get_mock_analysis(domain)
        except Exception:
            return {
                "agent": "analysis",
                "domain": domain,
                "severity": 5,
                "severity_label": "Medium",
                "severity_reasoning": "Fallback analysis due to LLM error.",
                "time_horizon": "medium_term",
                "kpis_affected": [],
                "total_impact": {
                    "financial_pkr": None,
                    "operational": "System operational in fallback state.",
                    "human": None,
                    "reputational": "low"
                },
                "affected_parties": [],
                "second_order_effects": [],
                "reasoning_chain": ["LLM fallback triggered"],
                "data_gaps": []
            }

    @retry(times=2, delay=2.0)
    async def _call_llm(self, signals: dict, domain: str) -> dict:
        if DEMO_MODE or not GEMINI_API_KEY or GEMINI_API_KEY.startswith("AIzaSy_mock"):
            import asyncio
            await asyncio.sleep(1.2)
            return self._get_mock_response(domain)

        if domain not in DOMAIN_ANALYSIS_INSTRUCTIONS:
            raise ValueError(
                f"Unknown domain '{domain}'. "
                f"Valid domains: {list(DOMAIN_ANALYSIS_INSTRUCTIONS.keys())}"
            )

        system = (
            ANALYSIS_BASE_SYSTEM_PROMPT
            + "\n\n# DOMAIN-SPECIFIC INSTRUCTIONS\n"
            + DOMAIN_ANALYSIS_INSTRUCTIONS[domain]
        )
        user_message = (
            f"Analyse these extracted signals:\n\n"
            f"SIGNALS:\n{json.dumps(signals, indent=2)}"
        )

        try:
            return await call_gemini(
                system_prompt=system,
                user_message=user_message,
                model=self.model,
                temperature=0.3,
                expect_json=True,
            )
        except Exception as e:
            import logging
            logging.warning(f"Gemini call failed: {e}. Using mock response.")
            return self._get_mock_response(domain)

    async def run(self, signals: dict, domain: str, *args, **kwargs) -> dict:
        session_id = kwargs.get("session_id")
        if not session_id and args:
            for arg in args:
                if isinstance(arg, str):
                    session_id = arg
                    break
        session_id = session_id or getattr(self, "session_id", None) or "session-default"
        logger = SessionLogger(session_id)
        logger.log("analysis_agent", "start", {"domain": domain, "timestamp": now_iso()})

        start_time = time.time()
        result = await self._call_llm(signals, domain)
        duration = time.time() - start_time

        logger.log(
            "analysis_agent",
            "complete",
            {"domain": domain, "duration_seconds": round(duration, 3), "timestamp": now_iso()},
        )

        result["model_used"] = MODELS["analysis"]
        result["agent_display_name"] = "Analysis Agent"

        return result
