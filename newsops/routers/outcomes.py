from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, desc, func

from database.db import get_db
from database.models import ActionOutcome, AnalysisSession

router = APIRouter(prefix="/api", tags=["Outcomes"])


# ── Schemas ─────────────────────────────────────────────────────────────────────

class ConfirmActionPayload(BaseModel):
    confirmed: bool
    note: Optional[str] = None


class RecordResultPayload(BaseModel):
    actual_outcome_note: str
    actual_value: Optional[float] = None


# ── Endpoints ────────────────────────────────────────────────────────────────────

@router.post("/session/{session_id}/confirm-action")
async def confirm_action(session_id: str, payload: ConfirmActionPayload):
    """Create or update ActionOutcome for this session with user's confirmed status."""
    async with get_db() as db:
        # Check if an outcome already exists for this session
        result = await db.execute(
            select(ActionOutcome).where(ActionOutcome.session_id == session_id)
        )
        outcome = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if outcome is None:
            # Try to fetch session domain info
            sess_result = await db.execute(
                select(AnalysisSession).where(AnalysisSession.id == session_id)
            )
            session = sess_result.scalar_one_or_none()
            domain = session.domain if session else "general"

            outcome = ActionOutcome(
                id=str(uuid.uuid4()),
                session_id=session_id,
                domain=domain,
                action_type="",
                action_description="",
                recommended_delta="",
                user_confirmed=payload.confirmed,
                confirmed_at=now if payload.confirmed else None,
                actual_outcome_note=payload.note,
            )
            db.add(outcome)
        else:
            outcome.user_confirmed = payload.confirmed
            outcome.confirmed_at = now if payload.confirmed else None
            if payload.note:
                outcome.actual_outcome_note = payload.note

        await db.flush()

        return {
            "id": outcome.id,
            "session_id": outcome.session_id,
            "user_confirmed": outcome.user_confirmed,
            "confirmed_at": outcome.confirmed_at.isoformat() if outcome.confirmed_at else None,
            "domain": outcome.domain,
            "actual_outcome_note": outcome.actual_outcome_note,
        }


@router.post("/outcomes/{outcome_id}/record-result")
async def record_result(outcome_id: str, payload: RecordResultPayload):
    """Update an existing ActionOutcome with the actual result."""
    async with get_db() as db:
        result = await db.execute(
            select(ActionOutcome).where(ActionOutcome.id == outcome_id)
        )
        outcome = result.scalar_one_or_none()
        if not outcome:
            raise HTTPException(status_code=404, detail="Outcome not found")

        outcome.actual_outcome_note = payload.actual_outcome_note
        outcome.actual_value = payload.actual_value
        outcome.outcome_recorded_at = datetime.now(timezone.utc)

        return {
            "id": outcome.id,
            "session_id": outcome.session_id,
            "action_type": outcome.action_type,
            "recommended_delta": outcome.recommended_delta,
            "user_confirmed": outcome.user_confirmed,
            "actual_outcome_note": outcome.actual_outcome_note,
            "actual_value": outcome.actual_value,
            "outcome_recorded_at": outcome.outcome_recorded_at.isoformat() if outcome.outcome_recorded_at else None,
            "domain": outcome.domain,
        }


@router.get("/outcomes")
async def get_outcomes(domain: Optional[str] = None, limit: int = 20):
    """Return recent ActionOutcome rows, optionally filtered by domain."""
    async with get_db() as db:
        stmt = select(ActionOutcome).order_by(desc(ActionOutcome.created_at)).limit(limit)
        if domain:
            stmt = stmt.where(ActionOutcome.domain == domain)
        result = await db.execute(stmt)
        outcomes = result.scalars().all()

    return [
        {
            "id": o.id,
            "session_id": o.session_id,
            "action_type": o.action_type,
            "action_description": o.action_description,
            "recommended_delta": o.recommended_delta,
            "user_confirmed": o.user_confirmed,
            "confirmed_at": o.confirmed_at.isoformat() if o.confirmed_at else None,
            "actual_outcome_note": o.actual_outcome_note,
            "outcome_recorded_at": o.outcome_recorded_at.isoformat() if o.outcome_recorded_at else None,
            "domain": o.domain,
            "kpi_name": o.kpi_name,
            "projected_value": o.projected_value,
            "actual_value": o.actual_value,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in outcomes
    ]


@router.get("/outcomes/summary")
async def get_outcomes_summary():
    """Return aggregated stats across all ActionOutcome rows."""
    async with get_db() as db:
        # Total actions recommended
        total_result = await db.execute(select(func.count(ActionOutcome.id)))
        total_actions = total_result.scalar() or 0

        # Total confirmed
        confirmed_result = await db.execute(
            select(func.count(ActionOutcome.id)).where(ActionOutcome.user_confirmed == True)
        )
        total_confirmed = confirmed_result.scalar() or 0

        # Outcomes recorded
        recorded_result = await db.execute(
            select(func.count(ActionOutcome.id)).where(ActionOutcome.outcome_recorded_at != None)
        )
        outcomes_recorded = recorded_result.scalar() or 0

        # By domain breakdown
        domain_rows = await db.execute(select(ActionOutcome))
        all_outcomes = domain_rows.scalars().all()

    # Build by_domain dict in Python for flexibility
    by_domain: dict = {}
    for o in all_outcomes:
        d = o.domain or "general"
        if d not in by_domain:
            by_domain[d] = {"confirmed": 0, "recorded": 0}
        if o.user_confirmed:
            by_domain[d]["confirmed"] += 1
        if o.outcome_recorded_at is not None:
            by_domain[d]["recorded"] += 1

    confirmation_rate = round((total_confirmed / total_actions * 100), 1) if total_actions > 0 else 0.0

    return {
        "total_actions_recommended": total_actions,
        "total_confirmed": total_confirmed,
        "confirmation_rate_pct": confirmation_rate,
        "outcomes_recorded": outcomes_recorded,
        "by_domain": by_domain,
    }
