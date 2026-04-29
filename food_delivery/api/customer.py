import frappe
import json


@frappe.whitelist()
def get_profile():
    """Get customer profile"""
    user = frappe.session.user
    
    customer = frappe.db.get_value(
        "Customer",
        {"email_id": user},
        ["name", "customer_name", "email_id", "mobile_no"],
        as_dict=True
    )
    
    if not customer:
        frappe.throw("Customer profile not found")
    
    return customer


@frappe.whitelist()
def update_profile(profile_data):
    """Update customer profile"""
    if isinstance(profile_data, str):
        profile_data = json.loads(profile_data)
    
    user = frappe.session.user
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    
    if not customer:
        frappe.throw("Customer profile not found")
    
    customer_doc = frappe.get_doc("Customer", customer)
    
    if profile_data.get("customer_name"):
        customer_doc.customer_name = profile_data["customer_name"]
    if profile_data.get("mobile_no"):
        customer_doc.mobile_no = profile_data["mobile_no"]
    
    customer_doc.save(ignore_permissions=True)
    return {"success": True, "message": "Profile updated successfully"}


@frappe.whitelist()
def get_saved_addresses():
    """Get customer saved addresses"""
    user = frappe.session.user
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    
    if not customer:
        return []
    
    addresses = frappe.get_all(
        "Customer Address",
        filters={"customer": customer},
        fields=["name", "address_type", "address_line1", "address_line2",
               "city", "state", "pincode", "latitude", "longitude", "is_default"]
    )
    return addresses


@frappe.whitelist()
def save_address(address_data):
    """Save delivery address"""
    if isinstance(address_data, str):
        address_data = json.loads(address_data)
    
    user = frappe.session.user
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    
    if not customer:
        frappe.throw("Customer profile not found")
    
    address_data["customer"] = customer
    address_data["doctype"] = "Customer Address"
    
    if address_data.get("is_default"):
        # Remove default from other addresses
        frappe.db.sql("""
            UPDATE `tabCustomer Address`
            SET is_default = 0
            WHERE customer = %s
        """, customer)
    
    address = frappe.get_doc(address_data)
    address.insert(ignore_permissions=True)
    
    return {"success": True, "address_id": address.name}


@frappe.whitelist()
def get_order_history(limit=10, offset=0):
    """Get customer order history"""
    user = frappe.session.user
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    
    if not customer:
        return []
    
    orders = frappe.get_all(
        "Food Order",
        filters={"customer": customer, "docstatus": ["!=", 2]},
        fields=[
            "name", "restaurant", "restaurant_name_display", "order_date",
            "order_status", "total_amount", "payment_status", "rating",
            "payment_method"
        ],
        order_by="order_date desc",
        limit=int(limit),
        start=int(offset)
    )
    
    # Get items for each order
    for order in orders:
        order["items"] = frappe.get_all(
            "Food Order Item",
            filters={"parent": order.name},
            fields=["item_name", "quantity", "rate", "amount"]
        )
    
    return orders


def on_login(login_manager):
    """On user login"""
    user = login_manager.user
    
    # Check if customer profile exists
    if not frappe.db.exists("Customer", {"email_id": user}):
        user_doc = frappe.get_doc("User", user)
        
        # Create customer profile
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": user_doc.full_name or user_doc.email,
            "email_id": user,
            "mobile_no": user_doc.phone or "",
            "customer_type": "Individual",
            "customer_group": "Individual",
            "territory": "India"
        })
        customer.insert(ignore_permissions=True)
        frappe.db.commit()
