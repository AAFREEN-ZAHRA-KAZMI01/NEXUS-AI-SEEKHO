from fastapi import APIRouter
from utils.validated_gemini import validation_stats
from config import DEBUG

router = APIRouter()

@router.get("/validation-stats")
async def get_validation_stats():
    if not DEBUG:
        return {"error": "Debug mode is not enabled"}
    return validation_stats
