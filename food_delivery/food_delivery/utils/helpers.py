import frappe
import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance


def format_currency(amount, currency="INR"):
    """Format amount as currency"""
    if currency == "INR":
        return f"\u20b9{amount:,.2f}"
    return f"{currency} {amount:,.2f}"


def get_rating_stars(rating):
    """Return star rating HTML"""
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    stars = "\u2605" * full_stars
    if half_star:
        stars += "\u00bd"
    stars += "\u2606" * empty_stars
    
    return stars


def generate_otp():
    """Generate 6-digit OTP"""
    import random
    return str(random.randint(100000, 999999))


def send_sms(phone, message):
    """Send SMS notification"""
    try:
        sms_settings = frappe.get_single("Food Delivery Settings")
        if sms_settings.sms_enabled:
            # Add SMS gateway code here
            pass
    except Exception as e:
        frappe.log_error(f"SMS sending failed: {str(e)}")


def get_delivery_eta(restaurant, delivery_address):
    """Calculate estimated delivery time"""
    prep_time = frappe.db.get_value("Restaurant", restaurant, "preparation_time") or 30
    delivery_time = frappe.db.get_value("Restaurant", restaurant, "delivery_time") or 30
    
    return prep_time + delivery_time


def validate_phone(phone):
    """Validate Indian phone number"""
    import re
    pattern = r'^(\+91|91)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone.replace(" ", "")))


def create_notification(recipient, subject, message, notification_type="Alert"):
    """Create system notification"""
    try:
        frappe.get_doc({
            "doctype": "Notification Log",
            "for_user": recipient,
            "subject": subject,
            "message": message,
            "type": notification_type,
            "read": 0
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Notification creation failed: {str(e)}")
