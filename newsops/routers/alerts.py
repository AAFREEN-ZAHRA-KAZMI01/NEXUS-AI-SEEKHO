from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, desc, update, delete

from database.db import get_db
from database.models import WatchlistAlert, AlertHistory

router = APIRouter(prefix="/api", tags=["Alerts"])


class AlertCreate(BaseModel):
    domain: str
    condition_type: str
    condition_value: str
    keyword: Optional[str] = None
    label: str
    user_id: str


@router.post("/alerts")
async def create_alert(payload: AlertCreate):
    async with get_db() as db:
        new_alert = WatchlistAlert(
            id=str(uuid.uuid4()),
            user_id=payload.user_id,
            domain=payload.domain,
            condition_type=payload.condition_type,
            condition_value=payload.condition_value,
            keyword=payload.keyword,
            label=payload.label,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            trigger_count=0
        )
        db.add(new_alert)
        await db.flush()
        # Fetch it or return it directly
        alert_dict = {
            "id": new_alert.id,
            "user_id": new_alert.user_id,
            "domain": new_alert.domain,
            "condition_type": new_alert.condition_type,
            "condition_value": new_alert.condition_value,
            "keyword": new_alert.keyword,
            "label": new_alert.label,
            "is_active": new_alert.is_active,
            "created_at": new_alert.created_at.isoformat() if new_alert.created_at else None,
            "last_triggered_at": None,
            "trigger_count": 0
        }
        return alert_dict


@router.get("/alerts")
async def get_alerts(user_id: str):
    async with get_db() as db:
        result = await db.execute(
            select(WatchlistAlert)
            .where(WatchlistAlert.user_id == user_id)
            .order_by(desc(WatchlistAlert.created_at))
        )
        alerts = result.scalars().all()
        
    return [
        {
            "id": a.id,
            "user_id": a.user_id,
            "domain": a.domain,
            "condition_type": a.condition_type,
            "condition_value": a.condition_value,
            "keyword": a.keyword,
            "label": a.label,
            "is_active": a.is_active,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "last_triggered_at": a.last_triggered_at.isoformat() if a.last_triggered_at else None,
            "trigger_count": a.trigger_count
        }
        for a in alerts
    ]


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    async with get_db() as db:
        result = await db.execute(
            select(WatchlistAlert).where(WatchlistAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        await db.delete(alert)
    return {"status": "success", "message": "Alert deleted successfully"}


@router.patch("/alerts/{alert_id}/toggle")
async def toggle_alert(alert_id: str):
    async with get_db() as db:
        result = await db.execute(
            select(WatchlistAlert).where(WatchlistAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        alert.is_active = not alert.is_active
        alert_dict = {
            "id": alert.id,
            "user_id": alert.user_id,
            "domain": alert.domain,
            "condition_type": alert.condition_type,
            "condition_value": alert.condition_value,
            "keyword": alert.keyword,
            "label": alert.label,
            "is_active": alert.is_active,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "last_triggered_at": alert.last_triggered_at.isoformat() if alert.last_triggered_at else None,
            "trigger_count": alert.trigger_count
        }
        return alert_dict


@router.get("/alerts/history")
async def get_alert_history(user_id: str):
    async with get_db() as db:
        result = await db.execute(
            select(AlertHistory, WatchlistAlert)
            .join(WatchlistAlert, AlertHistory.alert_id == WatchlistAlert.id)
            .where(WatchlistAlert.user_id == user_id)
            .order_by(desc(AlertHistory.triggered_at))
            .limit(50)
        )
        history_rows = result.all()
        
    return [
        {
            "id": hist.id,
            "alert_id": hist.alert_id,
            "session_id": hist.session_id,
            "triggered_at": hist.triggered_at.isoformat() if hist.triggered_at else None,
            "trigger_reason": hist.trigger_reason,
            "alert_label": alert.label,
            "domain": alert.domain,
            "condition_type": alert.condition_type,
            "condition_value": alert.condition_value,
        }
        for hist, alert in history_rows
    ]
