import frappe
from frappe.model.document import Document


class MenuItem(Document):
    def validate(self):
        self.validate_price()
        self.validate_category()

    def validate_price(self):
        if self.price <= 0:
            frappe.throw("Price must be greater than 0")
        if self.discounted_price and self.discounted_price >= self.price:
            frappe.throw("Discounted price must be less than original price")

    def validate_category(self):
        if self.category:
            category = frappe.db.get_value(
                "Menu Category", 
                self.category, 
                ["restaurant", "is_active"],
                as_dict=True
            )
            if not category:
                frappe.throw(f"Category {self.category} does not exist")
            if category.restaurant != self.restaurant:
                frappe.throw("Category does not belong to this restaurant")

    def get_effective_price(self):
        """Return discounted price if available, else original price"""
        if self.discounted_price and self.discounted_price > 0:
            return self.discounted_price
        return self.price

    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.discounted_price and self.discounted_price > 0:
            return round(((self.price - self.discounted_price) / self.price) * 100, 0)
        return 0


@frappe.whitelist()
def search_menu_items(query, restaurant=None, cuisine=None, is_veg=None):
    """Search menu items"""
    filters = {"is_available": 1}
    
    if restaurant:
        filters["restaurant"] = restaurant
    if is_veg is not None:
        filters["is_veg"] = int(is_veg)
    
    items = frappe.get_all(
        "Menu Item",
        filters=filters,
        fields=["name", "item_name", "restaurant", "category", "price", 
               "discounted_price", "image", "is_veg", "description", "is_bestseller"],
        or_filters={
            "item_name": ["like", f"%{query}%"],
            "description": ["like", f"%{query}%"]
        }
    )
    return items
