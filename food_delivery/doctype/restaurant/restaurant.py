import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_time, nowtime
import datetime


class Restaurant(Document):
    def validate(self):
        self.validate_timing()
        self.validate_charges()
        self.validate_contact()

    def validate_timing(self):
        if self.opening_time and self.closing_time:
            opening = get_time(self.opening_time)
            closing = get_time(self.closing_time)
            if opening >= closing:
                frappe.throw("Closing time must be after opening time")

    def validate_charges(self):
        if self.delivery_charge < 0:
            frappe.throw("Delivery charge cannot be negative")
        if self.minimum_order_amount < 0:
            frappe.throw("Minimum order amount cannot be negative")
        if self.tax_rate < 0 or self.tax_rate > 100:
            frappe.throw("Tax rate must be between 0 and 100")

    def validate_contact(self):
        if self.email:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, self.email):
                frappe.throw("Invalid email address")

    def is_open(self):
        """Check if restaurant is currently open"""
        if self.status != "Active":
            return False
        
        current_time = get_time(nowtime())
        opening = get_time(self.opening_time)
        closing = get_time(self.closing_time)
        
        return opening <= current_time <= closing

    def update_rating(self):
        """Update average rating from reviews"""
        result = frappe.db.sql("""
            SELECT AVG(rating) as avg_rating, COUNT(*) as total
            FROM `tabRestaurant Review`
            WHERE restaurant = %s AND docstatus = 0
        """, self.name, as_dict=True)
        
        if result:
            self.average_rating = round(result[0].avg_rating or 0, 1)
            self.total_reviews = result[0].total or 0
            self.save(ignore_permissions=True)

    def update_order_count(self):
        """Update total orders count"""
        count = frappe.db.count("Food Order", {
            "restaurant": self.name,
            "docstatus": 1
        })
        self.total_orders = count
        self.save(ignore_permissions=True)

    def get_menu(self):
        """Get restaurant menu"""
        return frappe.get_all(
            "Menu Item",
            filters={"restaurant": self.name, "is_available": 1},
            fields=["name", "item_name", "category", "price", 
                   "description", "image", "is_veg", "preparation_time"],
            order_by="category, item_name"
        )


@frappe.whitelist()
def get_nearby_restaurants(latitude, longitude, radius=5, cuisine=None):
    """Get restaurants within specified radius"""
    filters = {"status": "Active"}
    if cuisine:
        filters["cuisine_type"] = ["like", f"%{cuisine}%"]
    
    restaurants = frappe.get_all(
        "Restaurant",
        filters=filters,
        fields=["name", "restaurant_name", "logo", "average_rating", 
               "total_orders", "delivery_charge", "preparation_time",
               "delivery_time", "minimum_order_amount", "cuisine_type",
               "latitude", "longitude", "opening_time", "closing_time"],
    )
    
    if latitude and longitude:
        from food_delivery.utils.helpers import calculate_distance
        for restaurant in restaurants:
            if restaurant.latitude and restaurant.longitude:
                distance = calculate_distance(
                    float(latitude), float(longitude),
                    float(restaurant.latitude), float(restaurant.longitude)
                )
                restaurant["distance"] = round(distance, 2)
            else:
                restaurant["distance"] = None
        
        restaurants = [r for r in restaurants if r["distance"] is not None and r["distance"] <= float(radius)]
        restaurants.sort(key=lambda x: x["distance"])
    
    return restaurants


@frappe.whitelist()
def get_restaurant_details(restaurant_name):
    """Get complete restaurant details"""
    restaurant = frappe.get_doc("Restaurant", restaurant_name)
    
    menu = frappe.get_all(
        "Menu Item",
        filters={"restaurant": restaurant_name, "is_available": 1},
        fields=["name", "item_name", "category", "price", "description", 
               "image", "is_veg", "preparation_time", "calories"],
        order_by="category, item_name"
    )
    
    # Group menu by category
    menu_by_category = {}
    for item in menu:
        if item.category not in menu_by_category:
            menu_by_category[item.category] = []
        menu_by_category[item.category].append(item)
    
    reviews = frappe.get_all(
        "Restaurant Review",
        filters={"restaurant": restaurant_name},
        fields=["customer_name", "rating", "review_text", "creation"],
        limit=10,
        order_by="creation desc"
    )
    
    return {
        "restaurant": restaurant.as_dict(),
        "menu": menu_by_category,
        "reviews": reviews,
        "is_open": restaurant.is_open()
    }


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Restaurant Manager" in frappe.get_roles(user):
        return f"(`tabRestaurant`.owner = '{user}')"
    
    return "(`tabRestaurant`.status = 'Active')"


def reset_daily_stats():
    """Reset daily statistics"""
    frappe.db.sql("""
        UPDATE `tabRestaurant` 
        SET today_orders = 0, today_revenue = 0
    """)
    frappe.db.commit()
