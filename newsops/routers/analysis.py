import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List

from database.models import save_session, update_session_task_id, increment_org_usage
from utils.auth_middleware import get_org_from_request, check_usage_limit
from schemas.input_schemas import TextAnalysisRequest, UrlAnalysisRequest
from utils.helpers import generate_uuid
from utils.logger import SessionLogger
from parsers.text_parser import parse_text
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx
from parsers.csv_parser import parse_csv
from parsers.excel_parser import parse_excel

router = APIRouter(prefix="/api", tags=["Analysis"])

# ---------------------------------------------------------------------------
# Internal helper — enqueue pipeline and persist task_id
# ---------------------------------------------------------------------------

async def _enqueue(parsed_input: dict, input_type: str, session_id: str) -> str:
    """Submit the pipeline task to Celery and return the Celery task ID."""
    from tasks.pipeline_task import run_pipeline_task

    # run_pipeline_task.delay() is a sync call — offload to thread so we
    # don't block the event loop.
    loop = asyncio.get_event_loop()
    task = await loop.run_in_executor(
        None,
        lambda: run_pipeline_task.delay(parsed_input, input_type, session_id),
    )
    return task.id


def _queued_response(session_id: str, task_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=202,
        content={
            "session_id": session_id,
            "task_id": task_id,
            "status": "queued",
            "poll_url": f"/api/session/{session_id}/status",
            "estimated_seconds": 45,
        },
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/analyse/text")
async def analyse_text(body: TextAnalysisRequest, request: Request):
    org = await get_org_from_request(request)
    if org:
        check_usage_limit(org)

    session_id = body.session_id or generate_uuid()
    logger = SessionLogger(session_id)
    logger.log("api", "analyse_text_request", {"session_id": session_id})

    parsed_input = {
        "content": body.content,
        "domain": body.domain,
    }

    # Persist session with status "queued"
    await save_session({
        "id": session_id,
        "input_type": "text",
        "input_preview": (body.content or "")[:300],
        "domain": body.domain,
        "status": "queued",
        "org_id": org.id if org else None,
    })

    try:
        task_id = await _enqueue(parsed_input, "text", session_id)
        await update_session_task_id(session_id, task_id)
        if org:
            await increment_org_usage(org.id)
        return _queued_response(session_id, task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "session_id": session_id})


@router.post("/analyse/url")
async def analyse_url(body: UrlAnalysisRequest, request: Request):
    org = await get_org_from_request(request)
    if org:
        check_usage_limit(org)

    session_id = body.session_id or generate_uuid()
    logger = SessionLogger(session_id)
    logger.log("api", "analyse_url_request", {"session_id": session_id, "url": body.url})

    parsed_input = {
        "content": body.url,
        "domain": body.domain,
    }

    await save_session({
        "id": session_id,
        "input_type": "url",
        "input_preview": body.url[:300],
        "domain": body.domain,
        "status": "queued",
        "org_id": org.id if org else None,
    })

    try:
        task_id = await _enqueue(parsed_input, "url", session_id)
        await update_session_task_id(session_id, task_id)
        if org:
            await increment_org_usage(org.id)
        return _queued_response(session_id, task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "session_id": session_id})


@router.post("/analyse/file")
async def analyse_file(
    request: Request,
    file: UploadFile = File(...),
    input_type: str = Form(...),
    domain: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
):
    org = await get_org_from_request(request)
    if org:
        check_usage_limit(org)

    session_id = session_id or generate_uuid()
    logger = SessionLogger(session_id)
    logger.log("api", "analyse_file_request", {
        "session_id": session_id,
        "input_type": input_type,
        "filename": file.filename,
        "domain": domain,
    })

    try:
        file_bytes = await file.read()

        # Encode bytes as list of ints so Celery can JSON-serialise it
        parsed_input = {
            "file_bytes": list(file_bytes),
            "filename": file.filename,
            "domain": domain,
        }

        await save_session({
            "id": session_id,
            "input_type": input_type,
            "input_preview": file.filename[:300],
            "domain": domain,
            "status": "queued",
            "org_id": org.id if org else None,
        })

        task_id = await _enqueue(parsed_input, input_type, session_id)
        await update_session_task_id(session_id, task_id)
        if org:
            await increment_org_usage(org.id)
        return _queued_response(session_id, task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "session_id": session_id})


@router.post("/analyse/multi")
async def analyse_multi(
    request: Request,
    files: List[UploadFile] = File(...),
    context: Optional[str] = Form(None),
    domain: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
):
    org = await get_org_from_request(request)
    if org:
        check_usage_limit(org)

    session_id = session_id or generate_uuid()
    logger = SessionLogger(session_id)

    if len(files) > 5:
        raise HTTPException(status_code=400, detail={"error": "Maximum 5 files allowed", "session_id": session_id})

    logger.log("api", "analyse_multi_request", {
        "session_id": session_id,
        "file_count": len(files),
        "domain": domain,
    })

    try:
        combined_texts = []
        if context:
            combined_texts.append(f"[CONTEXT]: {context}\n")

        for i, file in enumerate(files):
            file_bytes = await file.read()
            filename = file.filename
            ext = filename.split(".")[-1].lower() if "." in filename else "txt"

            if ext == "pdf":
                parsed = await parse_pdf(file_bytes, domain=domain or "business", use_vision=True)
            elif ext in ["docx", "doc"]:
                parsed = await parse_docx(file_bytes, domain=domain or "business", use_vision=True)
            elif ext == "csv":
                parsed = await parse_csv(file_bytes)
            elif ext in ["xlsx", "xls"]:
                parsed = await parse_excel(file_bytes)
            else:
                try:
                    text_content = file_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    text_content = file_bytes.decode("latin-1", errors="replace")
                parsed = await parse_text(text_content)

            if parsed.get("error"):
                raise ValueError(f"Failed to parse {filename}: {parsed.get('reason')}")

            extracted_text = parsed.get("clean_text", "")
            combined_texts.append(f"[SOURCE {i + 1} - {filename}]: {extracted_text}")

        combined_text = "\n\n".join(combined_texts)

        parsed_input = {
            "content": combined_text,
            "domain": domain,
        }

        await save_session({
            "id": session_id,
            "input_type": "multi_document",
            "input_preview": combined_text[:300],
            "domain": domain,
            "status": "queued",
            "org_id": org.id if org else None,
        })

        task_id = await _enqueue(parsed_input, "multi_document", session_id)
        await update_session_task_id(session_id, task_id)
        if org:
            await increment_org_usage(org.id)
        return _queued_response(session_id, task_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "session_id": session_id})


@router.get("/rag/stats")
async def get_rag_stats():
    try:
        from utils.rag_store import get_collection_stats
        return get_collection_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
