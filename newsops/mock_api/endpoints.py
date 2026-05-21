from datetime import datetime, timezone, timedelta
from typing import List, Optional

import smtplib
from email.mime.text import MIMEText
import asyncio

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from database.db import get_db
from database.models import AnalysisSession, AgentArtifact
from mock_api.state_store import get_state, update_state
from utils.helpers import generate_uuid, now_iso
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

router = APIRouter(prefix="/api", tags=["Mock API"])


def _expiry_date(duration_days: int) -> str:
    return (
        datetime.now(timezone.utc) + timedelta(days=duration_days)
    ).isoformat().replace("+00:00", "Z")


# ── Logistics ─────────────────────────────────────────────────────────────────

class LogisticsPricingUpdateBody(BaseModel):
    route_id: str
    price_delta_pct: float
    effective_date: str
    session_id: str


@router.post("/logistics/pricing/update")
async def logistics_pricing_update(body: LogisticsPricingUpdateBody):
    old = get_state("logistics")["delivery_price_per_kg"]
    new_price = round(old * (1 + body.price_delta_pct / 100), 4)
    update_state("logistics", {"delivery_price_per_kg": new_price, "last_pricing_update": now_iso()})
    return {
        "status": "ok",
        "old_price": old,
        "new_price": new_price,
        "price_delta_pct": body.price_delta_pct,
        "routes_affected": 1,
        "effective_date": body.effective_date,
    }


class LogisticsRouteOptimizeBody(BaseModel):
    current_route_id: str
    optimization_target: str
    session_id: str


@router.post("/logistics/routes/optimize")
async def logistics_routes_optimize(_body: LogisticsRouteOptimizeBody):
    savings_pct = 8.5
    old_cost = get_state("logistics")["fuel_cost_ratio_pct"]
    new_cost = round(old_cost * (1 - savings_pct / 100), 2)
    update_state("logistics", {"fuel_cost_ratio_pct": new_cost})
    return {
        "status": "ok",
        "old_fuel_ratio": old_cost,
        "new_fuel_ratio": new_cost,
        "savings_pct": savings_pct,
    }


class NotificationsBulkSendBody(BaseModel):
    template: str
    recipient_list: List[str]
    effective_date: str
    session_id: str


@router.post("/notifications/bulk_send")
async def notifications_bulk_send(body: NotificationsBulkSendBody):
    # Generate rich notification content per recipient
    notifications = []
    for r in (body.recipient_list or ["Operations Team"]):
        notifications.append({
            "recipient": r,
            "channel": "email",
            "subject": f"[AI Ops] Action Notification — {body.template.replace('_',' ').title()}",
            "message_preview": (
                f"Dear {r}, your attention is required. "
                f"An automated action has been triggered based on AI analysis. "
                f"Effective date: {body.effective_date}. "
                f"Please review your dashboard immediately."
            ),
            "status": "delivered",
            "timestamp": now_iso(),
        })
    
    update_state("logistics", {"buyers_notified": len(body.recipient_list or [])})
    
    return {
        "status": "ok",
        "sent_count": len(notifications),
        "failed_count": 0,
        "notifications": notifications,
        "channels_used": ["email", "sms", "app"],
        "preview": notifications[0]["message_preview"] if notifications else "",
    }


class ProcurementHedgeBody(BaseModel):
    commodity: str
    volume_litres: float
    duration_days: int
    current_rate: float
    session_id: str


@router.post("/procurement/hedge")
async def procurement_hedge(body: ProcurementHedgeBody):
    return {
        "status": "ok",
        "locked_rate": body.current_rate,
        "volume": body.volume_litres,
        "expiry_date": _expiry_date(body.duration_days),
        "savings_estimate_pkr": round(body.volume_litres * 0.05 * body.current_rate, 0),
    }


class WarehouseReallocationBody(BaseModel):
    source_warehouse_id: str
    target_warehouse_id: str
    sku_list: List[str]
    session_id: str


@router.post("/warehouse/reallocation")
async def warehouse_reallocation(body: WarehouseReallocationBody):
    old_dist = get_state("logistics")["avg_delivery_distance_km"]
    new_dist = round(old_dist * 0.88, 1)
    update_state("logistics", {"avg_delivery_distance_km": new_dist})
    return {
        "status": "ok",
        "skus_moved": len(body.sku_list),
        "old_avg_distance_km": old_dist,
        "new_avg_distance_km": new_dist,
    }


# ── Business ──────────────────────────────────────────────────────────────────

class CrmCampaignCreateBody(BaseModel):
    region: str
    discount_pct: float
    target_segment: str
    duration_days: int
    budget_pkr: float
    session_id: str


@router.post("/crm/campaigns/create")
async def crm_campaigns_create(body: CrmCampaignCreateBody):
    campaign_id = generate_uuid()
    reach = round(body.budget_pkr * 3.2)
    old_campaigns = get_state("business")["active_campaigns"]
    update_state("business", {"active_campaigns": old_campaigns + 1, "campaign_reach": reach})
    return {
        "status": "ok",
        "campaign_id": campaign_id,
        "region": body.region,
        "reach_estimate": reach,
        "discount_pct": body.discount_pct,
        "duration_days": body.duration_days,
    }


class CatalogPricingUpdateBody(BaseModel):
    region: str
    category: str
    price_delta_pct: float
    effective_date: str
    session_id: str


@router.post("/catalog/pricing/update")
async def catalog_pricing_update(body: CatalogPricingUpdateBody):
    old_rev = get_state("business")["regional_revenue_pkr"]
    projected = round(old_rev * (1 + body.price_delta_pct / 100))
    update_state("business", {"regional_revenue_pkr": projected})
    return {
        "status": "ok",
        "region": body.region,
        "skus_updated": 47,
        "old_avg_price_pkr": round(old_rev / 1240),
        "new_avg_price_pkr": round(projected / 1240),
        "effective_date": body.effective_date,
    }


class CrmWorkflowTriggerBody(BaseModel):
    workflow_id: str
    segment: str
    message_template: str
    session_id: str


@router.post("/crm/workflows/trigger")
async def crm_workflows_trigger(body: CrmWorkflowTriggerBody):
    old_churn = get_state("business")["churn_risk_customers"]
    update_state("business", {"churn_risk_customers": round(old_churn * 0.7)})
    return {
        "status": "ok",
        "workflow_id": body.workflow_id,
        "customers_targeted": old_churn,
        "messages_queued": old_churn,
    }


class CrmTasksBulkCreateBody(BaseModel):
    account_list: List[str]
    task_type: str
    due_date: str
    session_id: str


@router.post("/crm/tasks/bulk_create")
async def crm_tasks_bulk_create(body: CrmTasksBulkCreateBody):
    return {
        "status": "ok",
        "tasks_created": len(body.account_list),
        "task_type": body.task_type,
        "assigned_to": "sales_team",
        "due_date": body.due_date,
    }


class ReportGenerateBody(BaseModel):
    report_type: str
    data_source: str
    recipients: List[str]
    session_id: str


@router.post("/reports/generate")
async def reports_generate(body: ReportGenerateBody):
    return {
        "status": "ok",
        "report_id": generate_uuid(),
        "report_type": body.report_type,
        "sent_to_count": len(body.recipients),
        "report_url": f"/api/reports/{generate_uuid()}",
    }


# ── Finance ───────────────────────────────────────────────────────────────────

class FinancePricingExportUpdateBody(BaseModel):
    currency_pair: str
    rate_delta_pct: float
    affected_contracts: List[str]
    effective_date: str
    session_id: str


@router.post("/finance/pricing/export_update")
async def finance_pricing_export_update(body: FinancePricingExportUpdateBody):
    old_rate = get_state("finance")["usd_pkr_rate"]
    new_rate = round(old_rate * (1 + body.rate_delta_pct / 100), 2)
    update_state("finance", {
        "usd_pkr_rate": new_rate,
        "contracts_repriced": len(body.affected_contracts),
    })
    return {
        "status": "ok",
        "old_rate": old_rate,
        "new_rate": new_rate,
        "contracts_repriced": len(body.affected_contracts),
    }


class FinanceHedgingBookBody(BaseModel):
    currency_pair: str
    amount_usd: float
    duration_days: int
    rate: float
    session_id: str


@router.post("/finance/hedging/book")
async def finance_hedging_book(body: FinanceHedgingBookBody):
    update_state("finance", {"hedged_amount_usd": body.amount_usd})
    return {
        "status": "ok",
        "contract_id": generate_uuid(),
        "locked_rate": body.rate,
        "amount_usd": body.amount_usd,
        "expiry_date": _expiry_date(body.duration_days),
        "hedge_cost_pkr": round(body.amount_usd * body.rate * 0.015),
    }


class PortfolioRebalanceFlagBody(BaseModel):
    affected_instruments: List[str]
    reason: str
    urgency: str
    session_id: str


@router.post("/portfolio/rebalance/flag")
async def portfolio_rebalance_flag(body: PortfolioRebalanceFlagBody):
    update_state("finance", {"portfolio_flags": len(body.affected_instruments)})
    return {
        "status": "ok",
        "instruments_flagged": len(body.affected_instruments),
        "urgency": body.urgency,
        "alert_sent_to": "portfolio_manager",
    }


class FinanceCostingRecalculateBody(BaseModel):
    fx_rate: float
    affected_po_list: List[str]
    session_id: str


@router.post("/finance/costing/recalculate")
async def finance_costing_recalculate(body: FinanceCostingRecalculateBody):
    return {
        "status": "ok",
        "pos_updated": len(body.affected_po_list),
        "new_fx_rate": body.fx_rate,
        "total_cost_delta_pkr": round(len(body.affected_po_list) * body.fx_rate * 1250),
    }


# ── Policy ────────────────────────────────────────────────────────────────────

class ComplianceTasksGenerateBody(BaseModel):
    regulation_id: str
    affected_departments: List[str]
    deadline: str
    session_id: str


@router.post("/compliance/tasks/generate")
async def compliance_tasks_generate(body: ComplianceTasksGenerateBody):
    tasks = len(body.affected_departments) * 3
    update_state("policy", {
        "compliance_tasks_open": tasks,
        "departments_notified": len(body.affected_departments),
    })
    return {
        "status": "ok",
        "tasks_created": tasks,
        "departments_notified": len(body.affected_departments),
        "deadline": body.deadline,
    }


class PricingPolicyUpdateBody(BaseModel):
    policy_ref: str
    affected_categories: List[str]
    cost_delta_pct: float
    session_id: str


@router.post("/pricing/policy_update")
async def pricing_policy_update(body: PricingPolicyUpdateBody):
    update_state("policy", {"affected_categories": len(body.affected_categories)})
    return {
        "status": "ok",
        "categories_updated": len(body.affected_categories),
        "policy_ref": body.policy_ref,
        "cost_delta_pct": body.cost_delta_pct,
    }


class CommunicationsDraftBody(BaseModel):
    template: str
    audience: str
    key_changes: List[str]
    session_id: str


@router.post("/communications/draft")
async def communications_draft(body: CommunicationsDraftBody):
    update_state("policy", {"notices_drafted": 1})
    preview = f"Notice regarding {body.key_changes[0]}" if body.key_changes else "Notice regarding policy update"
    return {
        "status": "ok",
        "draft_id": generate_uuid(),
        "audience": body.audience,
        "preview_text": preview,
        "status_detail": "ready_for_legal_review",
    }


class TaskCreateBody(BaseModel):
    task_type: str
    priority: str
    summary: str
    session_id: str
    assignee_team: Optional[str] = "general"


@router.post("/tasks/create")
async def tasks_create(body: TaskCreateBody):
    return {
        "status": "ok",
        "task_id": generate_uuid(),
        "task_type": body.task_type,
        "priority": body.priority,
        "assigned_to": body.assignee_team,
        "created_at": now_iso(),
    }


class ContractFlagReviewBody(BaseModel):
    policy_ref: str
    affected_contract_ids: List[str]
    reason: str
    session_id: str


@router.post("/contracts/flag_for_review")
async def contracts_flag_for_review(body: ContractFlagReviewBody):
    update_state("policy", {"contracts_flagged": len(body.affected_contract_ids)})
    return {
        "status": "ok",
        "contracts_flagged": len(body.affected_contract_ids),
        "reason": body.reason,
    }


# ── Healthcare ────────────────────────────────────────────────────────────────

class ProcurementEmergencyOrderBody(BaseModel):
    item_id: str
    quantity: int
    urgency: str
    supplier_shortlist: List[str]
    session_id: str


@router.post("/procurement/emergency_order")
async def procurement_emergency_order(body: ProcurementEmergencyOrderBody):
    old_pos = get_state("healthcare")["emergency_pos_open"]
    current_avail = get_state("healthcare")["drug_availability_pct"]
    update_state("healthcare", {
        "emergency_pos_open": old_pos + 1,
        "drug_availability_pct": min(99.0, current_avail + 5.0),
    })
    supplier = body.supplier_shortlist[0] if body.supplier_shortlist else "pending"
    return {
        "status": "ok",
        "po_number": f"EPO-{generate_uuid()[:8].upper()}",
        "item_id": body.item_id,
        "quantity": body.quantity,
        "supplier_confirmed": supplier,
        "eta_days": 3,
    }


class ClinicalProtocolsActivateBody(BaseModel):
    protocol_id: str
    drug_id: str
    affected_facilities: List[str]
    session_id: str


@router.post("/clinical/protocols/activate")
async def clinical_protocols_activate(body: ClinicalProtocolsActivateBody):
    return {
        "status": "ok",
        "protocol_id": body.protocol_id,
        "facilities_count": len(body.affected_facilities),
        "staff_notified": len(body.affected_facilities) * 12,
    }


class NotificationsClinicalAlertBody(BaseModel):
    alert_type: str
    affected_drug_or_procedure: str
    guidance: str
    recipients: List[str]
    session_id: str


@router.post("/notifications/clinical_alert")
async def notifications_clinical_alert(body: NotificationsClinicalAlertBody):
    update_state("healthcare", {"staff_alerts_sent": len(body.recipients)})
    return {
        "status": "ok",
        "sent_to": len(body.recipients),
        "acknowledged_count": round(len(body.recipients) * 0.85),
    }


class ClinicalFormularyUpdateBody(BaseModel):
    drug_id: str
    change_type: str
    alternative_drug_id: str
    effective_date: str
    session_id: str


@router.post("/clinical/formulary/update")
async def clinical_formulary_update(body: ClinicalFormularyUpdateBody):
    current = get_state("healthcare")["formulary_updates"]
    update_state("healthcare", {"formulary_updates": current + 1})
    return {
        "status": "ok",
        "drug_id": body.drug_id,
        "change_type": body.change_type,
        "alternative": body.alternative_drug_id,
        "effective_date": body.effective_date,
        "pharmacists_notified": 24,
    }


# ── Urban ─────────────────────────────────────────────────────────────────────

class OperationsDispatchBody(BaseModel):
    fault_location: str
    crew_type: str
    priority: str
    eta_minutes: int
    session_id: str


@router.post("/operations/dispatch")
async def operations_dispatch(body: OperationsDispatchBody):
    old_crews = get_state("urban")["crews_dispatched"]
    update_state("urban", {"crews_dispatched": old_crews + 1})
    return {
        "status": "ok",
        "crew_id": f"CREW-{generate_uuid()[:6].upper()}",
        "fault_location": body.fault_location,
        "eta_minutes": body.eta_minutes,
        "tracking_id": generate_uuid(),
    }


class InfrastructureContingencyActivateBody(BaseModel):
    zone_id: str
    utility_type: str
    contingency_source: str
    duration_hours: int
    session_id: str


@router.post("/infrastructure/contingency/activate")
async def infrastructure_contingency_activate(body: InfrastructureContingencyActivateBody):
    current_zones = get_state("urban")["contingency_zones_active"]
    update_state("urban", {
        "contingency_zones_active": current_zones + 1,
        "population_affected": 15000,
    })
    return {
        "status": "ok",
        "zone_id": body.zone_id,
        "utility_type": body.utility_type,
        "source": body.contingency_source,
        "duration_hours": body.duration_hours,
        "population_served": 15000,
    }


class CommunicationsPublicAdvisoryBody(BaseModel):
    zone_id: str
    issue_type: str
    severity: str
    guidance_text: str
    channels: List[str]
    session_id: str


@router.post("/communications/public_advisory")
async def communications_public_advisory(body: CommunicationsPublicAdvisoryBody):
    old_adv = get_state("urban")["advisories_published"]
    update_state("urban", {"advisories_published": old_adv + 1})
    return {
        "status": "ok",
        "advisory_id": generate_uuid(),
        "channels_reached": len(body.channels),
        "estimated_reach": 45000,
    }


class TrafficRerouteBody(BaseModel):
    affected_segment_id: str
    alternate_route_id: str
    duration_hours: int
    session_id: str


@router.post("/traffic/reroute")
async def traffic_reroute(body: TrafficRerouteBody):
    current = get_state("urban")["traffic_reroutes_active"]
    update_state("urban", {"traffic_reroutes_active": current + 1})
    return {
        "status": "ok",
        "segment_id": body.affected_segment_id,
        "alternate_route": body.alternate_route_id,
        "vehicles_affected": 3200,
        "delay_reduction_minutes": 18,
    }


# ── Notification Log ──────────────────────────────────────────────────────────

class NotificationsLogBody(BaseModel):
    recipients: List[str]
    message_template: str
    simulated: bool
    session_id: str


@router.post("/notifications/log")
async def notifications_log(body: NotificationsLogBody):
    return {
        "status": "ok",
        "log_id": generate_uuid(),
        "notifications": [
            {
                "recipient": r,
                "channel": "app",
                "message_preview": body.message_template[:100],
                "status": "delivered",
                "timestamp": now_iso(),
            }
            for r in body.recipients
        ],
    }


# ── Email and SMS Drafts ──────────────────────────────────────────────────────

class EmailDraftBody(BaseModel):
    action_type: str
    domain: str
    insight: str
    recipients: List[str]
    session_id: str

def _send_real_email(recipient: str, subject: str, body: str):
    if not SMTP_HOST or not SMTP_USER:
        return False
    if "@" not in recipient:
        return False
        
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = recipient
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

@router.post("/notifications/email_draft")
async def notifications_email_draft(body: EmailDraftBody):
    action_str = body.action_type.replace('_', ' ').title()
    subject = f"[Antigravity AI Ops] Action Required: {action_str}"
    
    body_text = f"""
Dear Team,

Our AI analysis system has detected an important business signal requiring immediate attention.

INSIGHT SUMMARY:
{body.insight}

RECOMMENDED ACTION:
{action_str} has been automatically initiated based on AI analysis.

IMPACT ASSESSMENT:
- Domain: {body.domain.title()}
- Severity: High Priority
- Action Status: Executed Successfully
- Timestamp: {now_iso()}

This notification was automatically generated by Antigravity AI Ops.
Please review the dashboard for full analysis details.

Best regards,
Antigravity AI Ops System
"""

    notifications = []
    for r in body.recipients:
        # Try to send real email if configured
        try:
            # We run the synchronous SMTP call in a thread to prevent blocking
            email_sent = await asyncio.to_thread(_send_real_email, r, subject, body_text)
        except Exception:
            email_sent = False
            
        notifications.append({
            "recipient": r,
            "channel": "email",
            "subject": subject,
            "body_preview": body_text[:200] + "...",
            "full_body": body_text,
            "status": "delivered" if email_sent or not SMTP_HOST else "failed",
            "real_email_sent": email_sent,
            "timestamp": now_iso(),
            "message_id": f"MSG-{generate_uuid()[:8].upper()}"
        })

    return {
        "status": "ok",
        "emails_sent": len([n for n in notifications if n["status"] == "delivered"]),
        "subject": subject,
        "preview": body_text[:150],
        "notifications": notifications
    }

class SmsDraftBody(BaseModel):
    insight: str
    action_type: str
    recipients: List[str]
    session_id: str

@router.post("/notifications/sms_draft")
async def notifications_sms_draft(body: SmsDraftBody):
    action_str = body.action_type.replace('_', ' ')
    sms_text = f"[AI Ops Alert] {body.insight[:80]}... Action taken: {action_str}. Check dashboard."
    
    return {
        "status": "ok",
        "sms_sent": len(body.recipients),
        "message": sms_text,
        "char_count": len(sms_text),
        "recipients": body.recipients
    }

# ── Workflows ─────────────────────────────────────────────────────────────────

class WorkflowTriggerBody(BaseModel):
    workflow_id: str
    trigger_reason: str
    domain: str
    session_id: str

@router.post("/workflows/trigger")
async def workflows_trigger(body: WorkflowTriggerBody):
    workflow_steps = {
      "business": [
        {"step": 1, "name": "Validate trigger conditions",   "status": "complete", "duration_ms": 120},
        {"step": 2, "name": "Fetch customer segment data",   "status": "complete", "duration_ms": 340},
        {"step": 3, "name": "Apply discount rules",          "status": "complete", "duration_ms": 89},
        {"step": 4, "name": "Queue campaign notifications",  "status": "complete", "duration_ms": 210},
        {"step": 5, "name": "Update CRM records",            "status": "complete", "duration_ms": 156},
        {"step": 6, "name": "Log execution trace",           "status": "complete", "duration_ms": 45},
      ],
      "logistics": [
        {"step": 1, "name": "Validate route data",           "status": "complete", "duration_ms": 90},
        {"step": 2, "name": "Calculate new pricing",         "status": "complete", "duration_ms": 180},
        {"step": 3, "name": "Update pricing table",          "status": "complete", "duration_ms": 120},
        {"step": 4, "name": "Notify affected buyers",        "status": "complete", "duration_ms": 310},
        {"step": 5, "name": "Log state change",              "status": "complete", "duration_ms": 55},
      ],
      "finance": [
        {"step": 1, "name": "Check exposure limits",         "status": "complete", "duration_ms": 145},
        {"step": 2, "name": "Calculate hedge amount",        "status": "complete", "duration_ms": 220},
        {"step": 3, "name": "Book forward contract",         "status": "complete", "duration_ms": 390},
        {"step": 4, "name": "Update portfolio records",      "status": "complete", "duration_ms": 167},
        {"step": 5, "name": "Send risk alert",               "status": "complete", "duration_ms": 88},
      ],
    }

    steps = workflow_steps.get(body.domain, workflow_steps["business"])
    total_ms = sum(s["duration_ms"] for s in steps)

    return {
      "status": "ok",
      "workflow_id": body.workflow_id,
      "workflow_name": f"{body.domain.title()} Action Workflow",
      "trigger_reason": body.trigger_reason,
      "total_steps": len(steps),
      "completed_steps": len(steps),
      "total_duration_ms": total_ms,
      "steps": steps,
      "final_status": "completed_successfully",
      "timestamp": now_iso()
    }


# ── Session Trace ─────────────────────────────────────────────────────────────

@router.get("/session/{session_id}/trace")
async def session_trace(session_id: str):
    async with get_db() as db:
        session_result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        session = session_result.scalar_one_or_none()

        artifacts_result = await db.execute(
            select(AgentArtifact)
            .where(AgentArtifact.session_id == session_id)
            .order_by(AgentArtifact.created_at.asc())
        )
        artifacts = list(artifacts_result.scalars().all())

    session_dict = {}
    if session:
        session_dict = {
            "id": session.id,
            "domain": session.domain,
            "input_type": session.input_type,
            "input_preview": session.input_preview,
            "status": session.status,
            "error_detail": session.error_detail,
            "duration_seconds": session.duration_seconds,
            "created_at": session.created_at.isoformat() if session.created_at else None,
        }

    artifacts_list = [
        {
            "id": a.id,
            "session_id": a.session_id,
            "agent_name": a.agent_name,
            "artifact_type": a.artifact_type,
            "content": a.content,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "duration_seconds": a.duration_seconds,
        }
        for a in artifacts
    ]

    return {
        "session": session_dict,
        "artifacts": artifacts_list,
        "total_artifacts": len(artifacts_list),
        "pipeline_duration_seconds": session.duration_seconds if session else None,
    }
