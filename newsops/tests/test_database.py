"""Tests for database models and async helper functions."""
import pytest
from utils.helpers import generate_uuid


class TestSaveSession:
    async def test_save_session_creates_record(self):
        from database.models import save_session, AnalysisSession
        from database.db import get_db
        from sqlalchemy import select

        sid = generate_uuid()
        await save_session({
            "id": sid,
            "domain": "logistics",
            "input_type": "text",
            "input_preview": "OGRA fuel price increase",
            "status": "pending",
        })

        async with get_db() as db:
            result = await db.execute(
                select(AnalysisSession).where(AnalysisSession.id == sid)
            )
            session = result.scalar_one_or_none()

        assert session is not None
        assert session.domain == "logistics"
        assert session.input_type == "text"
        assert session.status == "pending"

    async def test_save_session_preview_stored(self):
        from database.models import save_session, AnalysisSession
        from database.db import get_db
        from sqlalchemy import select

        sid = generate_uuid()
        preview = "Fuel notification from OGRA"
        await save_session({
            "id": sid,
            "domain": "policy",
            "input_type": "text",
            "input_preview": preview,
            "status": "pending",
        })

        async with get_db() as db:
            result = await db.execute(
                select(AnalysisSession).where(AnalysisSession.id == sid)
            )
            session = result.scalar_one_or_none()

        assert session.input_preview == preview


class TestUpdateSessionStatus:
    async def test_update_to_completed(self):
        from database.models import save_session, update_session_status, AnalysisSession
        from database.db import get_db
        from sqlalchemy import select

        sid = generate_uuid()
        await save_session({
            "id": sid,
            "domain": "business",
            "input_type": "csv",
            "input_preview": "sales data",
            "status": "pending",
        })

        await update_session_status(sid, "completed", duration=1.23)

        async with get_db() as db:
            result = await db.execute(
                select(AnalysisSession).where(AnalysisSession.id == sid)
            )
            session = result.scalar_one_or_none()

        assert session.status == "completed"
        assert session.duration_seconds == pytest.approx(1.23)

    async def test_update_to_failed_with_error(self):
        from database.models import save_session, update_session_status, AnalysisSession
        from database.db import get_db
        from sqlalchemy import select

        sid = generate_uuid()
        await save_session({
            "id": sid,
            "domain": "finance",
            "input_type": "text",
            "input_preview": "rate analysis",
            "status": "pending",
        })

        await update_session_status(sid, "failed", error="LLM timeout", duration=5.0)

        async with get_db() as db:
            result = await db.execute(
                select(AnalysisSession).where(AnalysisSession.id == sid)
            )
            session = result.scalar_one_or_none()

        assert session.status == "failed"
        assert session.error_detail == "LLM timeout"


class TestSaveArtifact:
    async def test_save_artifact_creates_record(self):
        from database.models import save_session, save_artifact, AgentArtifact
        from database.db import get_db
        from sqlalchemy import select

        sid = generate_uuid()
        await save_session({
            "id": sid,
            "domain": "logistics",
            "input_type": "text",
            "input_preview": "fuel report",
            "status": "pending",
        })

        content = {"agent": "ingestion", "facts": [{"text": "fuel up 18%"}]}
        await save_artifact(sid, "ingestion", "signals", content, duration=0.5)

        async with get_db() as db:
            result = await db.execute(
                select(AgentArtifact).where(AgentArtifact.session_id == sid)
            )
            artifacts = list(result.scalars().all())

        assert len(artifacts) == 1
        assert artifacts[0].agent_name == "ingestion"
        assert artifacts[0].artifact_type == "signals"
        assert artifacts[0].content["agent"] == "ingestion"

    async def test_multiple_artifacts_per_session(self):
        from database.models import save_session, save_artifact, AgentArtifact
        from database.db import get_db
        from sqlalchemy import select

        sid = generate_uuid()
        await save_session({
            "id": sid,
            "domain": "policy",
            "input_type": "text",
            "input_preview": "policy analysis",
            "status": "pending",
        })

        for agent_name in ["ingestion", "analysis", "decision"]:
            await save_artifact(sid, agent_name, "output", {"agent": agent_name})

        async with get_db() as db:
            result = await db.execute(
                select(AgentArtifact).where(AgentArtifact.session_id == sid)
            )
            artifacts = list(result.scalars().all())

        assert len(artifacts) == 3
        agent_names = {a.agent_name for a in artifacts}
        assert agent_names == {"ingestion", "analysis", "decision"}


class TestGetSessionArtifacts:
    async def test_returns_ordered_artifacts(self):
        from database.models import save_session, save_artifact, get_session_artifacts

        sid = generate_uuid()
        await save_session({
            "id": sid,
            "domain": "healthcare",
            "input_type": "text",
            "input_preview": "drug shortage",
            "status": "pending",
        })

        await save_artifact(sid, "ingestion", "signals", {"order": 1})
        await save_artifact(sid, "analysis", "impact", {"order": 2})
        await save_artifact(sid, "decision", "actions", {"order": 3})

        artifacts = await get_session_artifacts(sid)
        assert len(artifacts) == 3
        assert artifacts[0].agent_name == "ingestion"
        assert artifacts[1].agent_name == "analysis"
        assert artifacts[2].agent_name == "decision"

    async def test_returns_empty_for_unknown_session(self):
        from database.models import get_session_artifacts
        artifacts = await get_session_artifacts(generate_uuid())
        assert artifacts == []


class TestSessionTrace:
    async def test_session_trace_via_api(self, client):
        from database.models import save_session, save_artifact

        sid = generate_uuid()
        await save_session({
            "id": sid,
            "domain": "urban",
            "input_type": "text",
            "input_preview": "power outage",
            "status": "completed",
        })
        await save_artifact(sid, "ingestion", "signals", {"key": "value"})

        r = await client.get(f"/api/session/{sid}/trace")
        assert r.status_code == 200
        data = r.json()
        assert data["total_artifacts"] == 1
        assert data["artifacts"][0]["agent_name"] == "ingestion"
        assert data["session"]["domain"] == "urban"

    async def test_session_status_via_api(self, client):
        from database.models import save_session

        sid = generate_uuid()
        await save_session({
            "id": sid,
            "domain": "finance",
            "input_type": "csv",
            "input_preview": "rate data",
            "status": "completed",
        })

        r = await client.get(f"/api/session/{sid}/status")
        assert r.status_code == 200
        data = r.json()
        assert data["session_id"] == sid
        assert data["status"] == "completed"
