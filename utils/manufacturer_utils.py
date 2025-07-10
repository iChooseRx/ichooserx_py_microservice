from collections import Counter
import re

def normalize_manufacturer_name(name: str) -> str:
    name = name.strip().rstrip('.')
    name = re.sub(r'\s*,\s*', ', ', name)
    return name.title()

def count_manufacturers(variants: list) -> dict:
    manufacturers = [
        normalize_manufacturer_name(v.manufacturer_name)
        for v in variants
        if v.manufacturer_name
    ]
    return dict(Counter(manufacturers))

