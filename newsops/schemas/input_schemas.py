from pydantic import BaseModel, Field
from typing import Optional


class TextAnalysisRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Raw text to analyse")
    domain: Optional[str] = Field(None, description="Optional domain override")
    session_id: Optional[str] = Field(None, description="Optional frontend-generated session ID")


class UrlAnalysisRequest(BaseModel):
    url: str = Field(..., description="URL to fetch and analyse")
    domain: Optional[str] = None
    session_id: Optional[str] = Field(None, description="Optional frontend-generated session ID")


class FileAnalysisRequest(BaseModel):
    input_type: str = Field(..., description="pdf | docx | csv | excel")
    domain: Optional[str] = None
    session_id: Optional[str] = Field(None, description="Optional frontend-generated session ID")
