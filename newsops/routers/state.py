from fastapi import APIRouter, HTTPException

from config import DOMAINS
from mock_api.state_store import get_state, reset_state
from utils.helpers import now_iso

router = APIRouter(prefix="/api", tags=["State"])


@router.get("/state/{domain}")
async def get_domain_state(domain: str):
    if domain not in DOMAINS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown domain '{domain}'. Valid domains: {DOMAINS}",
        )
    return get_state(domain)


@router.post("/state/reset")
async def reset_all_state():
    reset_state()
    return {
        "status": "reset",
        "message": "All domain states restored to defaults",
        "timestamp": now_iso(),
    }
