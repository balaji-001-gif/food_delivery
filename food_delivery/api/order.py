import frappe
import json
from frappe.utils import now_datetime


@frappe.whitelist()
def create_order(order_data):
    """Create new food order via API"""
    if isinstance(order_data, str):
        order_data = json.loads(order_data)
    
    # Validate customer
    customer = frappe.db.get_value(
        "Customer",
        {"email_id": frappe.session.user},
        "name"
    )
    
    if not customer:
        frappe.throw("Customer profile not found. Please complete your profile.")
    
    order_data["customer"] = customer
    
    from food_delivery.doctype.food_order.food_order import place_order
    return place_order(order_data)


@frappe.whitelist()
def get_order_status(order_name):
    """Get real-time order status"""
    order = frappe.db.get_value(
        "Food Order",
        order_name,
        ["name", "order_status", "payment_status", "delivery_agent",
         "estimated_delivery_time", "actual_delivery_time"],
        as_dict=True
    )
    
    if not order:
        frappe.throw("Order not found")
    
    return order


@frappe.whitelist()
def cancel_order(order_name, reason=None):
    """Cancel an order"""
    order = frappe.get_doc("Food Order", order_name)
    
    # Check if user has permission
    customer = frappe.db.get_value("Customer", {"email_id": frappe.session.user}, "name")
    if order.customer != customer and "System Manager" not in frappe.get_roles():
        frappe.throw("You don't have permission to cancel this order")
    
    if order.order_status not in ["Pending", "Confirmed"]:
        frappe.throw(f"Order cannot be cancelled in {order.order_status} status")
    
    order.order_status = "Cancelled"
    order.cancellation_reason = reason or "Cancelled by customer"
    order.save(ignore_permissions=True)
    
    if order.docstatus == 1:
        order.cancel()
    
    return {"success": True, "message": "Order cancelled successfully"}


@frappe.whitelist()
def rate_order(order_name, rating, review=None, food_rating=None, delivery_rating=None):
    """Rate a delivered order"""
    order = frappe.get_doc("Food Order", order_name)
    
    if order.order_status != "Delivered":
        frappe.throw("You can only rate delivered orders")
    
    customer = frappe.db.get_value("Customer", {"email_id": frappe.session.user}, "name")
    if order.customer != customer:
        frappe.throw("You can only rate your own orders")
    
    # Update order rating
    order.rating = rating
    order.review = review
    order.save(ignore_permissions=True)
    
    # Create restaurant review
    review_doc = frappe.get_doc({
        "doctype": "Restaurant Review",
        "restaurant": order.restaurant,
        "customer": customer,
        "order": order_name,
        "rating": rating,
        "review_text": review,
        "food_rating": food_rating,
        "delivery_rating": delivery_rating
    })
    review_doc.insert(ignore_permissions=True)
    
    return {"success": True, "message": "Thank you for your review!"}


@frappe.whitelist()
def reorder(order_name):
    """Reorder from previous order"""
    old_order = frappe.get_doc("Food Order", order_name)
    
    customer = frappe.db.get_value("Customer", {"email_id": frappe.session.user}, "name")
    if old_order.customer != customer:
        frappe.throw("Permission denied")
    
    # Check if restaurant is still active
    restaurant = frappe.get_doc("Restaurant", old_order.restaurant)
    if not restaurant.is_open():
        frappe.throw(f"Restaurant {old_order.restaurant} is currently closed")
    
    # Check if items are still available
    items = []
    for item in old_order.items:
        menu_item = frappe.db.get_value(
            "Menu Item",
            item.menu_item,
            ["name", "price", "is_available"],
            as_dict=True
        )
        if menu_item and menu_item.is_available:
            items.append({
                "menu_item": item.menu_item,
                "item_name": item.item_name,
                "quantity": item.quantity,
                "rate": menu_item.price  # Use current price
            })
    
    if not items:
        frappe.throw("None of the items from previous order are available")
    
    order_data = {
        "customer": customer,
        "restaurant": old_order.restaurant,
        "delivery_address": old_order.delivery_address,
        "contact_number": old_order.contact_number,
        "payment_method": old_order.payment_method,
        "items": items
    }
    
    from food_delivery.doctype.food_order.food_order import place_order
    return place_order(order_data)
