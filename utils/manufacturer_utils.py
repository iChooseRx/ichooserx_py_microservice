from collections import Counter

def count_manufacturers(variants: list) -> dict:
    manufacturers = [v.manufacturer_name for v in variants if v.manufacturer_name]
    return dict(Counter(manufacturers))
