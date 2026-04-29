import frappe
from frappe.model.document import Document


class MenuCategory(Document):
    def validate(self):
        self.validate_restaurant()

    def validate_restaurant(self):
        if not frappe.db.exists("Restaurant", self.restaurant):
            frappe.throw(f"Restaurant {self.restaurant} does not exist")

    def get_items(self):
        return frappe.get_all(
            "Menu Item",
            filters={
                "restaurant": self.restaurant,
                "category": self.category_name,
                "is_available": 1
            },
            fields=["*"]
        )
