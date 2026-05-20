"""Tests for all mock API endpoints."""
import pytest
from utils.helpers import generate_uuid


# ── State endpoints ────────────────────────────────────────────────────────────

class TestStateEndpoints:
    async def test_get_logistics_state(self, client):
        r = await client.get("/api/state/logistics")
        assert r.status_code == 200
        data = r.json()
        assert "delivery_price_per_kg" in data
        assert "monthly_shipments" in data

    async def test_get_business_state(self, client):
        r = await client.get("/api/state/business")
        assert r.status_code == 200
        data = r.json()
        assert "regional_revenue_pkr" in data
        assert "order_volume_monthly" in data

    async def test_get_finance_state(self, client):
        r = await client.get("/api/state/finance")
        assert r.status_code == 200
        data = r.json()
        assert "usd_pkr_rate" in data

    async def test_get_policy_state(self, client):
        r = await client.get("/api/state/policy")
        assert r.status_code == 200
        data = r.json()
        assert "compliance_tasks_open" in data

    async def test_get_healthcare_state(self, client):
        r = await client.get("/api/state/healthcare")
        assert r.status_code == 200
        data = r.json()
        assert "drug_availability_pct" in data

    async def test_get_urban_state(self, client):
        r = await client.get("/api/state/urban")
        assert r.status_code == 200
        data = r.json()
        assert "active_faults" in data

    async def test_unknown_domain_returns_empty(self, client):
        r = await client.get("/api/state/nonexistent")
        assert r.status_code == 200
        assert r.json() == {}


# ── Logistics endpoints ────────────────────────────────────────────────────────

class TestLogisticsEndpoints:
    async def test_pricing_update(self, client):
        sid = generate_uuid()
        r = await client.post("/api/logistics/pricing/update", json={
            "route_id": "LHR-ISB-01",
            "price_delta_pct": 8.5,
            "effective_date": "2024-12-01",
            "session_id": sid,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["new_price"] > data["old_price"]
        assert data["price_delta_pct"] == 8.5

    async def test_pricing_update_mutates_state(self, client):
        original = (await client.get("/api/state/logistics")).json()["delivery_price_per_kg"]
        await client.post("/api/logistics/pricing/update", json={
            "route_id": "x",
            "price_delta_pct": 10.0,
            "effective_date": "2024-12-01",
            "session_id": generate_uuid(),
        })
        updated = (await client.get("/api/state/logistics")).json()["delivery_price_per_kg"]
        assert updated > original

    async def test_routes_optimize(self, client):
        r = await client.post("/api/logistics/routes/optimize", json={
            "current_route_id": "LHR-KHI-02",
            "optimization_target": "fuel",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["savings_pct"] > 0
        assert data["new_fuel_ratio"] < data["old_fuel_ratio"]

    async def test_notifications_bulk_send(self, client):
        recipients = ["buyer_001", "buyer_002", "buyer_003"]
        r = await client.post("/api/notifications/bulk_send", json={
            "template": "Price update notice",
            "recipient_list": recipients,
            "effective_date": "2024-12-01",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["sent_count"] == 3
        assert data["failed_count"] == 0

    async def test_procurement_hedge(self, client):
        r = await client.post("/api/procurement/hedge", json={
            "commodity": "HSD",
            "volume_litres": 50000.0,
            "duration_days": 30,
            "current_rate": 95.99,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["locked_rate"] == 95.99
        assert "expiry_date" in data

    async def test_warehouse_reallocation(self, client):
        r = await client.post("/api/warehouse/reallocation", json={
            "source_warehouse_id": "WH-LHR-01",
            "target_warehouse_id": "WH-KHI-01",
            "sku_list": ["SKU-001", "SKU-002"],
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["skus_moved"] == 2
        assert data["new_avg_distance_km"] < data["old_avg_distance_km"]


# ── Business endpoints ─────────────────────────────────────────────────────────

class TestBusinessEndpoints:
    async def test_crm_campaign_create(self, client):
        r = await client.post("/api/crm/campaigns/create", json={
            "region": "Lahore",
            "discount_pct": 10.0,
            "target_segment": "high_value",
            "duration_days": 14,
            "budget_pkr": 500000.0,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "campaign_id" in data
        assert data["reach_estimate"] > 0

    async def test_catalog_pricing_update(self, client):
        r = await client.post("/api/catalog/pricing/update", json={
            "region": "Lahore",
            "category": "electronics",
            "price_delta_pct": 5.0,
            "effective_date": "2024-12-01",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["skus_updated"] > 0

    async def test_crm_workflow_trigger(self, client):
        r = await client.post("/api/crm/workflows/trigger", json={
            "workflow_id": "WF-RETENTION-001",
            "segment": "at_risk",
            "message_template": "We miss you!",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["customers_targeted"] > 0

    async def test_crm_tasks_bulk_create(self, client):
        r = await client.post("/api/crm/tasks/bulk_create", json={
            "account_list": ["ACC-001", "ACC-002", "ACC-003"],
            "task_type": "follow_up",
            "due_date": "2024-12-15",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["tasks_created"] == 3

    async def test_reports_generate(self, client):
        r = await client.post("/api/reports/generate", json={
            "report_type": "sales_summary",
            "data_source": "crm",
            "recipients": ["manager@company.com"],
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "report_id" in data


# ── Finance endpoints ──────────────────────────────────────────────────────────

class TestFinanceEndpoints:
    async def test_pricing_export_update(self, client):
        r = await client.post("/api/finance/pricing/export_update", json={
            "currency_pair": "USD/PKR",
            "rate_delta_pct": 2.0,
            "affected_contracts": ["C-001", "C-002"],
            "effective_date": "2024-12-01",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["contracts_repriced"] == 2
        assert data["new_rate"] > data["old_rate"]

    async def test_hedging_book(self, client):
        r = await client.post("/api/finance/hedging/book", json={
            "currency_pair": "USD/PKR",
            "amount_usd": 100000.0,
            "duration_days": 90,
            "rate": 280.0,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["amount_usd"] == 100000.0
        assert "contract_id" in data

    async def test_portfolio_rebalance_flag(self, client):
        r = await client.post("/api/portfolio/rebalance/flag", json={
            "affected_instruments": ["ENGRO", "LUCK", "PSO"],
            "reason": "FX exposure",
            "urgency": "high",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["instruments_flagged"] == 3

    async def test_costing_recalculate(self, client):
        r = await client.post("/api/finance/costing/recalculate", json={
            "fx_rate": 285.50,
            "affected_po_list": ["PO-001", "PO-002"],
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["pos_updated"] == 2


# ── Policy endpoints ───────────────────────────────────────────────────────────

class TestPolicyEndpoints:
    async def test_compliance_tasks_generate(self, client):
        r = await client.post("/api/compliance/tasks/generate", json={
            "regulation_id": "OGRA-2024-1101",
            "affected_departments": ["procurement", "finance", "logistics"],
            "deadline": "2024-12-31",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["departments_notified"] == 3
        assert data["tasks_created"] == 9

    async def test_pricing_policy_update(self, client):
        r = await client.post("/api/pricing/policy_update", json={
            "policy_ref": "OGRA-2024-1101",
            "affected_categories": ["fuel", "logistics"],
            "cost_delta_pct": 18.5,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["categories_updated"] == 2

    async def test_communications_draft(self, client):
        r = await client.post("/api/communications/draft", json={
            "template": "regulatory_notice",
            "audience": "all_staff",
            "key_changes": ["Fuel price increase 18.5%", "Delivery cost adjusted"],
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "draft_id" in data

    async def test_tasks_create(self, client):
        r = await client.post("/api/tasks/create", json={
            "task_type": "legal_review",
            "priority": "high",
            "summary": "Review OGRA notification impact",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "task_id" in data

    async def test_contracts_flag_for_review(self, client):
        r = await client.post("/api/contracts/flag_for_review", json={
            "policy_ref": "OGRA-2024-1101",
            "affected_contract_ids": ["CTR-001", "CTR-002", "CTR-003"],
            "reason": "Fuel price clause renegotiation required",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["contracts_flagged"] == 3


# ── Healthcare endpoints ───────────────────────────────────────────────────────

class TestHealthcareEndpoints:
    async def test_emergency_order(self, client):
        r = await client.post("/api/procurement/emergency_order", json={
            "item_id": "DRUG-INS-001",
            "quantity": 500,
            "urgency": "critical",
            "supplier_shortlist": ["MedCo", "PharmaDist"],
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["quantity"] == 500
        assert data["supplier_confirmed"] == "MedCo"

    async def test_clinical_protocols_activate(self, client):
        r = await client.post("/api/clinical/protocols/activate", json={
            "protocol_id": "PROT-SHORTAGE-001",
            "drug_id": "DRUG-INS-001",
            "affected_facilities": ["CMH", "PIMS", "Jinnah"],
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["facilities_count"] == 3
        assert data["staff_notified"] > 0

    async def test_clinical_alert(self, client):
        r = await client.post("/api/notifications/clinical_alert", json={
            "alert_type": "shortage",
            "affected_drug_or_procedure": "Insulin",
            "guidance": "Switch to alternative formulary",
            "recipients": ["dr1", "dr2"],
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["sent_to"] == 2

    async def test_formulary_update(self, client):
        r = await client.post("/api/clinical/formulary/update", json={
            "drug_id": "DRUG-INS-001",
            "change_type": "substitute",
            "alternative_drug_id": "DRUG-INS-002",
            "effective_date": "2024-12-01",
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["pharmacists_notified"] > 0


# ── Urban endpoints ────────────────────────────────────────────────────────────

class TestUrbanEndpoints:
    async def test_operations_dispatch(self, client):
        r = await client.post("/api/operations/dispatch", json={
            "fault_location": "Gulberg Zone 3",
            "crew_type": "electrical",
            "priority": "high",
            "eta_minutes": 25,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "crew_id" in data
        assert data["eta_minutes"] == 25

    async def test_contingency_activate(self, client):
        r = await client.post("/api/infrastructure/contingency/activate", json={
            "zone_id": "ZONE-LHR-07",
            "utility_type": "electricity",
            "contingency_source": "generator",
            "duration_hours": 6,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["population_served"] > 0

    async def test_public_advisory(self, client):
        r = await client.post("/api/communications/public_advisory", json={
            "zone_id": "ZONE-LHR-07",
            "issue_type": "power_outage",
            "severity": "moderate",
            "guidance_text": "Conserve power. Crews dispatched.",
            "channels": ["sms", "app", "twitter"],
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["channels_reached"] == 3

    async def test_traffic_reroute(self, client):
        r = await client.post("/api/traffic/reroute", json={
            "affected_segment_id": "SEG-MM-ALAM-01",
            "alternate_route_id": "SEG-CANAL-02",
            "duration_hours": 4,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["vehicles_affected"] > 0


# ── Notification log ───────────────────────────────────────────────────────────

class TestNotificationLog:
    async def test_log_returns_correct_count(self, client):
        recipients = ["user_a", "user_b", "user_c"]
        r = await client.post("/api/notifications/log", json={
            "recipients": recipients,
            "message_template": "Your order price has changed.",
            "simulated": True,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert len(data["notifications"]) == 3

    async def test_log_notification_fields(self, client):
        r = await client.post("/api/notifications/log", json={
            "recipients": ["user_x"],
            "message_template": "Test message for notification",
            "simulated": True,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        note = r.json()["notifications"][0]
        assert note["recipient"] == "user_x"
        assert note["status"] == "delivered"
        assert "timestamp" in note

    async def test_log_message_preview_truncated(self, client):
        long_template = "A" * 200
        r = await client.post("/api/notifications/log", json={
            "recipients": ["u"],
            "message_template": long_template,
            "simulated": True,
            "session_id": generate_uuid(),
        })
        assert r.status_code == 200
        preview = r.json()["notifications"][0]["message_preview"]
        assert len(preview) <= 100
