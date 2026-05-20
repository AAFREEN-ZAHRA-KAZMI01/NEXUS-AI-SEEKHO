"""Verify every import in the project resolves. A failed import here breaks everything."""
import pytest


class TestCoreImports:
    def test_fastapi_imports(self):
        from fastapi import FastAPI, APIRouter, HTTPException, UploadFile
        from fastapi.middleware.cors import CORSMiddleware
        assert FastAPI is not None

    def test_pydantic_imports(self):
        from pydantic import BaseModel, Field
        assert BaseModel is not None

    def test_gemini_imports(self):
        from google import genai
        from google.genai import types
        assert genai is not None
        assert types is not None

    def test_sqlalchemy_imports(self):
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import DeclarativeBase
        assert create_async_engine is not None

    def test_pdf_parser_imports(self):
        import pdfplumber
        import fitz
        assert pdfplumber is not None
        assert fitz is not None

    def test_docx_parser_imports(self):
        from docx import Document
        assert Document is not None

    def test_csv_excel_imports(self):
        import pandas as pd
        import openpyxl
        assert pd is not None
        assert openpyxl is not None

    def test_web_parser_imports(self):
        import httpx
        from bs4 import BeautifulSoup
        assert httpx is not None
        assert BeautifulSoup is not None

    def test_ocr_imports(self):
        try:
            import pytesseract
            from pdf2image import convert_from_bytes
            assert pytesseract is not None
        except ImportError:
            pytest.skip("pytesseract / pdf2image not installed in local env (Docker-only)")


class TestProjectImports:
    def test_config_import(self):
        from config import GEMINI_API_KEY, MODELS, DOMAINS, DOMAIN_KEYWORDS, get_severity_label
        assert MODELS is not None
        assert len(DOMAINS) == 6

    def test_helpers_import(self):
        from utils.helpers import (
            generate_uuid, now_iso, detect_domain,
            detect_input_type, extract_json_from_text, compute_delta,
        )
        assert generate_uuid is not None

    def test_logger_import(self):
        from utils.logger import SessionLogger
        assert SessionLogger is not None

    def test_database_import(self):
        from database.db import create_tables, get_db
        from database.models import (
            AnalysisSession, AgentArtifact, StateLog,
            save_session, save_artifact, update_session_status, get_session_artifacts,
        )
        assert AnalysisSession is not None

    def test_parsers_import(self):
        from parsers.text_parser import parse_text, parse_url
        from parsers.pdf_parser import parse_pdf
        from parsers.docx_parser import parse_docx
        from parsers.csv_parser import parse_csv
        from parsers.excel_parser import parse_excel
        assert parse_text is not None

    def test_agents_import(self):
        from agents.ingestion_agent import IngestionAgent
        from agents.analysis_agent import AnalysisAgent
        from agents.decision_agent import DecisionAgent
        from agents.research_agent import ResearchAgent
        from agents.execution_agent import ExecutionAgent
        from agents.orchestrator import Orchestrator
        assert Orchestrator is not None

    def test_mock_api_import(self):
        from mock_api.state_store import get_state, update_state, reset_state, DEFAULT_STATE
        from mock_api.endpoints import router
        assert get_state is not None
        assert router is not None

    def test_pipeline_import(self):
        from pipelines.pipeline import run_pipeline
        assert run_pipeline is not None

    def test_routers_import(self):
        from routers.analysis import router as analysis_router
        from routers.session import router as session_router
        from routers.state import router as state_router
        assert analysis_router is not None

    def test_schemas_import(self):
        from schemas.input_schemas import TextAnalysisRequest, UrlAnalysisRequest, FileAnalysisRequest
        from schemas.output_schemas import AnalysisResponse
        assert AnalysisResponse is not None

    def test_document_intelligence_import(self):
        from parsers.document_intelligence import (
            detect_layout_regions,
            sort_by_reading_order,
            extract_region_content,
            extract_table_with_vision,
            extract_chart_meaning,
            extract_form_fields,
            extract_key_value_pairs,
            extract_document_intelligently,
        )
        assert extract_document_intelligently is not None

    def test_ocr_utils_import(self):
        from parsers.ocr_utils import (
            pdf_to_images, image_to_base64, run_tesseract_ocr, is_scanned_page,
        )
        assert is_scanned_page is not None
