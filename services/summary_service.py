import os
import httpx
from dotenv import load_dotenv
from transform.summary_builder import format_export_data
from utils.timestamp import current_timestamp

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
    """Builds and formats summary data from export_summaries API."""
    result = fetch_summary_for_drugs(drug_names, filters)

    rows = format_export_data(result)

    return {
        "created_at": current_timestamp(),
        "filters_used": filters,
        "table_data": rows
    }