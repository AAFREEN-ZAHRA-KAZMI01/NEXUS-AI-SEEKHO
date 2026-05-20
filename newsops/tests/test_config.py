"""Tests for config.py — constants, model map, domain list, severity labels."""
import pytest


class TestModels:
    def test_models_dict_has_all_agents(self):
        from config import MODELS
        expected = {"orchestrator", "ingestion", "analysis", "decision", "research", "execution", "input_parser"}
        assert set(MODELS.keys()) == expected

    def test_all_models_are_valid_gemini_models(self):
        from config import MODELS
        valid_prefixes = ("gemini-",)
        for agent, model in MODELS.items():
            assert any(model.startswith(p) for p in valid_prefixes), (
                f"MODELS['{agent}'] = '{model}' does not look like a valid Gemini model"
            )


class TestDomains:
    def test_domains_list_has_six_domains(self):
        from config import DOMAINS
        assert len(DOMAINS) == 6

    def test_domains_exact_set(self):
        from config import DOMAINS
        expected = {"logistics", "business", "finance", "policy", "healthcare", "urban"}
        assert set(DOMAINS) == expected

    def test_domain_keywords_covers_all_domains(self):
        from config import DOMAIN_KEYWORDS, DOMAINS
        for domain in DOMAINS:
            assert domain in DOMAIN_KEYWORDS, f"DOMAIN_KEYWORDS missing domain '{domain}'"
            assert len(DOMAIN_KEYWORDS[domain]) >= 5, (
                f"DOMAIN_KEYWORDS['{domain}'] has fewer than 5 keywords"
            )

    def test_domain_keywords_are_lowercase(self):
        from config import DOMAIN_KEYWORDS
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for kw in keywords:
                assert kw == kw.lower(), f"Keyword '{kw}' in domain '{domain}' is not lowercase"


class TestInputExtensions:
    def test_pdf_maps_to_pdf(self):
        from config import INPUT_EXTENSIONS
        assert INPUT_EXTENSIONS[".pdf"] == "pdf"

    def test_docx_maps_to_docx(self):
        from config import INPUT_EXTENSIONS
        assert INPUT_EXTENSIONS[".docx"] == "docx"

    def test_csv_maps_to_csv(self):
        from config import INPUT_EXTENSIONS
        assert INPUT_EXTENSIONS[".csv"] == "csv"

    def test_xlsx_maps_to_excel(self):
        from config import INPUT_EXTENSIONS
        assert INPUT_EXTENSIONS[".xlsx"] == "excel"

    def test_xls_maps_to_excel(self):
        from config import INPUT_EXTENSIONS
        assert INPUT_EXTENSIONS[".xls"] == "excel"

    def test_doc_maps_to_docx(self):
        from config import INPUT_EXTENSIONS
        assert INPUT_EXTENSIONS[".doc"] == "docx"


class TestSeverityLabel:
    def test_score_1_is_low(self):
        from config import get_severity_label
        assert get_severity_label(1) == "Low"

    def test_score_2_is_low(self):
        from config import get_severity_label
        assert get_severity_label(2) == "Low"

    def test_score_5_is_medium(self):
        from config import get_severity_label
        assert get_severity_label(5) == "Medium"

    def test_score_6_is_medium(self):
        from config import get_severity_label
        assert get_severity_label(6) == "Medium"

    def test_score_7_is_high(self):
        from config import get_severity_label
        assert get_severity_label(7) == "High"

    def test_score_8_is_high(self):
        from config import get_severity_label
        assert get_severity_label(8) == "High"

    def test_score_10_is_critical(self):
        from config import get_severity_label
        assert get_severity_label(10) == "Critical"

    def test_score_9_is_critical(self):
        from config import get_severity_label
        assert get_severity_label(9) == "Critical"

    def test_score_3_is_low_medium(self):
        from config import get_severity_label
        assert get_severity_label(3) == "Low-Medium"

    def test_out_of_range_returns_unknown(self):
        from config import get_severity_label
        assert get_severity_label(0) == "Unknown"
        assert get_severity_label(11) == "Unknown"


class TestGeminiKey:
    def test_gemini_api_key_exists(self):
        from config import GEMINI_API_KEY
        assert GEMINI_API_KEY is not None
        assert len(GEMINI_API_KEY) > 0
