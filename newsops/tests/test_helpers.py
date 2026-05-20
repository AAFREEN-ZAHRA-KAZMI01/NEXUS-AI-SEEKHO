"""Tests for utils/helpers.py — all utility functions."""
import json
import pytest


class TestGenerateUuid:
    def test_returns_string(self):
        from utils.helpers import generate_uuid
        assert isinstance(generate_uuid(), str)

    def test_is_valid_uuid_format(self):
        import re
        from utils.helpers import generate_uuid
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        assert re.match(uuid_pattern, generate_uuid())

    def test_each_call_unique(self):
        from utils.helpers import generate_uuid
        ids = {generate_uuid() for _ in range(20)}
        assert len(ids) == 20


class TestNowIso:
    def test_returns_string(self):
        from utils.helpers import now_iso
        assert isinstance(now_iso(), str)

    def test_ends_with_z(self):
        from utils.helpers import now_iso
        assert now_iso().endswith("Z")

    def test_parseable_as_datetime(self):
        from datetime import datetime
        from utils.helpers import now_iso
        ts = now_iso().replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        assert dt.year >= 2024


class TestDetectDomain:
    def test_logistics_keywords(self):
        from utils.helpers import detect_domain
        assert detect_domain("The shipment arrived at the warehouse via truck") == "logistics"

    def test_business_keywords(self):
        from utils.helpers import detect_domain
        assert detect_domain("Monthly revenue from sales orders declined in Lahore region") == "business"

    def test_finance_keywords(self):
        from utils.helpers import detect_domain
        assert detect_domain("USD/PKR forex rate moved against our portfolio on KSE") == "finance"

    def test_policy_keywords(self):
        from utils.helpers import detect_domain
        assert detect_domain("OGRA issued regulation notification for compliance by ministry") == "policy"

    def test_healthcare_keywords(self):
        from utils.helpers import detect_domain
        assert detect_domain("Hospital drug shortage reported by DRAP for patient formulary") == "healthcare"

    def test_urban_keywords(self):
        from utils.helpers import detect_domain
        assert detect_domain("WASA reported water outage in urban zone; LESCO crew dispatched") == "urban"

    def test_empty_string_returns_business(self):
        from utils.helpers import detect_domain
        assert detect_domain("") == "business"

    def test_unrelated_text_returns_business(self):
        from utils.helpers import detect_domain
        assert detect_domain("The cat sat on the mat today in the garden") == "business"


class TestDetectInputType:
    def test_pdf_extension(self):
        from utils.helpers import detect_input_type
        assert detect_input_type("report.pdf") == "pdf"

    def test_docx_extension(self):
        from utils.helpers import detect_input_type
        assert detect_input_type("document.docx") == "docx"

    def test_doc_extension(self):
        from utils.helpers import detect_input_type
        assert detect_input_type("old.doc") == "docx"

    def test_csv_extension(self):
        from utils.helpers import detect_input_type
        assert detect_input_type("data.csv") == "csv"

    def test_xlsx_extension(self):
        from utils.helpers import detect_input_type
        assert detect_input_type("workbook.xlsx") == "excel"

    def test_xls_extension(self):
        from utils.helpers import detect_input_type
        assert detect_input_type("old.xls") == "excel"

    def test_no_extension_returns_text(self):
        from utils.helpers import detect_input_type
        assert detect_input_type("myfile") == "text"

    def test_unknown_extension_returns_text(self):
        from utils.helpers import detect_input_type
        assert detect_input_type("archive.zip") == "text"

    def test_uppercase_extension(self):
        from utils.helpers import detect_input_type
        assert detect_input_type("REPORT.PDF") == "pdf"


class TestExtractJsonFromText:
    def test_plain_json(self):
        from utils.helpers import extract_json_from_text
        data = extract_json_from_text('{"key": "value", "num": 42}')
        assert data == {"key": "value", "num": 42}

    def test_json_in_markdown_fence(self):
        from utils.helpers import extract_json_from_text
        text = '```json\n{"agent": "ingestion", "domain": "logistics"}\n```'
        data = extract_json_from_text(text)
        assert data["agent"] == "ingestion"
        assert data["domain"] == "logistics"

    def test_json_embedded_in_prose(self):
        from utils.helpers import extract_json_from_text
        text = 'Here is the result: {"status": "ok", "count": 3} and nothing else.'
        data = extract_json_from_text(text)
        assert data["status"] == "ok"

    def test_nested_json(self):
        from utils.helpers import extract_json_from_text
        text = '{"facts": [{"text": "fuel up 18%", "value": 18}], "confidence": "high"}'
        data = extract_json_from_text(text)
        assert len(data["facts"]) == 1
        assert data["confidence"] == "high"

    def test_raises_on_no_json(self):
        from utils.helpers import extract_json_from_text
        with pytest.raises(ValueError):
            extract_json_from_text("No JSON here at all.")

    def test_raises_on_malformed_json(self):
        from utils.helpers import extract_json_from_text
        with pytest.raises(ValueError):
            extract_json_from_text("{bad json: missing quotes}")


class TestComputeDelta:
    def test_increase_detected(self):
        from utils.helpers import compute_delta
        before = {"price": 100.0}
        after = {"price": 118.0}
        delta = compute_delta(before, after)
        assert "price" in delta
        assert delta["price"]["from"] == 100.0
        assert delta["price"]["to"] == 118.0
        assert delta["price"]["change_pct"] == pytest.approx(18.0)

    def test_decrease_detected(self):
        from utils.helpers import compute_delta
        before = {"volume": 1240}
        after = {"volume": 890}
        delta = compute_delta(before, after)
        assert "volume" in delta
        assert delta["volume"]["change_pct"] < 0

    def test_unchanged_fields_not_in_delta(self):
        from utils.helpers import compute_delta
        before = {"count": 100, "price": 50.0}
        after = {"count": 100, "price": 60.0}
        delta = compute_delta(before, after)
        assert "count" not in delta
        assert "price" in delta

    def test_new_key_not_in_before_excluded(self):
        from utils.helpers import compute_delta
        before = {"price": 100.0}
        after = {"price": 110.0, "new_field": 999}
        delta = compute_delta(before, after)
        assert "new_field" not in delta

    def test_string_values_ignored(self):
        from utils.helpers import compute_delta
        before = {"name": "alpha", "count": 10}
        after = {"name": "beta", "count": 20}
        delta = compute_delta(before, after)
        assert "name" not in delta
        assert "count" in delta

    def test_empty_dicts_return_empty(self):
        from utils.helpers import compute_delta
        assert compute_delta({}, {}) == {}

    def test_zero_from_value_no_crash(self):
        from utils.helpers import compute_delta
        before = {"rate": 0}
        after = {"rate": 5}
        delta = compute_delta(before, after)
        assert "rate" in delta
        assert delta["rate"]["change_pct"] == 0

    def test_multiple_changed_fields(self):
        from utils.helpers import compute_delta
        before = {"a": 100, "b": 200, "c": 300}
        after = {"a": 110, "b": 200, "c": 270}
        delta = compute_delta(before, after)
        assert "a" in delta
        assert "b" not in delta
        assert "c" in delta
        assert delta["c"]["change_pct"] == pytest.approx(-10.0)
