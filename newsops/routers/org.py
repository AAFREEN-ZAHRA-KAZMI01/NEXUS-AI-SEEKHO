import secrets
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from database.db import get_db
from database.models import Organisation
from utils.auth_middleware import require_org

router = APIRouter()

class RegisterRequest(BaseModel):
    name: str

@router.post("/register")
async def register_org(req: RegisterRequest):
    api_key = secrets.token_urlsafe(32)
    async with get_db() as db:
        new_org = Organisation(
            name=req.name,
            api_key=api_key
        )
        db.add(new_org)
        await db.commit()
        await db.refresh(new_org)
        return {
            "org_id": new_org.id,
            "api_key": new_org.api_key,
            "name": new_org.name,
            "plan": new_org.plan,
            "monthly_limit": new_org.monthly_limit
        }

@router.get("/me")
async def get_org_me(org: Organisation = Depends(require_org)):
    return {
        "org_id": org.id,
        "name": org.name,
        "plan": org.plan,
        "monthly_analysis_count": org.monthly_analysis_count,
        "monthly_limit": org.monthly_limit,
        "remaining_analyses": max(0, org.monthly_limit - org.monthly_analysis_count)
    }

@router.get("/usage")
async def get_org_usage(org: Organisation = Depends(require_org)):
    return {
        "daily_counts": [], 
        "total_this_month": org.monthly_analysis_count,
        "top_domains": []
    }
