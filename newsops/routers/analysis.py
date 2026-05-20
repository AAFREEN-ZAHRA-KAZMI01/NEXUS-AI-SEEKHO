from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from pipelines.pipeline import run_pipeline
from schemas.input_schemas import TextAnalysisRequest, UrlAnalysisRequest
from schemas.output_schemas import AnalysisResponse
from utils.helpers import generate_uuid
from utils.logger import SessionLogger

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post("/analyse/text", response_model=AnalysisResponse)
async def analyse_text(body: TextAnalysisRequest):
    session_id = body.session_id or generate_uuid()
    logger = SessionLogger(session_id)
    logger.log("api", "analyse_text_request", {"session_id": session_id})
    try:
        result = await run_pipeline(
            input_type="text",
            content=body.content,
            session_id=session_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "session_id": session_id})


@router.post("/analyse/url", response_model=AnalysisResponse)
async def analyse_url(body: UrlAnalysisRequest):
    session_id = body.session_id or generate_uuid()
    logger = SessionLogger(session_id)
    logger.log("api", "analyse_url_request", {"session_id": session_id, "url": body.url})
    try:
        result = await run_pipeline(
            input_type="url",
            content=body.url,
            session_id=session_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "session_id": session_id})


@router.post("/analyse/file", response_model=AnalysisResponse)
async def analyse_file(
    file: UploadFile = File(...),
    input_type: str = Form(...),
    domain: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
):
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
        result = await run_pipeline(
            input_type=input_type,
            file_bytes=file_bytes,
            session_id=session_id,
            domain=domain,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "session_id": session_id})
