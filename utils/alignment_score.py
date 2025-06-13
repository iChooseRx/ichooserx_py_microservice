def calculate_alignment_score(filtered: int, total: int) -> float:
    if total == 0:
        return 0.0
    score = (filtered / total) * 10
    return round(score, 1)