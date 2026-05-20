import copy

DEFAULT_STATE = {
    "logistics": {
        "delivery_price_per_kg": 2.40,
        "fuel_cost_ratio_pct": 35.0,
        "monthly_shipments": 4200,
        "active_routes": 12,
        "buyers_notified": 0,
        "last_pricing_update": None,
        "avg_delivery_distance_km": 45.0,
        "on_time_delivery_pct": 87.5,
        "warehouse_utilization_pct": 72.0,
    },
    "business": {
        "regional_revenue_pkr": 8500000,
        "order_volume_monthly": 1240,
        "avg_order_value_pkr": 6850,
        "active_campaigns": 0,
        "churn_risk_customers": 47,
        "campaign_reach": 0,
        "sales_conversion_pct": 3.2,
        "buyers_notified": 0,
        "last_campaign_id": None,
        "crm_tasks_open": 0,
        "workflow_status": "idle",
    },
    "finance": {
        "usd_pkr_rate": 278.50,
        "open_contracts": 8,
        "hedged_amount_usd": 0,
        "export_revenue_at_risk_pkr": 12000000,
        "contracts_repriced": 0,
        "portfolio_flags": 0,
    },
    "policy": {
        "compliance_tasks_open": 0,
        "affected_categories": 0,
        "notices_drafted": 0,
        "contracts_flagged": 0,
        "departments_notified": 0,
    },
    "healthcare": {
        "drug_availability_pct": 94.0,
        "emergency_pos_open": 0,
        "staff_alerts_sent": 0,
        "formulary_updates": 0,
        "patients_at_risk": 0,
    },
    "urban": {
        "active_faults": 0,
        "crews_dispatched": 0,
        "population_affected": 0,
        "advisories_published": 0,
        "traffic_reroutes_active": 0,
        "contingency_zones_active": 0,
    },
}

_state = copy.deepcopy(DEFAULT_STATE)


def get_state(domain: str) -> dict:
    return copy.deepcopy(_state.get(domain, {}))


def update_state(domain: str, updates: dict) -> dict:
    if domain in _state:
        _state[domain].update(updates)
    return get_state(domain)


def reset_state():
    global _state
    _state = copy.deepcopy(DEFAULT_STATE)
