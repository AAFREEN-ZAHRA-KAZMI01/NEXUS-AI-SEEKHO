import json
import time
from config import GEMINI_API_KEY, MODELS, DEMO_MODE
from utils.logger import SessionLogger
from utils.helpers import retry, extract_json_from_text, now_iso
from utils.gemini_client import call_gemini


INGESTION_SYSTEM_PROMPT = """
# ROLE
You are the Ingestion Agent — a precision data extraction specialist in the NewsOps
autonomous intelligence system. Your sole responsibility is to read raw content and
extract a perfectly structured set of signals. You do NOT analyze, infer, or recommend.
You ONLY extract what is explicitly stated.

# CHAIN-OF-THOUGHT EXTRACTION PROTOCOL
Before producing output, silently work through these steps:
<thinking>
Step 1 — SCAN: Read the entire content once to understand the subject.
Step 2 — IDENTIFY ENTITIES: List every organization, location, person, regulation,
          product, and currency mentioned.
Step 3 — EXTRACT NUMBERS: Find every number. Pair each with its unit and context.
Step 4 — DETECT DIRECTION: For each number or claim, determine if it signals
          increase, decrease, stable, or neutral.
Step 5 — BUILD FACTS: Combine steps 3 and 4 into structured fact objects.
Step 6 — ASSESS CONFIDENCE: Official/regulatory = high, news media = medium,
          social/unverified = low.
</thinking>

# EXTRACTION RULES
1. Extract ONLY what is explicitly stated. Never infer.
2. Every fact must have a non-null "subject" field.
3. Every number must be paired with its unit and context.
4. Directional signals must be paired with their subject.
5. facts array: minimum 3 entries, maximum 15 entries.
6. If content is too sparse for 3 facts, extract what exists, set confidence to "low".
7. Capture both absolute and relative date references.
8. Source credibility: official/regulatory = "high", news = "medium", unverified = "low".

# DOMAIN-SPECIFIC EXTRACTION PRIORITIES
logistics:   shipment volumes, delivery costs, fuel prices, routes, carrier names, warehouse metrics
business:    revenue figures, order volumes, customer segments, regional breakdowns, SKUs
finance:     exchange rates (PKR/USD), interest rates, stock prices, fund values, P&L figures
policy:      regulation names, effective dates, regulatory body names, affected sectors
healthcare:  drug names, patient counts, shortage quantities, facility names, WHO/DRAP references
urban:       infrastructure metrics, population counts, zone names, utility readings, outage durations

# OUTPUT FORMAT
Respond with ONLY valid JSON. No markdown fences. No preamble. Raw JSON only.
{
  "agent": "ingestion",
  "input_type": "<text|url|pdf|docx|csv|excel>",
  "domain": "<domain>",
  "source": "<url, filename, or direct_text>",
  "timestamp": "<ISO 8601>",
  "facts": [
    {
      "text": "<exact extracted fact>",
      "subject": "<entity or metric this fact is about>",
      "direction": "<increase|decrease|stable|neutral>",
      "value": "<number or null>",
      "unit": "<unit string or null>",
      "date_reference": "<date string or null>"
    }
  ],
  "entities": {
    "organizations": [],
    "locations": [],
    "people": [],
    "regulations": [],
    "products": [],
    "currencies": []
  },
  "raw_numbers": [
    { "value": "<number>", "unit": "<unit>", "context": "<surrounding sentence>" }
  ],
  "document_meta": {
    "title": "<title or null>",
    "source_domain": "<domain if URL>",
    "total_rows": "<number if csv/excel or null>",
    "pages": "<number if pdf or null>"
  },
  "confidence": "<high|medium|low>"
}

# STRUCTURED DOCUMENT INPUT HANDLING

When the input includes structured extraction results (tables, charts, forms,
key_value_pairs), you MUST prioritize these over the raw clean_text.

PRIORITY ORDER FOR FACT EXTRACTION:
1. HIGHEST: key_value_pairs where is_high_signal=True — these are precisely extracted
2. HIGH: tables → key_insights field — these are pre-analyzed table summaries
3. HIGH: charts → key_insight field — these capture visual data not in text
4. MEDIUM: forms → fields where is_empty=False — form data is structured
5. LOWER: clean_text paragraphs — use for context and narrative

SPECIAL HANDLING:
- Table data: extract each numeric column trend as a separate fact
- Chart data: the key_insight is your fact — the chart_type and trend are metadata
- Form data: label+value pairs become facts directly — no inference needed
- KV pairs: treat as ground truth — these were precisely extracted

ACCURACY BOOST RULES:
- If a number appears in both clean_text AND a table/kv_pair, trust the table/kv version
- If a chart shows a trend, that trend is a fact even if not stated in text
- Cross-reference: if table says "revenue declined 25%" and text says "revenue fell",
  use the table's specific number (25%) as the fact value
"""


class IngestionAgent:
    def __init__(self, *args, **kwargs):
        self.session_id = args[0] if args else kwargs.get("session_id", "init")
        self.logger = SessionLogger(session_id=self.session_id)
        self.model = MODELS["ingestion"]
        self.client = GEMINI_API_KEY if (GEMINI_API_KEY and not GEMINI_API_KEY.startswith("AIzaSy_mock")) else None

    def _get_mock_response(self, domain: str, text: str) -> dict:
        """Fallback mock response when OpenAI is unavailable"""
        try:
            from agents.mock_responses import get_mock_ingestion
            return get_mock_ingestion(domain)
        except Exception:
            return {
              "agent": "ingestion",
              "input_type": "text",
              "domain": domain,
              "source": "direct_text",
              "timestamp": now_iso(),
              "facts": [
                {"text": f"Content analysis initiated for {domain} domain",
                 "subject": domain, "direction": "neutral",
                 "value": None, "unit": None, "date_reference": None},
                {"text": "Key business metrics detected in uploaded content",
                 "subject": "metrics", "direction": "stable",
                 "value": None, "unit": None, "date_reference": None},
                {"text": "Impact assessment in progress",
                 "subject": "impact", "direction": "neutral",
                 "value": None, "unit": None, "date_reference": None},
              ],
              "entities": {
                "organizations": [], "locations": [],
                "people": [], "regulations": [],
                "products": [], "currencies": ["PKR"]
              },
              "raw_numbers": [],
              "document_meta": {"title": None, "source_domain": None,
                                "total_rows": None, "pages": None},
              "confidence": "low"
            }

    @retry(times=2, delay=2.0)
    async def _call_llm(self, parsed_input: dict, domain: str, input_type: str) -> dict:
        clean_text = parsed_input.get('clean_text', '') if isinstance(parsed_input, dict) else parsed_input
        if DEMO_MODE or not GEMINI_API_KEY or GEMINI_API_KEY.startswith("AIzaSy_mock"):
            import asyncio
            await asyncio.sleep(1.2)
            mock_res = self._get_mock_response(domain, clean_text)
            mock_res["mock_mode_active"] = True

            # Send email warning about mock data activation
            try:
                from utils.email_service import send_mock_fallback_alert
                reason = "DEMO_MODE is active or GEMINI_API_KEY is missing/mock"
                send_mock_fallback_alert(domain, reason)
            except Exception as email_err:
                import logging
                logging.error(f"Failed to send mock fallback email: {email_err}")

            return mock_res

        if isinstance(parsed_input, dict):
            high_signal_kv = [
                p for p in parsed_input.get("key_value_pairs", [])
                if p.get("is_high_signal")
            ]

            user_message = f"""DOMAIN: {domain}
INPUT TYPE: {input_type}

CLEAN TEXT (reading-order, layout-aware):
{parsed_input.get('clean_text', '')[:4000]}

EXTRACTED TABLES ({len(parsed_input.get('tables', []))} found):
{json.dumps(parsed_input.get('tables', []), indent=2)[:3000]}

EXTRACTED CHARTS ({len(parsed_input.get('charts', []))} found):
{json.dumps(parsed_input.get('charts', []), indent=2)[:1000]}

KEY-VALUE PAIRS (high-precision extractions):
{json.dumps(high_signal_kv, indent=2)[:2000]}

SEMANTIC ANALYSIS (if available):
{json.dumps(parsed_input.get('semantic_analysis', {}), indent=2)[:500]}

Extract all signals using the priority order defined in your instructions.
Cross-reference across sources — tables and KV pairs override plain text for numbers.
"""
        else:
            user_message = (
                f"DOMAIN: {domain}\n"
                f"INPUT TYPE: {input_type}\n\n"
                f"CONTENT TO EXTRACT FROM:\n{clean_text}"
            )

        try:
            return await call_gemini(
                system_prompt=INGESTION_SYSTEM_PROMPT,
                user_message=user_message,
                model=self.model,
                temperature=0.1,
                expect_json=True,
            )
        except Exception as e:
            import logging
            logging.warning(f"Gemini call failed: {e}. Using mock response.")
            
            from utils.email_service import send_mock_fallback_alert
            send_mock_fallback_alert(domain, str(e))
            
            mock_res = self._get_mock_response(domain, clean_text)
            mock_res["mock_mode_active"] = True
            mock_res["mock_error"] = str(e)
            return mock_res

    async def run(self, parsed_input: dict, domain: str, *args, **kwargs) -> dict:
        session_id = kwargs.get("session_id")
        if not session_id and args:
            for arg in args:
                if isinstance(arg, str):
                    session_id = arg
                    break
        session_id = session_id or getattr(self, "session_id", None) or "session-default"
        logger = SessionLogger(session_id)
        logger.log("ingestion", "start")
        start_time = time.time()

        try:
            input_type = parsed_input.get("source_type", "text")
            result = await self._call_llm(parsed_input, domain, input_type)

            duration = time.time() - start_time
            logger.log("ingestion", "complete", {"duration": duration})

            result["model_used"] = MODELS["ingestion"]
            result["agent_display_name"] = "Ingestion Agent"

            return result
        except Exception as e:
            logger.log("ingestion", "error", {"error": str(e)})
            raise
