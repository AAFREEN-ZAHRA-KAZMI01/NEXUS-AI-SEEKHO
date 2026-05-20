import io
import json

import pandas as pd
from config import MODELS
from utils.gemini_client import call_gemini

EXCEL_RELATIONSHIP_PROMPT = """
# ROLE
You are an Excel Workbook Analyst. You receive summaries of multiple sheets
from an Excel workbook. Identify how the sheets relate to each other and
which contains the most decision-relevant data.

# ANALYSIS TASKS
1. SHEET ROLES: For each sheet, infer its role:
   "summary", "raw_data", "pivot", "lookup_table", "dashboard", "template", "other"
2. RELATIONSHIPS: Do sheets reference each other? (e.g., summary sheet totals raw_data sheet)
3. PRIMARY ANALYSIS SHEET: Which sheet should the Ingestion Agent focus on?
4. CROSS-SHEET INSIGHT: Is there something you can only see by looking across sheets?
   (e.g., summary shows decline, raw_data shows it's concentrated in one region)

# OUTPUT — Raw JSON only
{
  "sheet_roles": {"<sheet_name>": "<role>"},
  "primary_analysis_sheet": "<sheet_name>",
  "relationships": ["<sheet A totals come from sheet B raw data>"],
  "cross_sheet_insight": "<insight only visible across sheets, or null>",
  "recommended_focus": "<which sheet and columns to focus analysis on>"
}
"""


async def _analyze_df(df: pd.DataFrame) -> dict:
    numeric_df = df.select_dtypes(include=["number"])
    describe_dict = numeric_df.describe().to_dict()

    anomaly_rows = []
    for col in numeric_df.columns:
        mean = numeric_df[col].mean()
        std = numeric_df[col].std()
        anomalies = df[df[col] > (mean + 2 * std)]
        if not anomalies.empty:
            anomaly_rows.extend(anomalies.to_dict(orient="records"))

    trends_dict = {}
    for col in numeric_df.columns:
        if len(numeric_df) > 1:
            diff_mean = numeric_df[col].diff().mean()
            if diff_mean > 0.05:
                trends_dict[col] = "upward"
            elif diff_mean < -0.05:
                trends_dict[col] = "downward"
            else:
                trends_dict[col] = "stable"
        else:
            trends_dict[col] = "insufficient_data"

    return {
        "numeric_summary": describe_dict,
        "anomaly_rows": anomaly_rows,
        "column_trends": trends_dict,
        "total_rows": len(df),
        "columns": list(df.columns),
    }


async def parse_excel(file_bytes: bytes) -> dict:
    try:
        sheets = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None, engine="openpyxl")

        sheet_results = {}
        primary_sheet_name = ""
        max_rows = -1

        for name, df in sheets.items():
            analysis = await _analyze_df(df)
            sheet_results[name] = analysis
            if len(df) > max_rows:
                max_rows = len(df)
                primary_sheet_name = name

        combined_summary = f"Excel file with {len(sheets)} sheets: {list(sheets.keys())}. "
        combined_summary += f"Primary sheet: {primary_sheet_name} with {max_rows} rows. "
        for name, res in sheet_results.items():
            combined_summary += f"Sheet '{name}' trends: {res['column_trends']}. "

        # Cross-sheet relationship analysis
        workbook_analysis = {}
        try:
            sheet_summaries = {
                name: {
                    "columns": res["columns"],
                    "total_rows": res["total_rows"],
                    "trends": res["column_trends"],
                }
                for name, res in sheet_results.items()
            }
            user_msg = f"Workbook sheet summaries:\n{json.dumps(sheet_summaries, indent=2)[:3000]}"
            workbook_analysis = await call_gemini(
                system_prompt=EXCEL_RELATIONSHIP_PROMPT,
                user_message=user_msg,
                model=MODELS.get("input_parser", "gemini-1.5-flash"),
                temperature=0.2,
                expect_json=True,
            )
            primary_sheet_name = workbook_analysis.get("primary_analysis_sheet", primary_sheet_name)
        except Exception:
            pass

        cross_insight = workbook_analysis.get("cross_sheet_insight", "")
        clean_text = f"{cross_insight}\n\n{combined_summary}" if cross_insight else combined_summary

        return {
            "clean_text": clean_text[:8000],
            "sheets": sheet_results,
            "primary_sheet": primary_sheet_name,
            "sheet_names": list(sheets.keys()),
            "source_type": "excel",
            "workbook_analysis": workbook_analysis,
        }
    except Exception as e:
        return {"error": True, "reason": str(e), "clean_text": ""}
