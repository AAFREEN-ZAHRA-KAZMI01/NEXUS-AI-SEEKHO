import io
import logging
import pdfplumber

from config import MAX_TEXT_CHARS
from parsers.document_intelligence import extract_document_intelligently

logger = logging.getLogger(__name__)


async def parse_pdf(file_bytes: bytes, domain: str = "business", use_vision: bool = True) -> dict:
    if use_vision:
        try:
            result = await extract_document_intelligently(file_bytes, "pdf", domain, use_vision=True)
            if result and result.get("clean_text"):
                return result
        except Exception as e:
            logger.warning("Vision extraction failed, falling back to basic: %s", e)

    # Basic fallback with pdfplumber
    try:
        combined_text = []
        tables_list = []
        has_tables = False

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_count = len(pdf.pages)
            for n, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    text = f"[Page {n}: no text extracted — may be scanned]"

                tables = page.extract_tables()
                if tables:
                    has_tables = True
                    for table in tables:
                        md_table = []
                        for row in table:
                            row_str = " | ".join(str(cell) if cell is not None else "" for cell in row)
                            md_table.append(f"| {row_str} |")
                        if md_table:
                            md_str = "\n".join(md_table)
                            tables_list.append(md_str)
                            text += f"\n\n[Table found on page {n}]\n{md_str}\n"

                combined_text.append(f"--- Page {n} ---\n\n{text}")

        combined = "\n\n".join(combined_text)
        return {
            "clean_text": combined[:MAX_TEXT_CHARS],
            "pages_count": pages_count,
            "has_tables": has_tables,
            "tables_extracted": tables_list,
            "source_type": "pdf",
            "extraction_method": "basic_ocr",
        }
    except Exception as e:
        return {"error": True, "reason": str(e), "clean_text": ""}
