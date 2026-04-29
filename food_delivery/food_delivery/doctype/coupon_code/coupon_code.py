import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class CouponCode(Document):
    def validate(self):
        self.validate_dates()
        self.validate_discount()
        self.code = self.code.upper()

    def validate_dates(self):
        if self.valid_from and self.expiry_date:
            if self.valid_from > self.expiry_date:
                frappe.throw("Expiry date must be after valid from date")

    def validate_discount(self):
        if self.discount_value <= 0:
            frappe.throw("Discount value must be greater than 0")
        if self.discount_type == "Percentage" and self.discount_value > 100:
            frappe.throw("Percentage discount cannot exceed 100%")

    def is_valid(self, order_amount=0, customer=None):
        """Check if coupon is valid"""
        if not self.is_active:
            return False, "Coupon is not active"
        
        if self.valid_from and self.valid_from > nowdate():
            return False, "Coupon is not yet valid"
        
        if self.expiry_date and self.expiry_date < nowdate():
            return False, "Coupon has expired"
        
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False, "Coupon usage limit exceeded"
        
        if self.minimum_order and order_amount < self.minimum_order:
            return False, f"Minimum order amount is ₹{self.minimum_order}"
        
        if customer and self.per_user_limit:
            customer_usage = frappe.db.count(
                "Food Order",
                {"coupon_code": self.name, "customer": customer, "docstatus": 1}
            )
            if customer_usage >= self.per_user_limit:
                return False, "You have already used this coupon"
        
        return True, "Valid"


@frappe.whitelist()
def validate_coupon(coupon_code, order_amount, customer, restaurant=None):
    """Validate a coupon code"""
    if not frappe.db.exists("Coupon Code", coupon_code):
        return {"valid": False, "message": "Invalid coupon code"}
    
    coupon = frappe.get_doc("Coupon Code", coupon_code)
    
    if coupon.restaurant and restaurant and coupon.restaurant != restaurant:
        return {"valid": False, "message": "Coupon is not valid for this restaurant"}
    
    is_valid, message = coupon.is_valid(float(order_amount), customer)
    
    if not is_valid:
        return {"valid": False, "message": message}
    
    # Calculate discount
    if coupon.discount_type == "Percentage":
        discount = (float(order_amount) * coupon.discount_value) / 100
        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)
    else:
        discount = coupon.discount_value
    
    return {
        "valid": True,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value,
        "discount_amount": round(discount, 2),
        "description": coupon.description
    }


def expire_coupons():
    """Scheduled: Deactivate expired coupons"""
    frappe.db.sql("""
        UPDATE `tabCoupon Code`
        SET is_active = 0
        WHERE expiry_date < CURDATE()
        AND is_active = 1
    """)
    frappe.db.commit()
