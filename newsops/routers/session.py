import asyncio
import json
from fastapi import APIRouter, HTTPException, Request
from utils.auth_middleware import get_org_from_request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select, desc

from database.db import get_db
from database.models import AnalysisSession, get_session_artifacts
from schemas.output_schemas import TraceArtifact, TraceResponse

router = APIRouter(prefix="/api", tags=["Session"])

async def _get_org_filter(request: Request):
    org = await get_org_from_request(request)
    if org:
        return AnalysisSession.org_id == org.id
    return None



@router.get("/sessions")
async def get_sessions(request: Request):
    """Retrieve the last 20 analysis sessions sorted by created_at descending."""
    async with get_db() as db:
        from sqlalchemy import func
        stmt_count = select(func.count(AnalysisSession.id))
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt_count = stmt_count.where(org_filter)
        count_result = await db.execute(stmt_count)
        total_count = count_result.scalar() or 0

        stmt = select(AnalysisSession)
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt = stmt.where(org_filter)
        stmt = stmt.order_by(desc(AnalysisSession.created_at)).limit(20)
        result = await db.execute(stmt)
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
async def get_session_trace(session_id: str, request: Request):
    artifacts_raw = await get_session_artifacts(session_id)

    async with get_db() as db:
        stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt = stmt.where(org_filter)
        result = await db.execute(stmt)
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
                            if (exec_artifact and exec_artifact.content) else "unknown",
    }


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str, request: Request):
    async with get_db() as db:
        stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt = stmt.where(org_filter)
        result = await db.execute(stmt)
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


@router.get("/session/{session_id}/task-status")
async def get_session_task_status(session_id: str, request: Request):
    async with get_db() as db:
        stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt = stmt.where(org_filter)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    celery_state = "UNKNOWN"
    result_ready = False
    if session.task_id:
        from celery.result import AsyncResult
        from celery_app import celery
        res = AsyncResult(session.task_id, app=celery)
        celery_state = res.state
        result_ready = res.ready()

    return {
        "session_id": session.id,
        "celery_state": celery_state,
        "db_status": session.status,
        "task_id": session.task_id,
        "result_ready": result_ready
    }


@router.get("/session/{session_id}/export/json")
async def export_session_json(session_id: str, request: Request):
    import json
    from fastapi import Response
    artifacts_raw = await get_session_artifacts(session_id)
    async with get_db() as db:
        stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt = stmt.where(org_filter)
        result = await db.execute(stmt)
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
async def export_session_csv(session_id: str, request: Request):
    import csv
    from io import StringIO
    from fastapi import Response
    artifacts_raw = await get_session_artifacts(session_id)
    async with get_db() as db:
        stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt = stmt.where(org_filter)
        result = await db.execute(stmt)
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
            summary = f"Status: {c.get('execution_status')}. Notifications sent: {len(c.get('notifications_sent', []))}"
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


@router.get("/session/{session_id}/export/pdf")
async def export_session_pdf_route(session_id: str, request: Request):
    from fastapi import Response
    from utils.pdf_report import generate_session_pdf
    
    artifacts_raw = await get_session_artifacts(session_id)
    async with get_db() as db:
        stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt = stmt.where(org_filter)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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
        pdf_bytes = generate_session_pdf(session_dict, artifacts_raw)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=newsops_report_{session_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ---------------------------------------------------------------------------

# SSE stream — maps pipeline status → agent label shown in the UI
# ---------------------------------------------------------------------------
_STATUS_AGENT: dict[str, str] = {
    "pending":    "orchestrator",
    "ingesting":  "ingestion",
    "researching":"research",
    "analysing":  "analysis",
    "deciding":   "decision",
    "executing":  "execution",
    "complete":   "orchestrator",
    "failed":     "orchestrator",
}
_TERMINAL = {"complete", "failed"}


@router.get("/session/{session_id}/stream", tags=["Session"])
async def stream_session_progress(session_id: str, request: Request):
    """Server-Sent Events endpoint that streams live pipeline status.

    Emits one SSE frame every 2 seconds until the session reaches
    ``complete`` or ``failed``, then emits a final frame and closes.

    Frame format::

        data: {"session_id": "...", "status": "...", "agent": "...", "timestamp": "..."}

    """
    from utils.helpers import now_iso

    async def _event_generator():
        # Verify session exists before opening the stream
        async with get_db() as db:
            stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
            org_filter = await _get_org_filter(request)
            if org_filter is not None: stmt = stmt.where(org_filter)
            check = await db.execute(stmt)
            if check.scalar_one_or_none() is None:
                payload = json.dumps({
                    "session_id": session_id,
                    "status": "error",
                    "agent": "orchestrator",
                    "timestamp": now_iso(),
                    "detail": f"Session {session_id} not found",
                })
                yield f"data: {payload}\n\n"
                return

        while True:
            async with get_db() as db:
                result = await db.execute(
                    select(AnalysisSession).where(AnalysisSession.id == session_id)
                )
                session = result.scalar_one_or_none()

            status = session.status if session else "error"
            agent  = _STATUS_AGENT.get(status, "orchestrator")

            payload = json.dumps({
                "session_id": session_id,
                "status":     status,
                "agent":      agent,
                "timestamp":  now_iso(),
            })
            yield f"data: {payload}\n\n"

            if status in _TERMINAL:
                break

            await asyncio.sleep(2)

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            # Prevent proxies / nginx from buffering the stream
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":       "keep-alive",
        },
    )


class EmailReportRequest(BaseModel):
    recipient_email: Optional[str] = None


@router.post("/session/{session_id}/email-report")
async def email_session_report(session_id: str, request: Request, body: EmailReportRequest = EmailReportRequest()):
    artifacts_raw = await get_session_artifacts(session_id)
    async with get_db() as db:
        stmt = select(AnalysisSession).where(AnalysisSession.id == session_id)
        org_filter = await _get_org_filter(request)
        if org_filter is not None:
            stmt = stmt.where(org_filter)
        result = await db.execute(stmt)
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
