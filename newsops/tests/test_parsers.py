"""Tests for all parsers — text, CSV, Excel, PDF, DOCX (all parsers are async)."""
import pytest


class TestTextParser:
    async def test_parse_text_returns_dict(self, sample_text):
        from parsers.text_parser import parse_text
        result = await parse_text(sample_text)
        assert isinstance(result, dict)

    async def test_parse_text_has_clean_text(self, sample_text):
        from parsers.text_parser import parse_text
        result = await parse_text(sample_text)
        assert "clean_text" in result
        assert len(result["clean_text"]) > 0

    async def test_parse_text_has_word_count(self, sample_text):
        from parsers.text_parser import parse_text
        result = await parse_text(sample_text)
        assert "word_count" in result
        assert result["word_count"] > 0

    async def test_parse_text_preserves_content(self, sample_text):
        from parsers.text_parser import parse_text
        result = await parse_text(sample_text)
        text_lower = result["clean_text"].lower()
        assert "ogra" in text_lower or "fuel" in text_lower

    async def test_parse_text_word_count_matches_content(self, sample_text):
        from parsers.text_parser import parse_text
        result = await parse_text(sample_text)
        assert result["word_count"] == len(sample_text.split())

    async def test_parse_url_bad_url_returns_error_dict(self):
        from parsers.text_parser import parse_url
        result = await parse_url("not-a-real-url")
        assert isinstance(result, dict)
        assert "error" in result or "clean_text" in result

    async def test_parse_text_empty_string(self):
        from parsers.text_parser import parse_text
        result = await parse_text("")
        assert isinstance(result, dict)
        assert "clean_text" in result

    @pytest.mark.integration
    async def test_parse_url_real_page(self):
        from parsers.text_parser import parse_url
        result = await parse_url("https://httpbin.org/html")
        assert isinstance(result, dict)
        if "error" not in result:
            assert result.get("word_count", 0) > 0


class TestCSVParser:
    async def test_parse_csv_returns_dict(self, sample_csv_bytes):
        from parsers.csv_parser import parse_csv
        result = await parse_csv(sample_csv_bytes)
        assert isinstance(result, dict)

    async def test_parse_csv_has_clean_text(self, sample_csv_bytes):
        from parsers.csv_parser import parse_csv
        result = await parse_csv(sample_csv_bytes)
        assert "clean_text" in result
        assert len(result["clean_text"]) > 0

    async def test_parse_csv_detects_columns(self, sample_csv_bytes):
        from parsers.csv_parser import parse_csv
        result = await parse_csv(sample_csv_bytes)
        assert "columns" in result
        expected_cols = {"month", "region", "order_volume", "revenue_pkr"}
        assert expected_cols.issubset(set(result["columns"]))

    async def test_parse_csv_row_count(self, sample_csv_bytes):
        from parsers.csv_parser import parse_csv
        result = await parse_csv(sample_csv_bytes)
        assert result.get("total_rows") == 12

    async def test_parse_csv_source_type(self, sample_csv_bytes):
        from parsers.csv_parser import parse_csv
        result = await parse_csv(sample_csv_bytes)
        assert result.get("source_type") == "csv"

    async def test_parse_csv_summary_stats(self, sample_csv_bytes):
        from parsers.csv_parser import parse_csv
        result = await parse_csv(sample_csv_bytes)
        assert "numeric_summary" in result
        assert isinstance(result["numeric_summary"], dict)

    async def test_parse_csv_inline_bytes(self):
        from parsers.csv_parser import parse_csv
        csv_data = b"name,value\nalpha,100\nbeta,200\n"
        result = await parse_csv(csv_data)
        assert isinstance(result, dict)
        assert result.get("total_rows") == 2

    async def test_parse_csv_handles_empty_data(self):
        from parsers.csv_parser import parse_csv
        result = await parse_csv(b"col1,col2\n")
        assert isinstance(result, dict)


class TestExcelParser:
    async def test_parse_excel_returns_dict(self, sample_excel_bytes):
        from parsers.excel_parser import parse_excel
        result = await parse_excel(sample_excel_bytes)
        assert isinstance(result, dict)

    async def test_parse_excel_has_clean_text(self, sample_excel_bytes):
        from parsers.excel_parser import parse_excel
        result = await parse_excel(sample_excel_bytes)
        assert "clean_text" in result
        assert len(result["clean_text"]) > 0

    async def test_parse_excel_sheet_names(self, sample_excel_bytes):
        from parsers.excel_parser import parse_excel
        result = await parse_excel(sample_excel_bytes)
        assert "sheet_names" in result
        assert "Sales Data" in result["sheet_names"]

    async def test_parse_excel_sheet_count(self, sample_excel_bytes):
        from parsers.excel_parser import parse_excel
        result = await parse_excel(sample_excel_bytes)
        assert len(result.get("sheet_names", [])) >= 1

    async def test_parse_excel_source_type(self, sample_excel_bytes):
        from parsers.excel_parser import parse_excel
        result = await parse_excel(sample_excel_bytes)
        assert result.get("source_type") == "excel"

    async def test_parse_excel_sheets_dict(self, sample_excel_bytes):
        from parsers.excel_parser import parse_excel
        result = await parse_excel(sample_excel_bytes)
        assert "sheets" in result
        assert isinstance(result["sheets"], dict)


class TestPDFParser:
    async def test_parse_pdf_returns_dict(self, sample_pdf_bytes):
        from parsers.pdf_parser import parse_pdf
        result = await parse_pdf(sample_pdf_bytes, domain="logistics", use_vision=False)
        assert isinstance(result, dict)

    async def test_parse_pdf_has_clean_text(self, sample_pdf_bytes):
        from parsers.pdf_parser import parse_pdf
        result = await parse_pdf(sample_pdf_bytes, domain="logistics", use_vision=False)
        assert "clean_text" in result
        assert len(result["clean_text"]) > 0

    async def test_parse_pdf_source_type(self, sample_pdf_bytes):
        from parsers.pdf_parser import parse_pdf
        result = await parse_pdf(sample_pdf_bytes, domain="logistics", use_vision=False)
        assert result.get("source_type") in ("pdf", "pdf_agentic")

    async def test_parse_pdf_page_count(self, sample_pdf_bytes):
        from parsers.pdf_parser import parse_pdf
        result = await parse_pdf(sample_pdf_bytes, domain="logistics", use_vision=False)
        assert result.get("pages_count", 0) >= 1

    async def test_parse_pdf_word_count(self, sample_pdf_bytes):
        from parsers.pdf_parser import parse_pdf
        result = await parse_pdf(sample_pdf_bytes, domain="logistics", use_vision=False)
        assert result.get("word_count", 0) > 0

    async def test_parse_pdf_content_contains_expected_text(self, sample_pdf_bytes):
        from parsers.pdf_parser import parse_pdf
        result = await parse_pdf(sample_pdf_bytes, domain="logistics", use_vision=False)
        text = result["clean_text"].lower()
        assert any(kw in text for kw in ["lahore", "fuel", "delivery", "q3"])


class TestDocxParser:
    async def test_parse_docx_returns_dict(self, sample_docx_bytes):
        from parsers.docx_parser import parse_docx
        result = await parse_docx(sample_docx_bytes, domain="policy", use_vision=False)
        assert isinstance(result, dict)

    async def test_parse_docx_has_clean_text(self, sample_docx_bytes):
        from parsers.docx_parser import parse_docx
        result = await parse_docx(sample_docx_bytes, domain="policy", use_vision=False)
        assert "clean_text" in result
        assert len(result["clean_text"]) > 0

    async def test_parse_docx_source_type(self, sample_docx_bytes):
        from parsers.docx_parser import parse_docx
        result = await parse_docx(sample_docx_bytes, domain="policy", use_vision=False)
        assert result.get("source_type") in ("docx", "docx_agentic")

    async def test_parse_docx_content_contains_expected_text(self, sample_docx_bytes):
        from parsers.docx_parser import parse_docx
        result = await parse_docx(sample_docx_bytes, domain="policy", use_vision=False)
        text = result["clean_text"].lower()
        assert any(kw in text for kw in ["ogra", "fuel", "policy", "notification"])
