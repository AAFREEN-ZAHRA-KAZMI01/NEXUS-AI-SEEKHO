import pytest
from database.db import get_db
from database.models import WatchlistAlert, AlertHistory

@pytest.mark.asyncio
class TestAlertsRouter:
    async def test_create_and_get_alerts(self, client):
        user_id = "test-user-alerts-999"
        
        # 1. Create alert
        create_payload = {
            "domain": "finance",
            "condition_type": "severity_above",
            "condition_value": "7",
            "keyword": None,
            "label": "Test Finance Alert",
            "user_id": user_id
        }
        
        r = await client.post("/api/alerts", json=create_payload)
        assert r.status_code == 200
        alert_data = r.json()
        assert alert_data["label"] == "Test Finance Alert"
        assert alert_data["domain"] == "finance"
        alert_id = alert_data["id"]
        
        # 2. Get alerts
        r = await client.get(f"/api/alerts?user_id={user_id}")
        assert r.status_code == 200
        alerts = r.json()
        assert len(alerts) >= 1
        assert any(a["id"] == alert_id for a in alerts)
        
        # 3. Toggle alert
        r = await client.patch(f"/api/alerts/{alert_id}/toggle")
        assert r.status_code == 200
        assert r.json()["is_active"] is False
        
        # 4. Delete alert
        r = await client.delete(f"/api/alerts/{alert_id}")
        assert r.status_code == 200
        
        # Verify deletion
        r = await client.get(f"/api/alerts?user_id={user_id}")
        assert r.status_code == 200
        alerts = r.json()
        assert not any(a["id"] == alert_id for a in alerts)
