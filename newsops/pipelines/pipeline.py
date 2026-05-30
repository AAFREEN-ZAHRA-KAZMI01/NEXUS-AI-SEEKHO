from typing import Optional

from utils.helpers import generate_uuid
from parsers.text_parser import parse_text, parse_url
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx
from parsers.csv_parser import parse_csv
from parsers.excel_parser import parse_excel
from agents.orchestrator import Orchestrator


async def run_pipeline(
    input_type: str,
    content: str = None,
    file_bytes: bytes = None,
    session_id: str = None,
    domain: Optional[str] = None,
) -> dict:
    if not session_id:
        session_id = generate_uuid()

    if input_type == "text":
        parsed = await parse_text(content)
    elif input_type == "url":
        parsed = await parse_url(content)
    elif input_type == "pdf":
        parsed = await parse_pdf(file_bytes, domain=domain or "business", use_vision=True)
    elif input_type == "docx":
        parsed = await parse_docx(file_bytes, domain=domain or "business", use_vision=True)
    elif input_type == "csv":
        parsed = await parse_csv(file_bytes)
    elif input_type == "excel":
        parsed = await parse_excel(file_bytes)
    elif input_type == "multi_document":
        parsed = await parse_text(content)
    else:
        raise ValueError(f"Unsupported input_type: {input_type}")

    if parsed.get("error"):
        raise ValueError(f"Parser failed: {parsed['reason']}")

    orchestrator = Orchestrator()
    result = await orchestrator.run(parsed, input_type, session_id)

    return result
