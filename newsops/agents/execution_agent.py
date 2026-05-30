import asyncio
import time

from utils.logger import SessionLogger
from utils.logger import SessionLogger
from utils.helpers import compute_delta, now_iso, generate_uuid
from database.models import save_state_log
from utils.commentary_stream import push_commentary, close_stream

from mock_api.state_store import get_state
from mock_api.endpoints import (
    logistics_pricing_update, LogisticsPricingUpdateBody,
    logistics_routes_optimize, LogisticsRouteOptimizeBody,
    notifications_bulk_send, NotificationsBulkSendBody,
    procurement_hedge, ProcurementHedgeBody,
    warehouse_reallocation, WarehouseReallocationBody,
    crm_campaigns_create, CrmCampaignCreateBody,
    catalog_pricing_update, CatalogPricingUpdateBody,
    crm_workflows_trigger, CrmWorkflowTriggerBody,
    crm_tasks_bulk_create, CrmTasksBulkCreateBody,
    reports_generate, ReportGenerateBody,
    finance_pricing_export_update, FinancePricingExportUpdateBody,
    finance_hedging_book, FinanceHedgingBookBody,
    portfolio_rebalance_flag, PortfolioRebalanceFlagBody,
    finance_costing_recalculate, FinanceCostingRecalculateBody,
    compliance_tasks_generate, ComplianceTasksGenerateBody,
    pricing_policy_update, PricingPolicyUpdateBody,
    communications_draft, CommunicationsDraftBody,
    tasks_create, TaskCreateBody,
    contracts_flag_for_review, ContractFlagReviewBody,
    procurement_emergency_order, ProcurementEmergencyOrderBody,
    clinical_protocols_activate, ClinicalProtocolsActivateBody,
    notifications_clinical_alert, NotificationsClinicalAlertBody,
    clinical_formulary_update, ClinicalFormularyUpdateBody,
    operations_dispatch, OperationsDispatchBody,
    infrastructure_contingency_activate, InfrastructureContingencyActivateBody,
    communications_public_advisory, CommunicationsPublicAdvisoryBody,
    traffic_reroute, TrafficRerouteBody,
    notifications_log, NotificationsLogBody,
    notifications_email_draft, EmailDraftBody,
    notifications_sms_draft, SmsDraftBody,
    workflows_trigger, WorkflowTriggerBody,
)


class ExecutionAgent:
    def __init__(self, *args, **kwargs):
        self.logger = SessionLogger(session_id="init")
        self.base_url = "http://localhost:8000"

        # Dispatcher mapping endpoint paths directly to their Pydantic bodies and functions
        self.dispatcher = {
            "/api/logistics/pricing/update": (logistics_pricing_update, LogisticsPricingUpdateBody),
            "/logistics/pricing/update": (logistics_pricing_update, LogisticsPricingUpdateBody),
            
            "/api/logistics/routes/optimize": (logistics_routes_optimize, LogisticsRouteOptimizeBody),
            "/logistics/routes/optimize": (logistics_routes_optimize, LogisticsRouteOptimizeBody),
            
            "/api/notifications/bulk_send": (notifications_bulk_send, NotificationsBulkSendBody),
            "/notifications/bulk_send": (notifications_bulk_send, NotificationsBulkSendBody),
            
            "/api/procurement/hedge": (procurement_hedge, ProcurementHedgeBody),
            "/procurement/hedge": (procurement_hedge, ProcurementHedgeBody),
            
            "/api/warehouse/reallocation": (warehouse_reallocation, WarehouseReallocationBody),
            "/warehouse/reallocation": (warehouse_reallocation, WarehouseReallocationBody),
            
            "/api/crm/campaigns/create": (crm_campaigns_create, CrmCampaignCreateBody),
            "/crm/campaigns/create": (crm_campaigns_create, CrmCampaignCreateBody),
            
            "/api/catalog/pricing/update": (catalog_pricing_update, CatalogPricingUpdateBody),
            "/catalog/pricing/update": (catalog_pricing_update, CatalogPricingUpdateBody),
            
            "/api/crm/workflows/trigger": (crm_workflows_trigger, CrmWorkflowTriggerBody),
            "/crm/workflows/trigger": (crm_workflows_trigger, CrmWorkflowTriggerBody),
            
            "/api/crm/tasks/bulk_create": (crm_tasks_bulk_create, CrmTasksBulkCreateBody),
            "/crm/tasks/bulk_create": (crm_tasks_bulk_create, CrmTasksBulkCreateBody),
            
            "/api/reports/generate": (reports_generate, ReportGenerateBody),
            "/reports/generate": (reports_generate, ReportGenerateBody),
            
            "/api/finance/pricing/export_update": (finance_pricing_export_update, FinancePricingExportUpdateBody),
            "/finance/pricing/export_update": (finance_pricing_export_update, FinancePricingExportUpdateBody),
            
            "/api/finance/hedging/book": (finance_hedging_book, FinanceHedgingBookBody),
            "/finance/hedging/book": (finance_hedging_book, FinanceHedgingBookBody),
            
            "/api/portfolio/rebalance/flag": (portfolio_rebalance_flag, PortfolioRebalanceFlagBody),
            "/portfolio/rebalance/flag": (portfolio_rebalance_flag, PortfolioRebalanceFlagBody),
            
            "/api/finance/costing/recalculate": (finance_costing_recalculate, FinanceCostingRecalculateBody),
            "/finance/costing/recalculate": (finance_costing_recalculate, FinanceCostingRecalculateBody),
            
            "/api/compliance/tasks/generate": (compliance_tasks_generate, ComplianceTasksGenerateBody),
            "/compliance/tasks/generate": (compliance_tasks_generate, ComplianceTasksGenerateBody),
            
            "/api/pricing/policy_update": (pricing_policy_update, PricingPolicyUpdateBody),
            "/pricing/policy_update": (pricing_policy_update, PricingPolicyUpdateBody),
            
            "/api/communications/draft": (communications_draft, CommunicationsDraftBody),
            "/communications/draft": (communications_draft, CommunicationsDraftBody),
            
            "/api/tasks/create": (tasks_create, TaskCreateBody),
            "/tasks/create": (tasks_create, TaskCreateBody),
            
            "/api/contracts/flag_for_review": (contracts_flag_for_review, ContractFlagReviewBody),
            "/contracts/flag_for_review": (contracts_flag_for_review, ContractFlagReviewBody),
            
            "/api/procurement/emergency_order": (procurement_emergency_order, ProcurementEmergencyOrderBody),
            "/procurement/emergency_order": (procurement_emergency_order, ProcurementEmergencyOrderBody),
            
            "/api/clinical/protocols/activate": (clinical_protocols_activate, ClinicalProtocolsActivateBody),
            "/clinical/protocols/activate": (clinical_protocols_activate, ClinicalProtocolsActivateBody),
            
            "/api/notifications/clinical_alert": (notifications_clinical_alert, NotificationsClinicalAlertBody),
            "/notifications/clinical_alert": (notifications_clinical_alert, NotificationsClinicalAlertBody),
            
            "/api/clinical/formulary/update": (clinical_formulary_update, ClinicalFormularyUpdateBody),
            "/clinical/formulary/update": (clinical_formulary_update, ClinicalFormularyUpdateBody),
            
            "/api/operations/dispatch": (operations_dispatch, OperationsDispatchBody),
            "/operations/dispatch": (operations_dispatch, OperationsDispatchBody),
            
            "/api/infrastructure/contingency/activate": (infrastructure_contingency_activate, InfrastructureContingencyActivateBody),
            "/infrastructure/contingency/activate": (infrastructure_contingency_activate, InfrastructureContingencyActivateBody),
            
            "/api/communications/public_advisory": (communications_public_advisory, CommunicationsPublicAdvisoryBody),
            "/communications/public_advisory": (communications_public_advisory, CommunicationsPublicAdvisoryBody),
            
            "/api/traffic/reroute": (traffic_reroute, TrafficRerouteBody),
            "/traffic/reroute": (traffic_reroute, TrafficRerouteBody),
            
            "/api/notifications/log": (notifications_log, NotificationsLogBody),
            "/notifications/log": (notifications_log, NotificationsLogBody),
            
            "/api/notifications/email_draft": (notifications_email_draft, EmailDraftBody),
            "/notifications/email_draft": (notifications_email_draft, EmailDraftBody),
            
            "/api/notifications/sms_draft": (notifications_sms_draft, SmsDraftBody),
            "/notifications/sms_draft": (notifications_sms_draft, SmsDraftBody),
            
            "/api/workflows/trigger": (workflows_trigger, WorkflowTriggerBody),
            "/workflows/trigger": (workflows_trigger, WorkflowTriggerBody),
        }

    async def run(self, master_brief: dict, session_id: str = None, *args, **kwargs) -> dict:
        # Determine actual session_id, ensuring compatibility with test signatures
        actual_session_id = session_id
        if not actual_session_id or not isinstance(actual_session_id, str):
            actual_session_id = master_brief.get("session_id") or "session-default"

        self.logger.session_id = actual_session_id
        self.logger.log("execution", "start", {"session_id": actual_session_id})
        start_time = time.time()

        # Determine domain, falling back to third parameter if called with tests' legacy signature
        domain = master_brief.get("domain")
        if not domain and len(args) > 0 and isinstance(args[0], str):
            domain = args[0]
        if not domain:
            domain = "logistics"  # Fallback

        # STEP 1 — state before (directly import and query from local state store)
        state_before = await self._get_state(domain)
        self.logger.log("execution", "state_before_fetched", {"domain": domain})

        # STEP 2 — execute top action
        top_action = master_brief.get("top_action")
        if not top_action and "recommended_actions" in master_brief:
            top_action = master_brief["recommended_actions"][0]

        if not top_action:
            # Create a mock top action if none exists in brief to avoid crashing
            top_action = {
                "api_endpoint": "/api/logistics/pricing/update",
                "api_payload": {
                    "session_id": actual_session_id,
                    "route_id": "default",
                    "price_delta_pct": 0.0,
                    "effective_date": now_iso()
                },
                "action_type": "update_pricing"
            }
            
        action_type = top_action.get("action_type", "unknown")
        push_commentary(actual_session_id, "execution", f"Executing: {action_type}...", "start")

        raw_endpoint = top_action.get("api_endpoint", "/api/logistics/pricing/update")
        # Strip method prefix
        endpoint = raw_endpoint.strip()
        for prefix in ["POST ", "GET ", "PUT ", "DELETE "]:
            if endpoint.startswith(prefix):
                endpoint = endpoint[len(prefix):]
                break

        payload = dict(top_action.get("api_payload", {}))
        payload["session_id"] = actual_session_id
        
        # Directly invoke the dispatcher instead of loopback HTTP client
        api_result = await self._call_mock_api(endpoint, payload)
        self.logger.log(
            "execution",
            "action_executed",
            {"endpoint": endpoint, "status": api_result.get("status")},
        )

        # STEP 3 — state after
        state_after = await self._get_state(domain)
        self.logger.log("execution", "state_after_fetched", {"domain": domain})

        # STEP 4 — delta
        delta = compute_delta(state_before, state_after)
        self.logger.log("execution", "delta_computed", {"keys_changed": list(delta.keys())})
        
        changed_fields = len(delta.keys())
        push_commentary(actual_session_id, "execution", f"State updated — {changed_fields} fields changed", "progress")

        # STEP 5 — notifications
        notifications = []
        action_type = top_action.get("action_type", "")
        if "notify" in action_type or "campaign" in action_type or "alert" in action_type:
            notif_result = await self._send_notification_log(actual_session_id, top_action, domain)
            notifications = notif_result.get("notifications", [])
            self.logger.log("execution", "notifications_sent", {"count": len(notifications)})

        if master_brief.get("mock_mode_active"):
            notifications.insert(0, {
                "notification_id": generate_uuid(),
                "session_id": actual_session_id,
                "recipient": "System Admin",
                "recipient_role": "admin",
                "channel": "system",
                "message_preview": "⚠️ System switched to Mock Data Mode due to Gemini API failure. Check email.",
                "status": "delivered",
                "timestamp": now_iso(),
            })

        # STEP 6 — persist state log
        await save_state_log(
            session_id=actual_session_id,
            domain=domain,
            before=state_before,
            after=state_after,
            action=action_type,
            delta=delta,
        )

        # STEP 6.5 — Simulate Email Draft and Workflow Execution
        insight_str = master_brief.get("insight", "System automatically resolved alert.")
        if isinstance(insight_str, dict):
            insight_str = str(insight_str)
            
        # Build real recipients from master brief context
        domain = master_brief.get("domain", "business")
        affected = master_brief.get("impact_summary", {}).get("affected_parties", [])
        
        recipient_map = {
            "logistics": ["Al-Faisal Logistics", "Karachi Freight Co", "Punjab Carriers"],
            "business":  ["Lahore Regional Team", "Sales Manager", "Top 3 Accounts"],
            "finance":   ["CFO Office", "Treasury Team", "Risk Manager"],
            "policy":    ["Legal Team", "Compliance Officer", "Operations Head"],
            "healthcare":["Medical Director", "Pharmacy Head", "Clinical Staff"],
            "urban":     ["City Operations", "Zone Manager", "Public Affairs"],
        }
        recipients = affected if affected else recipient_map.get(domain, ["Operations Team"])
            
        email_result = await self._call_mock_api(
          "/api/notifications/email_draft",
          {
            "action_type": action_type,
            "domain": domain,
            "insight": insight_str,
            "recipients": recipients,
            "session_id": actual_session_id
          }
        )

        workflow_result = await self._call_mock_api(
          "/api/workflows/trigger",
          {
            "workflow_id": f"WF-{domain.upper()}-001",
            "trigger_reason": insight_str,
            "domain": domain,
            "session_id": actual_session_id
          }
        )

        # STEP 7 — build exec_log and persist artifact
        duration = time.time() - start_time
        execution_status = "success" if api_result.get("status") == "ok" else "failed"
        exec_log = {
            "agent": "execution",
            "session_id": actual_session_id,
            "domain": domain,
            "timestamp_start": start_time,
            "timestamp_end": now_iso(),
            "duration_seconds": round(duration, 3),
            "action_executed": {
                "rank": 1,
                "action_type": action_type,
                "api_endpoint": top_action.get("api_endpoint"),
                "payload_sent": payload,
                "http_status": api_result.get("status_code", 200),
                "response_received": api_result,
            },
            "state_before": state_before,
            "state_after": state_after,
            "delta": delta,
            "notifications_sent": notifications,
            "execution_status": execution_status,
            "projected_outcome": master_brief.get("projected_outcome", ""),
            "email_draft": email_result,
            "workflow_execution": workflow_result,
        }

        # Build rich notification entries — always populate this
        notifications_sent = list(notifications)
        
        domain = master_brief.get("domain", "business")
        insight = master_brief.get("insight", "Action required")
        if isinstance(insight, dict):
            insight = str(insight)
        action_type = top_action.get("action_type", "update")
        
        channels = ["email", "sms", "app"]
        
        for i, recipient in enumerate(recipients[:3]):
            channel = channels[i % len(channels)]
            
            if channel == "email":
                preview = (
                    f"Subject: [AI Ops] Action Taken — {action_type.replace('_',' ').title()}\n"
                    f"Dear {recipient},\n\n"
                    f"Our AI system detected: {insight[:100]}...\n"
                    f"Action executed: {action_type.replace('_',' ')}.\n"
                    f"Please review the dashboard for full details.\n\n"
                    f"Regards, Antigravity AI Ops"
                )
            elif channel == "sms":
                preview = (
                    f"[AI Ops Alert] {insight[:60]}... "
                    f"Action: {action_type.replace('_',' ')}. "
                    f"Check dashboard."
                )
            else:
                preview = (
                    f"AI Analysis complete. "
                    f"{insight[:80]}. "
                    f"Action taken: {action_type.replace('_',' ')}."
                )
            
            notifications_sent.append({
                "recipient":       recipient,
                "channel":         channel,
                "message_preview": preview,
                "status":          "delivered",
                "timestamp":       now_iso(),
            })
        
        exec_log["notifications_sent"] = notifications_sent


        self.logger.log(
            "execution",
            "complete",
            {"status": execution_status, "duration": duration},
        )
        
        exec_log["model_used"] = "python_executor"
        exec_log["agent_display_name"] = "Execution Agent"
        
        push_commentary(actual_session_id, "execution", f"Execution done — {len(notifications_sent)} notifications sent", "complete")
        close_stream(actual_session_id)
        
        return exec_log

    async def _get_state(self, domain: str) -> dict:
        try:
            # Query local state_store directly
            return get_state(domain)
        except Exception as e:
            self.logger.log("execution", "state_fetch_error", {"domain": domain, "error": str(e)})
            return {"domain": domain, "status": "error", "error": str(e)}

    async def _call_mock_api(self, endpoint: str, payload: dict) -> dict:
        try:
            # Standardize endpoint path
            ep = endpoint
            if not ep.startswith("/"):
                ep = "/" + ep

            if ep not in self.dispatcher:
                # Try with /api prefix stripped or added
                if ep.startswith("/api"):
                    ep_alt = ep[4:]
                else:
                    ep_alt = "/api" + ep
                    
                if ep_alt in self.dispatcher:
                    ep = ep_alt

            if ep not in self.dispatcher:
                raise ValueError(f"Unknown mock API endpoint: {endpoint}")

            func, body_class = self.dispatcher[ep]

            # Filter payload keys to match pydantic fields to avoid validation errors
            model_fields = body_class.model_fields
            filtered_payload = {k: v for k, v in payload.items() if k in model_fields}

            body = body_class(**filtered_payload)
            result = await func(body)

            if isinstance(result, dict):
                result["status_code"] = 200
                return result
            else:
                return {"status": "ok", "status_code": 200, "response": result}

        except Exception as e:
            self.logger.log("execution", "api_call_error", {"endpoint": endpoint, "error": str(e)})
            return {"status": "error", "status_code": 500, "error": str(e), "simulated_only": True}

    async def _send_notification_log(self, session_id: str, action: dict, domain: str) -> dict:
        notifications = [
            {
                "notification_id": generate_uuid(),
                "session_id": session_id,
                "recipient": f"{domain}_manager@newsops.local",
                "recipient_role": f"{domain}_manager",
                "channel": "email",
                "message_preview": (
                    f"[NewsOps Alert] Action executed: "
                    f"{action.get('action_type', 'unknown')} — domain: {domain}"
                ),
                "status": "delivered",
                "timestamp": now_iso(),
            },
            {
                "notification_id": generate_uuid(),
                "session_id": session_id,
                "recipient": "operations@newsops.local",
                "recipient_role": "operations_team",
                "channel": "slack",
                "message_preview": (
                    f"NewsOps pipeline complete for session {session_id[:8]}. "
                    f"Check dashboard."
                ),
                "status": "delivered",
                "timestamp": now_iso(),
            },
            {
                "notification_id": generate_uuid(),
                "session_id": session_id,
                "recipient": "+92300000000",
                "recipient_role": "duty_manager",
                "channel": "sms",
                "message_preview": (
                    f"NewsOps: Action {action.get('action_id', 'A1')} executed. "
                    f"Severity handled."
                ),
                "status": "delivered",
                "timestamp": now_iso(),
            },
        ]

        try:
            # Call notifications_log directly using its Pydantic body
            body = NotificationsLogBody(
                recipients=[n["recipient"] for n in notifications],
                message_template=notifications[0]["message_preview"] if notifications else "",
                simulated=True,
                session_id=session_id
            )
            await notifications_log(body)
        except Exception as e:
            self.logger.log(
                "execution",
                "notification_log_warning",
                {"error": str(e), "count": len(notifications)},
            )

        return {"notifications": notifications}

    async def close(self):
        # httpx client removed, close is now a safe no-op
        pass
