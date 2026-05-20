import io
import json

import pandas as pd
from config import MODELS
from utils.gemini_client import call_gemini

CSV_SEMANTIC_PROMPT = """
# ROLE
You are a Data Schema Analyst. You receive a CSV summary with column names
and statistical descriptions. Your job is to identify the semantic meaning
of each column and find the most analytically important patterns.

# CHAIN-OF-THOUGHT ANALYSIS
<thinking>
Step 1 — COLUMN SEMANTICS: For each column name, infer:
  - What does this column represent in business terms?
  - Is it a dimension (category) or measure (number)?
  - If measure: is it currency, percentage, count, ratio, or index?
Step 2 — KEY METRIC COLUMNS: Which columns are the most analytically important?
  (usually: revenue, cost, volume, rate, percentage change columns)
Step 3 — TREND IDENTIFICATION: Given the trend data (upward/downward/stable),
  which trends are most significant for business decision-making?
Step 4 — ANOMALY SIGNIFICANCE: Are the detected anomaly rows genuinely anomalous
  (errors, outliers) or are they legitimate extreme values?
Step 5 — BUSINESS NARRATIVE: What story does this data tell in 2-3 sentences?
</thinking>

# OUTPUT FORMAT — Raw JSON only
{
  "column_semantics": [
    {
      "column": "<column_name>",
      "business_meaning": "<what this column represents>",
      "type": "<dimension|measure>",
      "measure_type": "<currency|percentage|count|ratio|index|null>",
      "currency": "<PKR|USD|null>",
      "importance": "<high|medium|low>"
    }
  ],
  "key_metric_columns": ["<col1>", "<col2>"],
  "significant_trends": [
    {
      "column": "<col_name>",
      "trend": "<upward|downward|stable>",
      "business_implication": "<what this trend means>"
    }
  ],
  "anomaly_assessment": "<are anomaly rows errors or legitimate extremes>",
  "business_narrative": "<2-3 sentence story this data tells>",
  "recommended_action_focus": "<which metric should drive the recommended action>"
}
"""


async def parse_csv(file_bytes: bytes) -> dict:
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))

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

        summary = (
            f"This CSV contains {len(df)} rows and {len(df.columns)} columns. "
            f"Columns: {list(df.columns)}. "
            f"Numeric summary available for: {list(numeric_df.columns)}. "
            f"Trends detected: {trends_dict}. "
            f"Anomalous rows found: {len(anomaly_rows)}."
        )

        # Semantic column analysis via LLM
        semantic_analysis = {}
        try:
            user_msg = (
                f"CSV SCHEMA:\nColumns: {list(df.columns)}\n\n"
                f"Statistics:\n{json.dumps(describe_dict)[:2000]}\n\n"
                f"Trends:\n{json.dumps(trends_dict)}\n\n"
                f"Anomalies found: {len(anomaly_rows)}"
            )
            semantic_analysis = await call_gemini(
                system_prompt=CSV_SEMANTIC_PROMPT,
                user_message=user_msg,
                model=MODELS.get("input_parser", "gemini-1.5-flash"),
                temperature=0.2,
                expect_json=True,
            )
        except Exception:
            pass

        narrative = semantic_analysis.get("business_narrative", "")
        clean_text = f"{narrative}\n\n{summary}" if narrative else summary

        return {
            "clean_text": clean_text,
            "parsed_rows": df.head(100).to_dict(orient="records"),
            "numeric_summary": describe_dict,
            "anomaly_rows": anomaly_rows,
            "column_trends": trends_dict,
            "total_rows": len(df),
            "columns": list(df.columns),
            "source_type": "csv",
            "semantic_analysis": semantic_analysis,
        }
    except Exception as e:
        return {"error": True, "reason": str(e), "clean_text": ""}
