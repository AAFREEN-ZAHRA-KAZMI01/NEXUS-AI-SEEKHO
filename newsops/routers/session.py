from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select, desc

from database.db import get_db
from database.models import AnalysisSession, get_session_artifacts
from schemas.output_schemas import TraceArtifact, TraceResponse

router = APIRouter(prefix="/api", tags=["Session"])


@router.get("/sessions")
async def get_sessions():
    """Retrieve the last 20 analysis sessions sorted by created_at descending."""
    async with get_db() as db:
        from sqlalchemy import func
        count_result = await db.execute(select(func.count(AnalysisSession.id)))
        total_count = count_result.scalar() or 0

        result = await db.execute(
            select(AnalysisSession)
            .order_by(desc(AnalysisSession.created_at))
            .limit(20)
        )
        sessions = result.scalars().all()

    return {
        "sessions": [
            {
                "id": s.id,
                "domain": s.domain,
                "input_type": s.input_type,
                "input_preview": (s.input_preview[:80] + "...") if s.input_preview and len(s.input_preview) > 80 else (s.input_preview or ""),
                "status": s.status,
                "duration_seconds": s.duration_seconds,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sessions
        ],
        "total": total_count
    }


@router.get("/session/{session_id}/trace")
async def get_session_trace(session_id: str):
    artifacts_raw = await get_session_artifacts(session_id)

    async with get_db() as db:
        result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        session = result.scalar_one_or_none()

    session_dict = {}
    if session:
        session_dict = {
            "id": session.id,
            "domain": session.domain,
            "input_type": session.input_type,
            "input_preview": session.input_preview,
            "status": session.status,
            "error_detail": session.error_detail,
            "duration_seconds": session.duration_seconds,
            "created_at": session.created_at.isoformat() if session.created_at else None,
        }

    artifacts = [
        TraceArtifact(
            id=a.id,
            session_id=a.session_id,
            agent_name=a.agent_name,
            artifact_type=a.artifact_type,
            content=a.content,
            created_at=a.created_at.isoformat() if a.created_at else None,
            duration_seconds=a.duration_seconds,
        )
        for a in artifacts_raw
    ]

    # Find exec_log artifact and extract notifications
    exec_artifact = next(
        (a for a in artifacts if a.artifact_type == "exec_log"), None)
    
    notifications = []
    if exec_artifact and exec_artifact.content:
        notifications = exec_artifact.content.get("notifications_sent", [])
    
    return {
        "session": session_dict,
        "artifacts": [a.model_dump() for a in artifacts],
        "total_artifacts": len(artifacts),
        "pipeline_duration_seconds": session.duration_seconds if session else None,
        "notifications_sent": notifications,
        "execution_status": exec_artifact.content.get("execution_status") 
                            if exec_artifact else "unknown",
    }


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    async with get_db() as db:
        result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return {
        "session_id": session.id,
        "status": session.status,
        "domain": session.domain,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "duration_seconds": session.duration_seconds,
    }


@router.get("/session/{session_id}/export/json")
async def export_session_json(session_id: str):
    import json
    from fastapi import Response
    artifacts_raw = await get_session_artifacts(session_id)
    async with get_db() as db:
        result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    data = {
        "session": {
            "id": session.id,
            "domain": session.domain,
            "input_type": session.input_type,
            "input_preview": session.input_preview,
            "status": session.status,
            "duration_seconds": session.duration_seconds,
            "created_at": session.created_at.isoformat() if session.created_at else None,
        },
        "artifacts": [
            {
                "agent_name": a.agent_name,
                "artifact_type": a.artifact_type,
                "content": a.content,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in artifacts_raw
        ]
    }
    
    json_str = json.dumps(data, indent=2)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=session_{session_id}.json"}
    )


@router.get("/session/{session_id}/export/csv")
async def export_session_csv(session_id: str):
    import csv
    from io import StringIO
    from fastapi import Response
    artifacts_raw = await get_session_artifacts(session_id)
    async with get_db() as db:
        result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Session ID", session.id])
    writer.writerow(["Domain", session.domain])
    writer.writerow(["Input Type", session.input_type])
    writer.writerow(["Status", session.status])
    writer.writerow([])
    writer.writerow(["Agent Name", "Artifact Type", "Created At", "Duration (s)", "Key Insights / Content Summary"])
    
    for a in artifacts_raw:
        summary = ""
        c = a.content or {}
        if a.artifact_type == "master_brief":
            summary = c.get("insight", "")
        elif a.artifact_type == "signals":
            facts = c.get("facts", [])
            summary = "; ".join([f.get("text", "") for f in facts[:2]])
        elif a.artifact_type == "exec_log":
            summary = f"Status: {c.get('execution_status')}. Actions taken: {len(c.get('actions_taken', []))}"
        elif a.artifact_type == "actions":
            summary = f"Ranked actions: {len(c.get('actions', []))}"
        else:
            summary = str(c.keys())
            
        writer.writerow([
            a.agent_name,
            a.artifact_type,
            a.created_at.isoformat() if a.created_at else "",
            a.duration_seconds or "",
            summary
        ])
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=session_{session_id}.csv"}
    )


class EmailReportRequest(BaseModel):
    recipient_email: Optional[str] = None


@router.post("/session/{session_id}/email-report")
async def email_session_report(session_id: str, body: EmailReportRequest = EmailReportRequest()):
    artifacts_raw = await get_session_artifacts(session_id)
    async with get_db() as db:
        result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    from utils.email_service import send_html_report_email
    
    session_dict = {
        "id": session.id,
        "domain": session.domain,
        "input_type": session.input_type,
        "input_preview": session.input_preview,
        "status": session.status,
        "duration_seconds": session.duration_seconds,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }
    
    try:
        send_html_report_email(session_id, session_dict, artifacts_raw, recipient_email=body.recipient_email)
        to_addr = body.recipient_email or "configured SMTP address"
        return {"status": "success", "message": f"Email sent successfully to {to_addr}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
