import pandas as pd
from utils.alignment_score import calculate_alignment_score
from utils.manufacturer_utils import count_manufacturers
from utils.timestamp import current_timestamp
from serializers.drug_summary_factory import from_api as build_drug_summary

def build_summary_row_header():
    return [
        ["Drug Name", "Total Results", "Filtered Results", "Alignment Score (0-10)"],
        ["", "", "", "Based on % of drug variants matching your selected filters"]
    ]

def build_manufacturer_section(drug_name, variants):
    section = [[]]
    section.append([f"Top Manufacturers for {drug_name}", "Count"])

    mfr_counts = count_manufacturers(variants)
    mfr_df = pd.DataFrame({
        "Manufacturer": list(mfr_counts.keys()),
        "Count": list(mfr_counts.values())
    }).sort_values(by="Count", ascending=False)

    for _, row in mfr_df.iterrows():
        section.append([row["Manufacturer"], row["Count"]])

    return section

def format_export_data(raw_data):
    timestamp = current_timestamp()
    filters_used = raw_data.get("filters_applied", [])
    filters_str = ", ".join([f["label"] for f in filters_used])

    rows = [
        ["Created At:", f"{timestamp}"],
        ["Filters Used:", filters_str],
        [],
    ]

    rows.extend(build_summary_row_header())

    summaries = []
    all_manufacturer_sections = []

    for summary in raw_data.get("summary", []):
        drug_summary = build_drug_summary(summary)
        summaries.append(drug_summary)

        section = build_manufacturer_section(drug_summary.drug_name, drug_summary.variants)
        all_manufacturer_sections.extend(section)

    summaries.sort(key=lambda x: x.filtered_count, reverse=True)
    for summary in summaries:
        rows.append(summary.to_row())

    rows.extend(all_manufacturer_sections)

    return rows