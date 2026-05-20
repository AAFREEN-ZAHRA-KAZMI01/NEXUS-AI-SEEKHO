import io
import json
import os
import subprocess
import tempfile

import fitz  # pymupdf
from PIL import Image
from google import genai as google_genai
from google.genai import types as genai_types
from config import MODELS, GEMINI_API_KEY

_vision_client = google_genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
from parsers.ocr_utils import pdf_to_images, image_to_base64, run_tesseract_ocr, is_scanned_page

# ─────────────────────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

LAYOUT_DETECTION_PROMPT = """
# ROLE
You are a Document Layout Detection specialist. You analyze document page
images and identify distinct visual regions with their semantic types.

# TASK
Examine this document page image carefully. Identify ALL distinct layout
regions present on the page.

# REGION TYPES TO DETECT
- "title": Main document title or section heading
- "paragraph": Body text paragraph
- "table": Any tabular data with rows and columns
- "chart": Any graph, chart, figure, or visualization
- "caption": Text label describing a table or chart
- "list": Bullet points or numbered lists
- "header": Page header (top of page, repeated)
- "footer": Page footer (bottom of page, repeated)
- "form_field": Label-value pairs in a form structure
- "key_value": Standalone key:value data pairs
- "sidebar": Secondary content column
- "footnote": Small text at bottom referencing main content

# READING ORDER RULE
Assign each region a reading_order integer starting from 1.
Reading order follows: top-to-bottom, left-to-right for single column.
For multi-column: complete left column first, then right column.

# CRITICAL ACCURACY RULES
1. Never merge a table and its caption into the same region — they are separate
2. A chart and its caption are separate regions but mark them as related
3. Form fields (label + input box) are "form_field" type, not "key_value"
4. If text is inside a bordered box → likely "table" or "form_field"
5. Headers and footers repeat across pages — mark them as such

# OUTPUT
Respond with ONLY valid JSON. No markdown. Raw JSON only.
{
  "regions": [
    {
      "id": 1,
      "type": "<region_type>",
      "reading_order": <integer>,
      "content_preview": "<first 50 chars of content in this region>",
      "is_high_signal": <true if this region likely contains key facts>,
      "related_region_id": <id of caption/chart it relates to, or null>
    }
  ],
  "layout_type": "<single_column|two_column|form|mixed>",
  "has_tables": <boolean>,
  "has_charts": <boolean>,
  "has_forms": <boolean>,
  "estimated_data_density": "<low|medium|high>"
}
"""

TABLE_EXTRACTION_PROMPT = """
# ROLE
You are a Table Extraction specialist. You see a document page containing
a table. Extract the table with perfect structural fidelity.

# CHAIN-OF-THOUGHT TABLE READING PROTOCOL
<thinking>
Step 1 — IDENTIFY HEADERS: Find the header row(s). Are there multi-level headers?
         Multi-level headers span multiple rows — treat them as a hierarchy.
Step 2 — IDENTIFY MERGED CELLS: Look for cells that span multiple columns or rows.
         Record the span range.
Step 3 — READ DATA ROWS: For each data row, match each cell to its column header.
         Empty cells must be recorded as null — never skip them.
Step 4 — DETECT UNITS: Are values in a column numeric? What unit? (PKR, %, USD, kg)
         Record units in the column definition, not in every cell.
Step 5 — FIND TOTALS ROW: Is the last row a subtotal or total? Mark it.
Step 6 — EXTRACT CAPTION: Is there text immediately above or below the table
         that serves as a caption or table number? Record it.
</thinking>

# TABLE EXTRACTION RULES
1. Merged cells: if a cell spans columns 2-4, repeat the value for columns 2, 3, 4
2. Multi-level headers: represent as "Parent Header > Child Header"
3. Empty cells: use null not "" — empty is meaningful (no data) vs. not present
4. Numbers: extract as numbers not strings — "1,234" → 1234, "45%" → 0.45
5. Total/subtotal rows: mark with "is_summary_row": true
6. Never flatten a 2D table into a 1D list

# OUTPUT FORMAT
Respond with ONLY valid JSON. Raw JSON only.
{
  "table_type": "<data_table|comparison_table|summary_table|form_table>",
  "caption": "<table caption or null>",
  "headers": ["<col1>", "<col2>"],
  "units": {"<col_name>": "<unit or null>"},
  "rows": [
    {"<col1>": <value>, "<col2>": <value>, "is_summary_row": false}
  ],
  "has_merged_cells": <boolean>,
  "has_multi_level_headers": <boolean>,
  "numeric_columns": ["<col_name>"],
  "key_insights": ["<1-2 sentence insight about what this table shows>"]
}
"""

CHART_EXTRACTION_PROMPT = """
# ROLE
You are a Data Visualization Analysis specialist. You see a chart or graph
in a document. Extract the data and meaning it communicates.

# CHAIN-OF-THOUGHT CHART READING PROTOCOL
<thinking>
Step 1 — CHART TYPE: What kind of chart? (bar, line, pie, scatter, area, histogram, heatmap)
Step 2 — AXES: What are the X and Y axes? What are their labels and units?
Step 3 — DATA SERIES: How many data series? What are they named?
Step 4 — DATA POINTS: Read approximate values from the chart.
         For bar charts: read bar heights.
         For line charts: read key points (peaks, troughs, endpoints).
         For pie charts: read segment percentages.
Step 5 — TREND: What is the overall trend or pattern the chart communicates?
Step 6 — CAPTION: Is there a title on the chart itself? A label below it?
Step 7 — KEY INSIGHT: What is the single most important thing this chart shows?
</thinking>

# ACCURACY RULES
1. Only read values you can see clearly — use null for values you cannot read precisely
2. Mark approximate values with "approximate": true
3. For time-series: always note the time range shown
4. For comparisons: identify the highest and lowest values explicitly
5. Never hallucinate data points — uncertainty is better than invention

# OUTPUT FORMAT
Respond with ONLY valid JSON. Raw JSON only.
{
  "chart_type": "<bar|line|pie|scatter|area|histogram|heatmap|other>",
  "title": "<chart title or null>",
  "caption": "<external caption text or null>",
  "x_axis": {"label": "<label>", "unit": "<unit or null>"},
  "y_axis": {"label": "<label>", "unit": "<unit or null>"},
  "data_series": [
    {
      "name": "<series name>",
      "data_points": [{"x": "<value>", "y": "<value>", "approximate": false}]
    }
  ],
  "trend": "<upward|downward|stable|cyclical|mixed>",
  "key_insight": "<1-2 sentences: what is the most important thing this chart shows>",
  "dominant_value": "<the highest or most prominent data point>",
  "time_range": "<if time-series, e.g. Jan 2023 - Dec 2024 or null>"
}
"""

FORM_EXTRACTION_PROMPT = """
# ROLE
You are a Form Data Extraction specialist. You receive text from a form region
of a document. Extract all label-value pairs with perfect accuracy.

# CHAIN-OF-THOUGHT FORM READING PROTOCOL
<thinking>
Step 1 — FIELD IDENTIFICATION: Find every label. Labels are typically:
  - Followed by a colon (:)
  - Followed by an underline or blank space
  - In a smaller or lighter font than values
  - Left-aligned with values right-aligned or indented
Step 2 — VALUE EXTRACTION: For each label, find its corresponding value.
  - Values can be: text, numbers, dates, checkboxes (checked/unchecked), signatures
  - Empty fields: record as null, not ""
Step 3 — FIELD GROUPING: Are fields grouped into sections? Identify section headers.
Step 4 — DATA TYPES: Infer the data type of each value:
  date, currency, percentage, text, integer, boolean (checkbox), signature
Step 5 — REQUIRED FIELDS: Are any fields marked as required (*)? Note them.
</thinking>

# FORM EXTRACTION RULES
1. Checkbox fields: return true (checked) or false (unchecked) not text
2. Currency fields: return as number, note currency symbol separately
3. Date fields: convert to ISO format (YYYY-MM-DD) if format is recognizable
4. Blank/empty fields: return null — they represent missing data
5. Signature fields: return "signed" or "unsigned" as boolean
6. Never combine a label with its value into a single string

# OUTPUT FORMAT
Respond with ONLY valid JSON. Raw JSON only.
{
  "form_type": "<application|invoice|report|registration|survey|other>",
  "sections": [
    {
      "section_name": "<section header or null>",
      "fields": [
        {
          "label": "<field label>",
          "value": "<extracted value>",
          "data_type": "<text|number|date|currency|boolean|signature>",
          "is_empty": <boolean>,
          "is_required": <boolean>
        }
      ]
    }
  ],
  "total_fields": <number>,
  "empty_fields": <number>,
  "completion_pct": <filled/total * 100>
}
"""

KV_EXTRACTION_PROMPT = """
# ROLE
You are a Key-Value Extraction specialist. You receive text that contains
important data in label:value format outside of tables or forms.

# EXTRACTION RULES
1. Extract EVERY label:value pair visible in the text
2. Normalize labels: "Total Amount:" and "TOTAL AMT" both → "total_amount"
   (snake_case, lowercase, no special characters)
3. Normalize values:
   - Currency: "PKR 1,23,456" → {"value": 123456, "currency": "PKR"}
   - Percentage: "45.2%" → {"value": 0.452, "type": "percentage"}
   - Date: "12-Nov-2024" → "2024-11-12"
   - Plain text: keep as string
4. Flag high-signal pairs: numeric values, percentages, dates, named entities
5. Group related pairs if they clearly belong together

# OUTPUT FORMAT
Respond with ONLY valid JSON. Raw JSON only.
{
  "pairs": [
    {
      "label": "<normalized_label>",
      "raw_label": "<original label text>",
      "value": "<normalized value>",
      "raw_value": "<original value text>",
      "data_type": "<text|number|currency|percentage|date>",
      "is_high_signal": <boolean>
    }
  ],
  "high_signal_count": <number>,
  "currencies_found": ["<currency1>"],
  "dates_found": ["<ISO date>"]
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _find_region_type(text: str, regions: list) -> str:
    text_lower = text.lower()[:50]
    for region in regions:
        preview = region.get("content_preview", "").lower()[:50]
        if preview and (preview in text_lower or text_lower in preview):
            return region.get("type", "paragraph")
    return "paragraph"


def _find_high_signal(text: str, regions: list) -> bool:
    text_lower = text.lower()[:50]
    for region in regions:
        preview = region.get("content_preview", "").lower()[:50]
        if preview and (preview in text_lower or text_lower in preview):
            return bool(region.get("is_high_signal", False))
    return False


def _table_to_text(table: dict) -> str:
    return table.get("markdown", "") or f"[Table: {table.get('caption', 'extracted')}]"


def _chart_to_text(chart: dict) -> str:
    return chart.get("text_summary", f"[CHART: {chart.get('key_insight', '')}]")


def _form_to_text(form: dict) -> str:
    lines = []
    for section in form.get("sections", []):
        if section.get("section_name"):
            lines.append(f"FORM SECTION: {section['section_name']}")
        for field in section.get("fields", []):
            if not field.get("is_empty"):
                lines.append(f"{field['label']}: {field['value']}")
    return "\n".join(lines)


def _kv_to_text(kv: dict) -> str:
    lines = []
    for pair in kv.get("pairs", []):
        label = pair.get("raw_label", pair.get("label", ""))
        value = pair.get("raw_value", pair.get("value", ""))
        lines.append(f"{label}: {value}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# TECHNIQUE 1: LAYOUT DETECTION
# ─────────────────────────────────────────────────────────────────────────────

async def detect_layout_regions(page_image: Image.Image) -> dict:
    if not _vision_client:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    config = genai_types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json",
        system_instruction=LAYOUT_DETECTION_PROMPT,
    )
    response = await _vision_client.aio.models.generate_content(
        model="gemini-1.5-flash",
        contents=[page_image, "Analyze this document page and identify all layout regions."],
        config=config,
    )
    return json.loads(response.text.strip())


# ─────────────────────────────────────────────────────────────────────────────
# TECHNIQUE 2: READING ORDER SORTING
# ─────────────────────────────────────────────────────────────────────────────

def sort_by_reading_order(regions: list, raw_text_blocks: list, layout_info: dict = None) -> list:
    layout_type = (layout_info or {}).get("layout_type", "single_column")

    text_blocks = [
        (b[0], b[1], b[2], b[3], b[4])
        for b in raw_text_blocks
        if len(b) >= 5 and isinstance(b[4], str) and b[4].strip()
    ]

    if not text_blocks:
        return []

    if layout_type == "two_column":
        all_x1 = [b[2] for b in text_blocks]
        page_width = max(all_x1) if all_x1 else 595
        mid = page_width / 2

        left = sorted([(b[1], b[4]) for b in text_blocks if b[0] < mid], key=lambda x: x[0])
        right = sorted([(b[1], b[4]) for b in text_blocks if b[0] >= mid], key=lambda x: x[0])
        ordered_texts = left + right
    else:
        ordered_texts = sorted([(b[1], b[4]) for b in text_blocks], key=lambda x: x[0])

    result = []
    for idx, (_, text) in enumerate(ordered_texts):
        if text.strip():
            result.append({
                "region_type": _find_region_type(text, regions),
                "content": text.strip(),
                "reading_order": idx + 1,
                "is_high_signal": _find_high_signal(text, regions),
            })
    return result


# ─────────────────────────────────────────────────────────────────────────────
# TECHNIQUE 4: TABLE EXTRACTION WITH VISION GROUNDING
# ─────────────────────────────────────────────────────────────────────────────

async def extract_table_with_vision(page_image: Image.Image, region: dict) -> dict:
    if not _vision_client:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    config = genai_types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json",
        system_instruction=TABLE_EXTRACTION_PROMPT,
    )
    response = await _vision_client.aio.models.generate_content(
        model="gemini-1.5-flash",
        contents=[page_image, f"Extract the table from this document page. Region context: {region.get('content_preview', '')}"],
        config=config,
    )
    result = json.loads(response.text.strip())

    headers = result.get("headers", [])
    rows = result.get("rows", [])
    if headers and rows:
        md_lines = ["| " + " | ".join(str(h) for h in headers) + " |"]
        md_lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        for row in rows:
            cells = [str(row.get(h, "")) for h in headers]
            md_lines.append("| " + " | ".join(cells) + " |")
        result["markdown"] = "\n".join(md_lines)
    else:
        result["markdown"] = ""

    return result


# ─────────────────────────────────────────────────────────────────────────────
# TECHNIQUE 5: CHART / VISUALIZATION UNDERSTANDING
# ─────────────────────────────────────────────────────────────────────────────

async def extract_chart_meaning(page_image: Image.Image, region: dict) -> dict:
    if not _vision_client:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    config = genai_types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json",
        system_instruction=CHART_EXTRACTION_PROMPT,
    )
    response = await _vision_client.aio.models.generate_content(
        model="gemini-1.5-flash",
        contents=[page_image, f"Extract the chart data and meaning from this document page. Region context: {region.get('content_preview', '')}"],
        config=config,
    )
    result = json.loads(response.text.strip())
    result["text_summary"] = f"[CHART: {result.get('chart_type', 'unknown')} — {result.get('key_insight', '')}]"
    return result


# ─────────────────────────────────────────────────────────────────────────────
# TECHNIQUE 6: FORM FIELD EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

async def extract_form_fields(text: str, region: dict) -> dict:
    from utils.gemini_client import call_gemini
    return await call_gemini(
        system_prompt=FORM_EXTRACTION_PROMPT,
        user_message=f"Extract form fields from this text:\n\n{text}",
        model="gemini-1.5-flash",
        temperature=0.1,
        expect_json=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TECHNIQUE 7: KEY-VALUE PAIR EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

async def extract_key_value_pairs(text: str) -> dict:
    from utils.gemini_client import call_gemini
    return await call_gemini(
        system_prompt=KV_EXTRACTION_PROMPT,
        user_message=f"Extract key-value pairs from this text:\n\n{text}",
        model=MODELS.get("input_parser", "gemini-1.5-flash"),
        temperature=0.1,
        expect_json=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TECHNIQUE 3: SEMANTIC REGION DISPATCH
# ─────────────────────────────────────────────────────────────────────────────

async def extract_region_content(region: dict, page_image: Image.Image, raw_text: str) -> dict:
    rtype = region.get("type", "paragraph")
    if rtype == "table":
        return await extract_table_with_vision(page_image, region)
    elif rtype == "chart":
        return await extract_chart_meaning(page_image, region)
    elif rtype == "form_field":
        return await extract_form_fields(raw_text, region)
    elif rtype == "key_value":
        return await extract_key_value_pairs(raw_text)
    else:
        return {"type": rtype, "content": raw_text, "structured": False}


# ─────────────────────────────────────────────────────────────────────────────
# TECHNIQUE 8: SCANNED PDF FALLBACK (OCR)
# ─────────────────────────────────────────────────────────────────────────────

def ocr_page_fallback(page_image: Image.Image) -> str:
    return run_tesseract_ocr(page_image)["text"]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATION
# ─────────────────────────────────────────────────────────────────────────────

async def extract_document_intelligently(
    file_bytes: bytes,
    file_type: str,
    domain: str,
    use_vision: bool = True,
) -> dict:
    all_text_blocks: list = []
    all_raw_text: list = []
    pages_count = 0

    # ── STEP 1: BASIC TEXT EXTRACTION ────────────────────────────────────────
    if file_type == "pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_count = len(doc)
        for page_num in range(min(pages_count, 10)):
            page = doc[page_num]
            all_text_blocks.append(page.get_text("blocks"))
            all_raw_text.append(page.get_text("text"))

    elif file_type == "docx":
        # Try LibreOffice PDF conversion for full vision pipeline
        pdf_bytes = None
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                docx_path = os.path.join(tmpdir, "input.docx")
                with open(docx_path, "wb") as f:
                    f.write(file_bytes)
                subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", tmpdir, docx_path],
                    capture_output=True,
                    timeout=30,
                )
                pdf_path = os.path.join(tmpdir, "input.pdf")
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
        except Exception:
            pass

        if pdf_bytes:
            return await extract_document_intelligently(pdf_bytes, "pdf", domain, use_vision)

        # Fall back to python-docx
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        raw_text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        all_raw_text.append(raw_text)
        all_text_blocks.append([])
        pages_count = 1

    # ── STEP 2: PAGE-LEVEL VISION ANALYSIS ───────────────────────────────────
    page_images: list = []
    if use_vision and file_type == "pdf":
        try:
            page_images = pdf_to_images(file_bytes, dpi=150, max_pages=10)
        except Exception:
            use_vision = False

    # ── STEP 3: REGION-BY-REGION EXTRACTION ──────────────────────────────────
    all_tables: list = []
    all_charts: list = []
    all_forms: list = []
    all_kv_pairs: list = []
    all_text_regions: list = []
    layout_info_global: dict = {}

    for page_idx, (text_blocks, raw_text) in enumerate(zip(all_text_blocks, all_raw_text)):
        if is_scanned_page(raw_text) and page_idx < len(page_images):
            raw_text = ocr_page_fallback(page_images[page_idx])

        if use_vision and page_idx < len(page_images):
            page_image = page_images[page_idx]
            try:
                layout_info = await detect_layout_regions(page_image)
                regions = layout_info.get("regions", [])
                if not layout_info_global:
                    layout_info_global = layout_info

                ordered_blocks = sort_by_reading_order(regions, text_blocks, layout_info)

                for block in ordered_blocks:
                    rtype = block["region_type"]
                    content = block["content"]

                    if rtype == "table":
                        table_result = await extract_table_with_vision(page_image, block)
                        all_tables.append(table_result)
                        all_text_regions.append({
                            "type": "table",
                            "content": _table_to_text(table_result),
                            "reading_order": block["reading_order"],
                        })
                    elif rtype == "chart":
                        chart_result = await extract_chart_meaning(page_image, block)
                        all_charts.append(chart_result)
                        all_text_regions.append({
                            "type": "chart",
                            "content": _chart_to_text(chart_result),
                            "reading_order": block["reading_order"],
                        })
                    elif rtype == "form_field":
                        form_result = await extract_form_fields(content, block)
                        all_forms.append(form_result)
                        all_text_regions.append({
                            "type": "form_field",
                            "content": _form_to_text(form_result),
                            "reading_order": block["reading_order"],
                        })
                    elif rtype == "key_value":
                        kv_result = await extract_key_value_pairs(content)
                        all_kv_pairs.extend(kv_result.get("pairs", []))
                        all_text_regions.append({
                            "type": "key_value",
                            "content": _kv_to_text(kv_result),
                            "reading_order": block["reading_order"],
                        })
                    else:
                        all_text_regions.append({
                            "type": rtype,
                            "content": content,
                            "reading_order": block["reading_order"],
                        })
            except Exception:
                if raw_text.strip():
                    all_text_regions.append({
                        "type": "paragraph",
                        "content": raw_text,
                        "reading_order": len(all_text_regions) + 1,
                    })
        else:
            if raw_text.strip():
                all_text_regions.append({
                    "type": "paragraph",
                    "content": raw_text,
                    "reading_order": len(all_text_regions) + 1,
                })

    # ── STEP 4: DOCUMENT-LEVEL SYNTHESIS ─────────────────────────────────────
    clean_parts = []
    for region in sorted(all_text_regions, key=lambda x: x.get("reading_order", 0)):
        rtype = region["type"]
        content = region["content"]
        if rtype == "title":
            clean_parts.append(f"# {content}")
        else:
            clean_parts.append(content)

    clean_text = "\n\n".join(clean_parts)

    if not clean_text.strip():
        clean_text = "\n".join(t for t in all_raw_text if t.strip())

    clean_text = clean_text[:8000]

    # Build high-signal facts
    high_signal_facts = []
    for t in all_tables:
        for insight in t.get("key_insights", []):
            if insight:
                high_signal_facts.append(insight)
    for c in all_charts:
        if c.get("key_insight"):
            high_signal_facts.append(c["key_insight"])
    for pair in all_kv_pairs:
        if pair.get("is_high_signal"):
            label = pair.get("raw_label", pair.get("label", ""))
            value = pair.get("raw_value", pair.get("value", ""))
            high_signal_facts.append(f"{label}: {value}")

    if use_vision and page_images:
        confidence = "high"
    elif all_raw_text and any(len(t.strip()) > 200 for t in all_raw_text):
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "clean_text": clean_text,
        "source_type": file_type,
        "pages_count": pages_count,
        "layout_type": layout_info_global.get("layout_type", "single_column"),
        "extraction_method": "agentic_vision" if (use_vision and page_images) else "basic_text",
        "document_structure": {
            "has_tables": bool(all_tables) or layout_info_global.get("has_tables", False),
            "has_charts": bool(all_charts) or layout_info_global.get("has_charts", False),
            "has_forms": bool(all_forms) or layout_info_global.get("has_forms", False),
            "table_count": len(all_tables),
            "chart_count": len(all_charts),
            "form_count": len(all_forms),
        },
        "tables": all_tables,
        "charts": all_charts,
        "forms": all_forms,
        "key_value_pairs": all_kv_pairs,
        "high_signal_facts": high_signal_facts[:20],
        "reading_order_regions": all_text_regions,
        "word_count": len(clean_text.split()),
        "confidence": confidence,
    }
