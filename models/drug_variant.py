class DrugVariant:
    def __init__(self, brand_name=None, manufacturer_name=None, product_ndc=None):
        self.brand_name = brand_name
        self.manufacturer_name = manufacturer_name
        self.product_ndc = product_ndc

    def to_dict(self):
        return {
            "brand_name": self.brand_name,
            "manufacturer_name": self.manufacturer_name,
            "product_ndc": self.product_ndc
        }