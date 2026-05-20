import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON, select, update
from sqlalchemy.orm import relationship
from database.db import Base, get_db

# --- MODELS ---

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

    artifacts = relationship("AgentArtifact", back_populates="session", cascade="all, delete-orphan")
    state_logs = relationship("StateLog", back_populates="session", cascade="all, delete-orphan")


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
