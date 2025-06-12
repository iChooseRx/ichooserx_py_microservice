from models.drug_variant import DrugVariant

class DrugSummary:
    def __init__(
        self,
        drug_name: str,
        alignment_score: float,
        manufacturer_count: int,
        filtered_count: int,
        total_count: int,
        variants: list[DrugVariant],
    ):
        self.drug_name = drug_name
        self.alignment_score = alignment_score
        self.manufacturer_count = manufacturer_count
        self.filtered_count = filtered_count
        self.total_count = total_count
        self.variants = variants

    def to_row(self):
        return [
            self.drug_name,
            self.total_count,
            self.filtered_count,
            self.alignment_score,
        ]