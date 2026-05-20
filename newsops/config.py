import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./newsops.db")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", 8000))

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

MODELS = {
    "orchestrator":  "gemini-1.5-flash",
    "ingestion":     "gemini-1.5-flash",
    "analysis":      "gemini-1.5-flash",
    "decision":      "gemini-1.5-flash",
    "research":      "gemini-1.5-flash",
    "execution":     "gemini-1.5-flash",
    "input_parser":  "gemini-1.5-flash",
}


DOMAINS = ["logistics", "business", "finance", "policy", "healthcare", "urban"]

DOMAIN_KEYWORDS = {
    "logistics":  ["shipment","freight","logistics","warehouse","route","delivery","fuel","carrier","dispatch","truck","fleet","last-mile"],
    "business":   ["sales","revenue","crm","campaign","customer","region","order","product","sku","discount","churn","retention"],
    "finance":    ["stock","forex","pkr","usd","rate","investment","profit","loss","interest","kse","sbp","secp","portfolio","hedge","exchange"],
    "policy":     ["policy","government","law","ogra","sbp","regulation","ministry","notification","gazette","compliance","tax","duty"],
    "healthcare": ["hospital","patient","drug","medicine","healthcare","pharma","who","drap","formulary","clinical","shortage","procurement","treatment"],
    "urban":      ["traffic","water","electricity","urban","smart city","infrastructure","wasa","lesco","cda","zone","fault","outage","maintenance"],
}

INPUT_EXTENSIONS = {
    ".pdf":  "pdf",
    ".docx": "docx",
    ".doc":  "docx",
    ".csv":  "csv",
    ".xlsx": "excel",
    ".xls":  "excel",
}

SEVERITY_LABELS = {
    (1,2):  "Low",
    (3,4):  "Low-Medium",
    (5,6):  "Medium",
    (7,8):  "High",
    (9,10): "Critical",
}

def get_severity_label(score: int) -> str:
    for (low, high), label in SEVERITY_LABELS.items():
        if low <= score <= high:
            return label
    return "Unknown"
