import uuid
import re
import json
import asyncio
from datetime import datetime, timezone
from functools import wraps
from config import DOMAIN_KEYWORDS, INPUT_EXTENSIONS


def generate_uuid() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def retry(times: int = 2, delay: float = 2.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(times + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < times:
                        await asyncio.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


def detect_domain(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "business"


def detect_input_type(filename: str) -> str:
    if "." not in filename:
        return "text"
    suffix = "." + filename.rsplit(".", 1)[-1].lower()
    return INPUT_EXTENSIONS.get(suffix, "text")


def extract_json_from_text(text: str) -> dict:
    try:
        # Try to find content between ```json and ```
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Fallback to finding the outermost curly braces
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in text")
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse extracted JSON: {str(e)}")


def compute_delta(before: dict, after: dict) -> dict:
    result = {}
    for key in after:
        if key in before:
            from_val = before[key]
            to_val = after[key]
            try:
                if isinstance(from_val, (int, float)) and isinstance(to_val, (int, float)):
                    if from_val == to_val:
                        continue
                    change_pct = round(((to_val - from_val) / from_val) * 100, 2) if from_val != 0 else 0
                    result[key] = {"from": from_val, "to": to_val, "change_pct": change_pct}
            except (TypeError, ZeroDivisionError):
                continue
    return result

