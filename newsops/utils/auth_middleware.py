from fastapi import Request, HTTPException
from sqlalchemy import select
from database.db import get_db
from database.models import Organisation

async def get_org_from_request(request: Request) -> Organisation | None:
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None
        
    async with get_db() as db:
        stmt = select(Organisation).where(Organisation.api_key == api_key, Organisation.is_active == True)
        result = await db.execute(stmt)
        org = result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(status_code=401, detail="Invalid API key")
            
        return org

async def require_org(request: Request) -> Organisation:
    org = await get_org_from_request(request)
    if not org:
        raise HTTPException(status_code=401, detail="API key required")
    return org

def check_usage_limit(org: Organisation):
    if org.monthly_analysis_count >= org.monthly_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly analysis limit reached. Current plan: {org.plan}. Limit: {org.monthly_limit}"
        )
