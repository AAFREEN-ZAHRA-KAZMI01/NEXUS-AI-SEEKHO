import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, MODELS

_client = genai.Client(api_key=GEMINI_API_KEY) if (GEMINI_API_KEY and GEMINI_API_KEY.strip()) else None


async def call_gemini(
    system_prompt: str,
    user_message: str,
    model: str = None,
    temperature: float = 0.2,
    expect_json: bool = True,
) -> dict | str:
    if model is None:
        model = MODELS.get("ingestion", "gemini-2.5-flash")
    if not _client:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    full_prompt = f"{system_prompt}\n\n---\n\n{user_message}"
    if expect_json:
        full_prompt += "\n\nRespond with ONLY valid JSON. No markdown fences. No explanation. Raw JSON only."

    config = types.GenerateContentConfig(
        temperature=temperature,
        response_mime_type="application/json" if expect_json else "text/plain",
    )

    response = await _client.aio.models.generate_content(
        model=model,
        contents=full_prompt,
        config=config,
    )
    raw_text = response.text.strip()

    if not expect_json:
        return raw_text

    # Strip markdown fences if present
    if raw_text.startswith("```"):
        for part in raw_text.split("```"):
            part = part.strip()
            if part.startswith("json"):
                raw_text = part[4:].strip()
                break
            if part.startswith("{") or part.startswith("["):
                raw_text = part
                break

    raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        from utils.helpers import extract_json_from_text
        return extract_json_from_text(raw_text)
