from models.drug_summary import DrugSummary
from models.drug_variant import DrugVariant
from utils.alignment_score import calculate_alignment_score
from utils.manufacturer_utils import count_manufacturers

def from_api(summary_dict: dict) -> DrugSummary:
    attributes = summary_dict.get("attributes", {})
    drug_name = attributes.get("drug_name", "N/A")
    total = attributes.get("total_results", 0)
    filtered = attributes.get("filtered_results", 0)
    variants_data = attributes.get("variants", [])

    variants = [DrugVariant(**v) for v in variants_data if isinstance(v, dict)]
    alignment_score = calculate_alignment_score(filtered, total)
    manufacturer_count = len(count_manufacturers(variants))

    return DrugSummary(
        drug_name=drug_name,
        alignment_score=alignment_score,
        manufacturer_count=manufacturer_count,
        filtered_count=filtered,
        total_count=total,
        variants=variants,
    )