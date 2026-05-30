import copy

DEFAULT_STATE = {
    "logistics": {
        "delivery_price_per_kg": 45.0,
        "fuel_surcharge_pct": 12.0,
        "active_routes": 8,
        "delayed_shipments": 3,
        "on_time_rate_pct": 87.5,
    },
    "finance": {
        "pkr_usd_rate": 278.5,
        "kse100_index": 67840,
        "lending_rate_pct": 21.0,
        "inflation_rate_pct": 26.8,
        "fx_reserve_bn_usd": 8.2,
    },
    "business": {
        "active_campaigns": 3,
        "monthly_revenue_pkr": 4200000,
        "churn_rate_pct": 4.2,
        "new_customers_mtd": 127,
        "pipeline_value_pkr": 8900000,
    },
    "healthcare": {
        "critical_drug_shortage_count": 2,
        "avg_procurement_days": 14,
        "formulary_compliance_pct": 91.0,
        "pending_approvals": 7,
    },
    "policy": {
        "pending_regulations": 5,
        "compliance_deadline_days": 23,
        "active_notifications": 12,
        "last_gazette_date": "2026-05-15",
    },
    "urban": {
        "active_faults": 4,
        "avg_resolution_hours": 6.2,
        "water_supply_zones_affected": 2,
        "planned_maintenance_count": 8,
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
