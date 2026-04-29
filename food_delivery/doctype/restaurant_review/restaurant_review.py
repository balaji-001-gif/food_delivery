import frappe
from frappe.model.document import Document


class RestaurantReview(Document):
    def validate(self):
        self.validate_one_review_per_order()

    def validate_one_review_per_order(self):
        if self.order:
            existing = frappe.db.exists(
                "Restaurant Review",
                {
                    "order": self.order,
                    "customer": self.customer,
                    "name": ["!=", self.name]
                }
            )
            if existing:
                frappe.throw("You have already reviewed this order")

    def after_insert(self):
        # Update restaurant rating
        restaurant = frappe.get_doc("Restaurant", self.restaurant)
        restaurant.update_rating()

    def on_trash(self):
        # Update restaurant rating after deletion
        restaurant = frappe.get_doc("Restaurant", self.restaurant)
        restaurant.update_rating()
