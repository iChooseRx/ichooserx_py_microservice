import os
import httpx
from transform.summary_builder import format_export_data
from utils.timestamp import current_timestamp

RAILS_API_BASE = os.getenv("ICHOOSERX_API_BASE_URL")

def fetch_summary_for_drug(drug_name, filters):
    url = f"{RAILS_API_BASE}/drug_searches"
    params = {
        "query": drug_name,
        "filters[]": filters
    }

    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()

def build_json_summary(drug_names, filters):
    all_summaries = []

    for drug in drug_names:
        result = fetch_summary_for_drug(drug, filters)
        all_summaries.append(result)

    # Flatten all summary lists into one
    summary_data = []
    for r in all_summaries:
        summary_list = r.get("summary", [])
        summary_data.extend(summary_list)

    merged = {
        "filters_applied": all_summaries[-1].get("filters_applied", []),  # could use first or last
        "summary": summary_data
    }

    rows = format_export_data(merged)

    return {
        "created_at": current_timestamp(),
        "filters_used": filters,
        "table_data": rows
    }