import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON, select, update, Boolean, Integer
from sqlalchemy.orm import relationship
from database.db import Base, get_db

# --- MODELS ---

class Config(Base):
    __tablename__ = "configs"
    key = Column(String(50), primary_key=True)
    value = Column(String(200))

class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    api_key = Column(String(64), unique=True, nullable=False)
    plan = Column(String(20), default="free")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    monthly_analysis_count = Column(Integer, default=0)
    monthly_limit = Column(Integer, default=50)

    sessions = relationship("AnalysisSession", back_populates="organisation")


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    domain = Column(String(50))
    input_type = Column(String(20))
    input_preview = Column(Text)  # first 300 chars
    status = Column(String(20), default="pending")
    error_detail = Column(Text, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    task_id = Column(String(50), nullable=True)  # Celery task ID
    org_id = Column(String(36), ForeignKey("organisations.id"), nullable=True)

    organisation = relationship("Organisation", back_populates="sessions")
    artifacts = relationship("AgentArtifact", back_populates="session", cascade="all, delete-orphan")
    state_logs = relationship("StateLog", back_populates="session", cascade="all, delete-orphan")
    action_outcomes = relationship("ActionOutcome", back_populates="session", cascade="all, delete-orphan")


class AgentArtifact(Base):
    __tablename__ = "agent_artifacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("analysis_sessions.id"))
    agent_name = Column(String(50))
    artifact_type = Column(String(50))
    content = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    duration_seconds = Column(Float, nullable=True)

    session = relationship("AnalysisSession", back_populates="artifacts")


class StateLog(Base):
    __tablename__ = "state_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("analysis_sessions.id"))
    domain = Column(String(50))
    state_before = Column(JSON)
    state_after = Column(JSON)
    action_taken = Column(String(100))
    delta = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("AnalysisSession", back_populates="state_logs")


class WatchlistAlert(Base):
    __tablename__ = "watchlist_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organisations.id"), nullable=True)
    user_id = Column(String(100), nullable=False)
    domain = Column(String(50), nullable=False)
    condition_type = Column(String(50), nullable=False)
    condition_value = Column(String(200), nullable=False)
    keyword = Column(String(200), nullable=True)
    label = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_triggered_at = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String(36), ForeignKey("watchlist_alerts.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(36), ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False)
    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    trigger_reason = Column(Text, nullable=False)


class ActionOutcome(Base):
    __tablename__ = "action_outcomes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=True)
    session_id = Column(String(36), ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100), nullable=False, default="")
    action_description = Column(Text, nullable=False, default="")
    recommended_delta = Column(String(200), nullable=False, default="")
    user_confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, nullable=True)
    actual_outcome_note = Column(Text, nullable=True)
    outcome_recorded_at = Column(DateTime, nullable=True)
    domain = Column(String(50), nullable=False, default="general")
    kpi_name = Column(String(100), nullable=True)
    projected_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("AnalysisSession", back_populates="action_outcomes")


# --- ASYNC HELPER FUNCTIONS ---

async def save_session(session_dict: dict):
    """Insert a new AnalysisSession row."""
    async with get_db() as db:
        new_session = AnalysisSession(**session_dict)
        db.add(new_session)

async def update_session_status(session_id: str, status: str, error: str = None, duration: float = None):
    """Update status, error_detail, duration_seconds by session_id."""
    async with get_db() as db:
        stmt = (
            update(AnalysisSession)
            .where(AnalysisSession.id == session_id)
            .values(status=status, error_detail=error, duration_seconds=duration)
        )
        await db.execute(stmt)


async def update_session_task_id(session_id: str, task_id: str):
    """Store the Celery task ID on the session row after enqueueing."""
    async with get_db() as db:
        stmt = (
            update(AnalysisSession)
            .where(AnalysisSession.id == session_id)
            .values(task_id=task_id)
        )
        await db.execute(stmt)

async def increment_org_usage(org_id: str):
    """Increment the monthly analysis count for an organisation."""
    async with get_db() as db:
        stmt = (
            update(Organisation)
            .where(Organisation.id == org_id)
            .values(monthly_analysis_count=Organisation.monthly_analysis_count + 1)
        )
        await db.execute(stmt)

async def save_artifact(session_id: str, agent_name: str, artifact_type: str, content: dict, duration: float = None):
    """Insert a new AgentArtifact row."""
    async with get_db() as db:
        artifact = AgentArtifact(
            session_id=session_id,
            agent_name=agent_name,
            artifact_type=artifact_type,
            content=content,
            duration_seconds=duration
        )
        db.add(artifact)

async def save_state_log(session_id: str, domain: str, before: dict, after: dict, action: str, delta: dict):
    """Insert a new StateLog row."""
    async with get_db() as db:
        log = StateLog(
            session_id=session_id,
            domain=domain,
            state_before=before,
            state_after=after,
            action_taken=action,
            delta=delta
        )
        db.add(log)

async def get_session_artifacts(session_id: str) -> list:
    """Return all AgentArtifact rows for that session ordered by created_at ascending."""
    async with get_db() as db:
        stmt = (
            select(AgentArtifact)
            .where(AgentArtifact.session_id == session_id)
            .order_by(AgentArtifact.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


async def get_session(session_id: str) -> dict | None:
    """Return a single AnalysisSession as a dict, or None if not found."""
    async with get_db() as db:
        result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return {
            "id": row.id,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "domain": row.domain,
            "input_type": row.input_type,
            "input_preview": row.input_preview,
            "status": row.status,
            "error_detail": row.error_detail,
            "duration_seconds": row.duration_seconds,
            "task_id": row.task_id,
        }


async def create_action_outcome(
    session_id: str,
    domain: str,
    action_type: str,
    action_description: str,
    recommended_delta: str,
    org_id: str | None = None,
    kpi_name: str | None = None,
    projected_value: float | None = None,
) -> str:
    """Insert a new ActionOutcome row (user_confirmed=False by default).
    Returns the new outcome id."""
    async with get_db() as db:
        outcome = ActionOutcome(
            id=str(uuid.uuid4()),
            org_id=org_id,
            session_id=session_id,
            domain=domain,
            action_type=action_type,
            action_description=action_description,
            recommended_delta=recommended_delta,
            user_confirmed=False,
            kpi_name=kpi_name,
            projected_value=projected_value,
        )
        db.add(outcome)
        return outcome.id
