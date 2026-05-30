"""
scripts/demo_seed.py
====================
Inserts 3 pre-completed sample sessions into the NewsOps SQLite database so
the history screen is populated on first launch.

Usage (run from the newsops/ directory):
    python scripts/demo_seed.py

Safe to run multiple times — checks for an existing session with the same
preview text before inserting, so it won't duplicate rows.
"""

import asyncio
import sys
import os

# Make sure imports resolve from the project root (newsops/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import create_tables, get_db
from database.models import (
    AnalysisSession,
    save_session,
    save_artifact,
    save_state_log,
    update_session_status,
)
from utils.helpers import now_iso
from sqlalchemy import select
import uuid


# ---------------------------------------------------------------------------
# Sample data — one session per domain
# ---------------------------------------------------------------------------

DEMO_SESSIONS = [
    # ── 1. Finance ──────────────────────────────────────────────────────────
    {
        "session": {
            "domain": "finance",
            "input_type": "text",
            "input_preview": (
                "State Bank of Pakistan raises benchmark interest rate by 150 "
                "basis points to 22.5%. The Monetary Policy Committee cited "
                "rising inflation at 28.3% and PKR depreciation of 12% against "
                "USD this quarter. KSE-100 fell 890 points immediately after "
                "the announcement."
            ),
            "status": "complete",
            "duration_seconds": 18.42,
        },
        "signals": {
            "mock_mode_active": False,
            "facts": [
                {"text": "SBP raised benchmark rate by 150 bps to 22.5%", "confidence": 0.97},
                {"text": "KSE-100 fell 890 points post-announcement", "confidence": 0.95},
                {"text": "Inflation at 28.3%; PKR down 12% vs USD", "confidence": 0.93},
            ],
            "entities": ["SBP", "KSE-100", "PKR", "USD", "MPC"],
            "sentiment": "negative",
            "urgency": 8,
        },
        "context": {
            "additional_context": (
                "The MPC decision aligns with IMF fiscal consolidation targets. "
                "Regional central banks (Turkey, Egypt) have followed similar "
                "tightening paths in 2024."
            ),
            "corroboration": "confirmed",
            "sources": ["Bloomberg", "Dawn", "SBP Press Release"],
        },
        "impact": {
            "severity": 8,
            "severity_label": "High",
            "total_impact": {
                "revenue_impact_pkr": -12_500_000,
                "cost_impact_pkr": 8_200_000,
                "net_impact_pkr": -20_700_000,
            },
            "kpis_affected": [
                {
                    "kpi": "Lending Rate",
                    "current_value": 21.0,
                    "projected_value": 23.5,
                    "current_unit": "%",
                    "direction": "up",
                    "delta": 2.5,
                    "delta_pct": 11.9,
                },
                {
                    "kpi": "KSE-100 Index",
                    "current_value": 72133,
                    "projected_value": 69800,
                    "current_unit": "points",
                    "direction": "down",
                    "delta": -2333,
                    "delta_pct": -3.2,
                },
            ],
        },
        "actions": {
            "actions": [
                {
                    "action_type": "hedge_fx_exposure",
                    "description": "Hedge PKR/USD exposure via forward contracts for next 90 days.",
                    "priority": 1,
                    "estimated_savings_pkr": 6_000_000,
                    "timeline": "48 hours",
                },
                {
                    "action_type": "refinance_variable_loans",
                    "description": "Convert variable-rate facilities to fixed before next MPC meeting.",
                    "priority": 2,
                    "estimated_savings_pkr": 3_500_000,
                    "timeline": "1 week",
                },
                {
                    "action_type": "defer_capex",
                    "description": "Postpone non-critical capital expenditure by one quarter.",
                    "priority": 3,
                    "estimated_savings_pkr": 2_000_000,
                    "timeline": "2 weeks",
                },
            ]
        },
        "exec_log": {
            "execution_status": "completed",
            "state_before": {"lending_rate": 21.0, "kse100": 72133},
            "state_after":  {"lending_rate": 23.5, "kse100": 69800},
            "delta": {"lending_rate": +2.5, "kse100": -2333},
            "notifications_sent": [
                {"channel": "email", "recipient": "cfo@company.com", "status": "sent"},
                {"channel": "sms",   "recipient": "+92-300-0000001", "status": "sent"},
            ],
        },
    },

    # ── 2. Logistics ─────────────────────────────────────────────────────────
    {
        "session": {
            "domain": "logistics",
            "input_type": "text",
            "input_preview": (
                "Karachi Port Trust (KPT) reports 47 vessels awaiting berth as "
                "port congestion reaches a 3-year high. Average container dwell "
                "time is now 11.2 days vs the target of 4 days. Container "
                "throughput dropped 22% this week to 18,400 TEUs."
            ),
            "status": "complete",
            "duration_seconds": 21.07,
        },
        "signals": {
            "mock_mode_active": False,
            "facts": [
                {"text": "47 vessels awaiting berth at KPT — 3-year high", "confidence": 0.96},
                {"text": "Container dwell time 11.2 days vs 4-day target", "confidence": 0.94},
                {"text": "Throughput down 22% to 18,400 TEUs", "confidence": 0.92},
            ],
            "entities": ["KPT", "NLC", "Fauji Foundation", "Gwadar"],
            "sentiment": "negative",
            "urgency": 9,
        },
        "context": {
            "additional_context": (
                "Seasonal monsoon delays and customs scanner breakdown at Gate-7 "
                "are compounding the congestion. NLC fleet diversion to Gwadar "
                "has been authorized by Ministry of Maritime Affairs."
            ),
            "corroboration": "confirmed",
            "sources": ["KPT Official Notice", "NLC Dispatch Board", "Dawn Business"],
        },
        "impact": {
            "severity": 9,
            "severity_label": "Critical",
            "total_impact": {
                "revenue_impact_pkr": -45_000_000,
                "cost_impact_pkr": 18_000_000,
                "net_impact_pkr": -63_000_000,
            },
            "kpis_affected": [
                {
                    "kpi": "Freight Cost per TEU",
                    "current_value": 850,
                    "projected_value": 1003,
                    "current_unit": "USD",
                    "direction": "up",
                    "delta": 153,
                    "delta_pct": 18.0,
                },
                {
                    "kpi": "Dwell Time",
                    "current_value": 11.2,
                    "projected_value": 6.5,
                    "current_unit": "days",
                    "direction": "down",
                    "delta": -4.7,
                    "delta_pct": -41.9,
                },
            ],
        },
        "actions": {
            "actions": [
                {
                    "action_type": "divert_to_gwadar",
                    "description": "Redirect 30% of inbound TEUs to Gwadar Port and use NLC rail link.",
                    "priority": 1,
                    "estimated_savings_pkr": 22_000_000,
                    "timeline": "24 hours",
                },
                {
                    "action_type": "expedite_customs_clearance",
                    "description": "Deploy additional Customs officers for priority cargo lanes.",
                    "priority": 2,
                    "estimated_savings_pkr": 10_000_000,
                    "timeline": "48 hours",
                },
            ]
        },
        "exec_log": {
            "execution_status": "completed",
            "state_before": {"dwell_days": 11.2, "throughput_teus": 18400},
            "state_after":  {"dwell_days": 6.5,  "throughput_teus": 23500},
            "delta": {"dwell_days": -4.7, "throughput_teus": +5100},
            "notifications_sent": [
                {"channel": "email", "recipient": "logistics@company.com", "status": "sent"},
                {"channel": "email", "recipient": "procurement@company.com", "status": "sent"},
            ],
        },
    },

    # ── 3. Healthcare ────────────────────────────────────────────────────────
    {
        "session": {
            "domain": "healthcare",
            "input_type": "text",
            "input_preview": (
                "DRAP has confirmed a critical shortage of Insulin Glargine "
                "100IU/ml at 14 public hospitals across Lahore and Rawalpindi. "
                "An estimated 12,000 insulin-dependent diabetic patients are at "
                "immediate risk. Three pharma manufacturers suspended production."
            ),
            "status": "complete",
            "duration_seconds": 19.83,
        },
        "signals": {
            "mock_mode_active": False,
            "facts": [
                {"text": "Critical shortage of Insulin Glargine at 14 public hospitals", "confidence": 0.98},
                {"text": "12,000 insulin-dependent patients at immediate risk", "confidence": 0.97},
                {"text": "Getz Pharma, Searle, Highnoon suspended production", "confidence": 0.95},
            ],
            "entities": ["DRAP", "NHSRC", "WHO Pakistan", "Getz Pharma", "Searle", "Highnoon"],
            "sentiment": "negative",
            "urgency": 10,
        },
        "context": {
            "additional_context": (
                "API (Active Pharmaceutical Ingredient) import restrictions by "
                "SBP forex controls are the root cause. WHO Pakistan office has "
                "been formally notified and emergency procurement waiver granted."
            ),
            "corroboration": "confirmed",
            "sources": ["DRAP Circular 2024-HC-047", "WHO Pakistan Statement", "Geo Health"],
        },
        "impact": {
            "severity": 10,
            "severity_label": "Critical",
            "total_impact": {
                "revenue_impact_pkr": 0,
                "cost_impact_pkr": 35_000_000,
                "net_impact_pkr": -35_000_000,
            },
            "kpis_affected": [
                {
                    "kpi": "Drug Availability Index",
                    "current_value": 34,
                    "projected_value": 78,
                    "current_unit": "%",
                    "direction": "up",
                    "delta": 44,
                    "delta_pct": 129.4,
                },
                {
                    "kpi": "Patients at Risk",
                    "current_value": 12000,
                    "projected_value": 1200,
                    "current_unit": "patients",
                    "direction": "down",
                    "delta": -10800,
                    "delta_pct": -90.0,
                },
            ],
        },
        "actions": {
            "actions": [
                {
                    "action_type": "emergency_import_authorization",
                    "description": "Fast-track NHSRC emergency import authorization for Insulin Glargine from Turkey/China.",
                    "priority": 1,
                    "estimated_savings_pkr": 0,
                    "timeline": "12 hours",
                },
                {
                    "action_type": "activate_strategic_reserve",
                    "description": "Release strategic pharmaceutical reserve stocks held at NHSRC Islamabad warehouse.",
                    "priority": 2,
                    "estimated_savings_pkr": 0,
                    "timeline": "6 hours",
                },
            ]
        },
        "exec_log": {
            "execution_status": "completed",
            "state_before": {"drug_availability_pct": 34, "patients_at_risk": 12000},
            "state_after":  {"drug_availability_pct": 78, "patients_at_risk": 1200},
            "delta": {"drug_availability_pct": +44, "patients_at_risk": -10800},
            "notifications_sent": [
                {"channel": "email", "recipient": "health@company.com",   "status": "sent"},
                {"channel": "email", "recipient": "nhsrc@company.com",    "status": "sent"},
                {"channel": "sms",   "recipient": "+92-300-0000002",      "status": "sent"},
            ],
        },
    },
]


# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------

async def session_preview_exists(preview: str) -> bool:
    """Return True if a session with this input_preview already exists."""
    async with get_db() as db:
        result = await db.execute(
            select(AnalysisSession).where(
                AnalysisSession.input_preview == preview
            )
        )
        return result.scalar_one_or_none() is not None


async def seed_session(data: dict) -> str:
    """Insert one complete demo session and return its session_id."""
    session_id = str(uuid.uuid4())
    sess = data["session"]

    # 1. Create the session row
    await save_session({
        "id":            session_id,
        "domain":        sess["domain"],
        "input_type":    sess["input_type"],
        "input_preview": sess["input_preview"],
        "status":        "pending",
    })

    # 2. Save all artifacts (mirrors the orchestrator pipeline order)
    task_plan = {
        "agent":             "orchestrator",
        "session_id":        session_id,
        "timestamp":         now_iso(),
        "input_type":        sess["input_type"],
        "domain":            sess["domain"],
        "agents_to_spawn":   ["ingestion", "research", "analysis", "decision", "execution"],
        "estimated_duration_seconds": sess["duration_seconds"],
    }
    await save_artifact(session_id, "orchestrator", "task_plan",   task_plan)
    await save_artifact(session_id, "ingestion",    "signals",     data["signals"])
    await save_artifact(session_id, "research",     "context",     data["context"])
    await save_artifact(session_id, "analysis",     "impact",      data["impact"])
    await save_artifact(session_id, "decision",     "actions",     data["actions"])

    # 3. Merge artifacts into master_brief (mirrors Orchestrator.merge_artifacts)
    top_action = data["actions"]["actions"][0]
    first_kpi  = data["impact"]["kpis_affected"][0]
    master_brief = {
        "agent":             "orchestrator",
        "session_id":        session_id,
        "domain":            sess["domain"],
        "timestamp":         now_iso(),
        "mock_mode_active":  False,
        "insight":           data["signals"]["facts"][0]["text"],
        "severity":          data["impact"]["severity"],
        "severity_label":    data["impact"]["severity_label"],
        "impact_summary":    data["impact"]["total_impact"],
        "kpis_affected":     data["impact"]["kpis_affected"],
        "top_action":        top_action,
        "alternative_actions": data["actions"]["actions"][1:3],
        "context":           data["context"]["additional_context"],
        "corroboration":     data["context"]["corroboration"],
        "ready_for_execution": True,
        "projected_outcome": {
            "metric":           first_kpi["kpi"],
            "current":          first_kpi["current_value"],
            "projected_30_day": first_kpi["projected_value"],
            "recovery_pct":     None,
        },
    }
    await save_artifact(session_id, "orchestrator", "master_brief", master_brief)
    await save_artifact(session_id, "execution",    "exec_log",    data["exec_log"])

    # 4. State log
    await save_state_log(
        session_id,
        sess["domain"],
        data["exec_log"]["state_before"],
        data["exec_log"]["state_after"],
        top_action["action_type"],
        data["exec_log"]["delta"],
    )

    # 5. Mark complete
    await update_session_status(
        session_id, "complete", duration=sess["duration_seconds"]
    )

    return session_id


async def main():
    print("NewsOps Demo Seed — creating sample sessions\n" + "─" * 50)

    # Ensure tables exist
    await create_tables()

    inserted = 0
    skipped  = 0

    for data in DEMO_SESSIONS:
        preview = data["session"]["input_preview"]
        domain  = data["session"]["domain"]

        if await session_preview_exists(preview):
            print(f"  ⏭  [{domain:12s}] Already exists — skipped")
            skipped += 1
            continue

        session_id = await seed_session(data)
        print(f"  ✅  [{domain:12s}] Inserted  session_id={session_id}")
        inserted += 1

    print("─" * 50)
    print(f"Done. {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    asyncio.run(main())
