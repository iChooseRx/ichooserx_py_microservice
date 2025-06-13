import os
import httpx
from dotenv import load_dotenv
from serializers.drug_summary_factory import from_api as build_drug_summary
from transform.summary_builder import format_export_data
from utils.alignment_score import calculate_alignment_score
from utils.timestamp import current_timestamp
from utils.manufacturer_utils import count_manufacturers

load_dotenv()

RAILS_API_BASE = os.getenv("ICHOOSERX_API_BASE_URL")

def fetch_summary_for_drugs(drug_names, filters):
    """Send one GET request for all drugs with optional filters."""
    url = f"{RAILS_API_BASE}/export_summaries"
    params = {
      "drug_names[]": drug_names,
      "filters[]": filters
    }

    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()

def build_json_summary(drug_names, filters):
    result = fetch_summary_for_drugs(drug_names, filters)

    summaries = []
    json_data = []

    for item in result.get("summary", []):
        drug_summary = build_drug_summary(item)

        summaries.append(drug_summary)
        json_data.append({
            "drug_name": drug_summary.drug_name,
            "total_results": drug_summary.total_count,
            "filtered_results": drug_summary.filtered_count,
            "alignment_score": calculate_alignment_score(
                drug_summary.filtered_count,
                drug_summary.total_count
            ),
            "top_manufacturers": count_manufacturers(drug_summary.variants)
        })

    return {
        "created_at": current_timestamp(),
        "filters_used": filters,
        "json_data": json_data,
        "table_data": format_export_data({
            "filters_applied": result.get("filters_applied", []),
            "summary": result.get("summary", [])
        })
    }