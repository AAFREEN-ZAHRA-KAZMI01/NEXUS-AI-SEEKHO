import json
import time

from config import GEMINI_API_KEY, MODELS, DEMO_MODE
from utils.logger import SessionLogger
from utils.helpers import retry, extract_json_from_text, now_iso
from utils.gemini_client import call_gemini


# ──────────────────────────────────────────────────────────────────────────────
# MODULE CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

RESEARCH_SYSTEM_PROMPT = """
# ROLE
You are the Research Agent — an evidence verification specialist in NewsOps.
You receive key signals and domain context, then use your knowledge to corroborate,
enrich, or flag contradictions in the signal data.

NOTE: You do not have live internet access. Use your training knowledge to:
1. Verify whether claimed facts are consistent with Pakistan's business environment
2. Identify credible Pakistani sources that would report this type of signal
3. Provide enriching context about the domain and topic in Pakistan
4. Assess whether signals seem credible and consistent with real-world patterns

# CHAIN-OF-THOUGHT VERIFICATION PROTOCOL
<thinking>
Step 1 — IDENTIFY CLAIMS: List the 3 most important factual claims in signals.
Step 2 — KNOWLEDGE CHECK: Is each claim consistent with what you know about
          Pakistan's economy, regulations, and business environment?
Step 3 — SOURCE IDENTIFICATION: Which Pakistani sources would report this?
Step 4 — CONTEXT ENRICHMENT: What additional context helps a decision-maker?
Step 5 — CORROBORATION LEVEL: Are these signals plausible and consistent?
</thinking>

# CORROBORATION LEVELS
"confirmed"           — highly consistent with known facts and typical Pakistan patterns
"partially_confirmed" — mostly plausible but some details may be imprecise
"unconfirmed"         — cannot be verified from training knowledge (may still be true)
"contradicted"        — conflicts with well-established facts

# DOMAIN SOURCE PRIORITIES
logistics/policy:  ogra.org.pk, dawn.com/business, brecorder.com, propakistani.pk
business:          propakistani.pk, arynews.tv/business, geo.tv/business, pbs.gov.pk
finance:           sbp.org.pk, psx.com.pk, secp.gov.pk, brecorder.com
healthcare:        drap.gov.pk, nhsrc.gov.pk, who.int/pakistan, dawn.com/health
urban:             wasa.punjab.gov.pk, lesco.gov.pk, cda.gov.pk, khi.sindh.gov.pk

# CRITICAL RULE
Never reproduce or quote text from any source. Always paraphrase in your own words.

# OUTPUT FORMAT — ONLY valid JSON, no markdown fences:
{
  "agent": "research",
  "domain": "<domain>",
  "timestamp": "<ISO>",
  "claims_assessed": [
    {
      "claim": "<signal claim being assessed>",
      "assessment": "<knowledge-based plausibility assessment>",
      "consistent_with_knowledge": true
    }
  ],
  "corroboration": "<confirmed|partially_confirmed|unconfirmed|contradicted>",
  "corroboration_evidence": [
    {
      "source": "<credible Pakistani source>",
      "relevance": "<why this source is relevant>",
      "supports_signal": true
    }
  ],
  "additional_context": "<3-5 sentences of enriching context about this domain/topic in Pakistan>",
  "contradictions": "<known facts conflicting with signals, or null>",
  "recommended_sources": ["<url1>", "<url2>", "<url3>"]
}
"""


# ──────────────────────────────────────────────────────────────────────────────
# CLASS
# ──────────────────────────────────────────────────────────────────────────────

class ResearchAgent:
    def __init__(self, *args, **kwargs):
        self.session_id = args[0] if args else kwargs.get("session_id", "init")
        self.logger = SessionLogger(session_id=self.session_id)
        self.model = MODELS["research"]
        self.client = GEMINI_API_KEY if (GEMINI_API_KEY and not GEMINI_API_KEY.startswith("AIzaSy_mock")) else None

    def _get_mock_response(self, domain: str) -> dict:
        """Fallback mock response when OpenAI is unavailable"""
        try:
            from agents.mock_responses import get_mock_research
            return get_mock_research(domain)
        except Exception:
            return {
              "agent": "research",
              "domain": domain,
              "timestamp": now_iso(),
              "claims_assessed": [],
              "corroboration": "unconfirmed",
              "corroboration_evidence": [],
              "additional_context": "Fallback research context due to LLM error.",
              "contradictions": None,
              "recommended_sources": []
            }

    @retry(times=2, delay=2.0)
    async def _call_llm(self, parsed_input: dict, domain: str) -> dict:
        if DEMO_MODE or not GEMINI_API_KEY or GEMINI_API_KEY.startswith("AIzaSy_mock"):
            import asyncio
            await asyncio.sleep(1.2)
            return self._get_mock_response(domain)

        clean_text = parsed_input.get("clean_text") or parsed_input.get("raw_text") or json.dumps(parsed_input)
        user_message = (
            f"DOMAIN: {domain}\n\n"
            f"CONTENT TO RESEARCH:\n{clean_text[:3000]}"
        )

        try:
            return await call_gemini(
                system_prompt=RESEARCH_SYSTEM_PROMPT,
                user_message=user_message,
                model=self.model,
                temperature=0.2,
                expect_json=True,
            )
        except Exception as e:
            import logging
            logging.warning(f"Gemini call failed: {e}. Using mock response.")
            return self._get_mock_response(domain)

    async def run(self, parsed_input: dict, domain: str, *args, **kwargs) -> dict:
        session_id = kwargs.get("session_id")
        if not session_id and args:
            for arg in args:
                if isinstance(arg, str):
                    session_id = arg
                    break
        session_id = session_id or getattr(self, "session_id", None) or "session-default"
        logger = SessionLogger(session_id)
        logger.log("research_agent", "start", {"domain": domain})

        start_time = time.time()
        try:
            result = await self._call_llm(parsed_input, domain)
        except Exception as exc:
            logger.log("research_agent", "error", {"error": str(exc)})
            raise

        duration = time.time() - start_time
        logger.log(
            "research_agent",
            "complete",
            {
                "domain": domain,
                "corroboration": result.get("corroboration"),
                "duration_seconds": round(duration, 3),
            },
        )

        result["model_used"] = MODELS["research"]
        result["agent_display_name"] = "Research Agent"

        return result
