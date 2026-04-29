import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, nowdate
import json


class FoodOrder(Document):
    def validate(self):
        self.validate_restaurant_open()
        self.validate_minimum_order()
        self.calculate_totals()
        self.validate_coupon()
        self.set_estimated_delivery_time()

    def validate_restaurant_open(self):
        restaurant = frappe.get_doc("Restaurant", self.restaurant)
        if not restaurant.is_open():
            frappe.throw(f"Restaurant {self.restaurant} is currently closed")

    def validate_minimum_order(self):
        minimum = frappe.db.get_value("Restaurant", self.restaurant, "minimum_order_amount")
        if minimum and self.subtotal < minimum:
            frappe.throw(f"Minimum order amount is ₹{minimum}")

    def calculate_totals(self):
        """Calculate order totals"""
        subtotal = 0
        for item in self.items:
            item.amount = item.quantity * item.rate
            subtotal += item.amount
        
        self.subtotal = subtotal
        
        # Get restaurant charges
        restaurant = frappe.db.get_value(
            "Restaurant", self.restaurant,
            ["delivery_charge", "free_delivery_above", "tax_rate"],
            as_dict=True
        )
        
        # Calculate delivery charge
        if restaurant.free_delivery_above and subtotal >= restaurant.free_delivery_above:
            self.delivery_charge = 0
        else:
            self.delivery_charge = restaurant.delivery_charge or 0
        
        # Calculate tax
        tax_rate = restaurant.tax_rate or 0
        self.tax_amount = round((subtotal * tax_rate) / 100, 2)
        
        # Calculate coupon discount
        if self.coupon_code:
            self.coupon_discount = self.calculate_coupon_discount(subtotal)
        else:
            self.coupon_discount = 0
        
        # Calculate total
        self.discount_amount = self.coupon_discount
        self.total_amount = (
            self.subtotal + 
            self.delivery_charge + 
            self.tax_amount - 
            self.discount_amount
        )

    def calculate_coupon_discount(self, subtotal):
        """Calculate coupon discount"""
        if not self.coupon_code:
            return 0
        
        coupon = frappe.db.get_value(
            "Coupon Code",
            self.coupon_code,
            ["discount_type", "discount_value", "minimum_order", "max_discount"],
            as_dict=True
        )
        
        if not coupon:
            return 0
        
        if coupon.minimum_order and subtotal < coupon.minimum_order:
            frappe.throw(f"Minimum order amount for this coupon is ₹{coupon.minimum_order}")
        
        if coupon.discount_type == "Percentage":
            discount = (subtotal * coupon.discount_value) / 100
            if coupon.max_discount:
                discount = min(discount, coupon.max_discount)
        else:
            discount = coupon.discount_value
        
        return round(discount, 2)

    def validate_coupon(self):
        """Validate coupon code"""
        if not self.coupon_code:
            return
        
        coupon = frappe.get_doc("Coupon Code", self.coupon_code)
        
        if not coupon.is_active:
            frappe.throw("Coupon code is not active")
        
        if coupon.expiry_date and coupon.expiry_date < nowdate():
            frappe.throw("Coupon code has expired")
        
        if coupon.usage_limit and coupon.times_used >= coupon.usage_limit:
            frappe.throw("Coupon usage limit exceeded")
        
        if coupon.restaurant and coupon.restaurant != self.restaurant:
            frappe.throw("Coupon is not valid for this restaurant")

    def set_estimated_delivery_time(self):
        """Set estimated delivery time"""
        if not self.estimated_delivery_time:
            prep_time = frappe.db.get_value("Restaurant", self.restaurant, "preparation_time") or 30
            delivery_time = frappe.db.get_value("Restaurant", self.restaurant, "delivery_time") or 30
            total_time = prep_time + delivery_time
            self.estimated_delivery_time = add_to_date(now_datetime(), minutes=total_time)

    def before_submit(self):
        if self.order_status not in ["Delivered"]:
            self.order_status = "Confirmed"
        if self.payment_method != "Cash on Delivery" and self.payment_status != "Paid":
            frappe.throw("Payment must be completed before order submission")

    def on_submit(self):
        """Actions after order submission"""
        # Update coupon usage
        if self.coupon_code:
            frappe.db.sql("""
                UPDATE `tabCoupon Code` 
                SET times_used = times_used + 1
                WHERE name = %s
            """, self.coupon_code)
        
        # Update restaurant stats
        frappe.db.sql("""
            UPDATE `tabRestaurant`
            SET total_orders = total_orders + 1
            WHERE name = %s
        """, self.restaurant)
        
        # Send notification
        self.send_order_notification()
        
        frappe.db.commit()

    def on_cancel(self):
        """Actions after order cancellation"""
        # Refund coupon usage
        if self.coupon_code:
            frappe.db.sql("""
                UPDATE `tabCoupon Code`
                SET times_used = times_used - 1
                WHERE name = %s
            """, self.coupon_code)
        
        # Update restaurant stats
        frappe.db.sql("""
            UPDATE `tabRestaurant`
            SET total_orders = total_orders - 1
            WHERE name = %s
        """, self.restaurant)
        
        # Initiate refund if payment was done
        if self.payment_status == "Paid":
            self.initiate_refund()
        
        frappe.db.commit()

    def after_insert(self):
        """Actions after order creation"""
        # Send confirmation SMS/Email
        self.send_order_confirmation()

    def send_order_notification(self):
        """Send order notifications"""
        try:
            customer_email = frappe.db.get_value("Customer", self.customer, "email_id")
            restaurant_email = frappe.db.get_value("Restaurant", self.restaurant, "email")
            
            if customer_email:
                frappe.sendmail(
                    recipients=[customer_email],
                    subject=f"Order Confirmed - {self.name}",
                    message=f"""
                        <h3>Your order has been confirmed!</h3>
                        <p>Order ID: {self.name}</p>
                        <p>Restaurant: {self.restaurant}</p>
                        <p>Total Amount: ₹{self.total_amount}</p>
                        <p>Estimated Delivery: {self.estimated_delivery_time}</p>
                    """,
                    now=True
                )
        except Exception as e:
            frappe.log_error(f"Error sending order notification: {str(e)}")

    def send_order_confirmation(self):
        """Send order confirmation"""
        pass  # Implement SMS/Push notification here

    def initiate_refund(self):
        """Initiate payment refund"""
        frappe.get_doc({
            "doctype": "Payment Transaction",
            "order": self.name,
            "transaction_type": "Refund",
            "amount": self.total_amount,
            "payment_method": self.payment_method,
            "reference_id": self.transaction_id,
            "status": "Pending"
        }).insert(ignore_permissions=True)

    def update_status(self, new_status, delivery_agent=None):
        """Update order status"""
        valid_transitions = {
            "Pending": ["Confirmed", "Cancelled"],
            "Confirmed": ["Preparing", "Cancelled"],
            "Preparing": ["Ready for Pickup", "Cancelled"],
            "Ready for Pickup": ["Out for Delivery", "Cancelled"],
            "Out for Delivery": ["Delivered"],
            "Delivered": [],
            "Cancelled": []
        }
        
        if new_status not in valid_transitions.get(self.order_status, []):
            frappe.throw(f"Cannot transition from {self.order_status} to {new_status}")
        
        self.order_status = new_status
        
        if delivery_agent:
            self.delivery_agent = delivery_agent
        
        if new_status == "Delivered":
            self.actual_delivery_time = now_datetime()
            if self.payment_method == "Cash on Delivery":
                self.payment_status = "Paid"
        
        self.save(ignore_permissions=True)
        frappe.db.commit()


@frappe.whitelist()
def place_order(order_data):
    """Place a new food order"""
    if isinstance(order_data, str):
        order_data = json.loads(order_data)
    
    order = frappe.get_doc({
        "doctype": "Food Order",
        "customer": order_data.get("customer"),
        "restaurant": order_data.get("restaurant"),
        "delivery_address": order_data.get("delivery_address"),
        "contact_number": order_data.get("contact_number"),
        "payment_method": order_data.get("payment_method", "Cash on Delivery"),
        "special_instructions": order_data.get("special_instructions"),
        "coupon_code": order_data.get("coupon_code"),
        "delivery_latitude": order_data.get("latitude"),
        "delivery_longitude": order_data.get("longitude"),
        "items": order_data.get("items", [])
    })
    
    order.insert(ignore_permissions=True)
    
    if order_data.get("payment_method") == "Cash on Delivery":
        order.submit()
    
    return {
        "success": True,
        "order_name": order.name,
        "total_amount": order.total_amount,
        "estimated_delivery_time": str(order.estimated_delivery_time)
    }


@frappe.whitelist()
def update_order_status(order_name, new_status, delivery_agent=None):
    """Update order status"""
    order = frappe.get_doc("Food Order", order_name)
    order.update_status(new_status, delivery_agent)
    
    return {
        "success": True,
        "order_status": new_status
    }


@frappe.whitelist()
def get_order_tracking(order_name):
    """Get order tracking details"""
    order = frappe.get_doc("Food Order", order_name)
    
    tracking_info = {
        "order_name": order.name,
        "order_status": order.order_status,
        "estimated_delivery_time": str(order.estimated_delivery_time),
        "actual_delivery_time": str(order.actual_delivery_time) if order.actual_delivery_time else None,
        "delivery_agent": None,
        "items": []
    }
    
    if order.delivery_agent:
        agent = frappe.db.get_value(
            "Delivery Agent",
            order.delivery_agent,
            ["agent_name", "phone", "current_latitude", "current_longitude"],
            as_dict=True
        )
        tracking_info["delivery_agent"] = agent
    
    for item in order.items:
        tracking_info["items"].append({
            "item_name": item.item_name,
            "quantity": item.quantity,
            "rate": item.rate,
            "amount": item.amount
        })
    
    return tracking_info


@frappe.whitelist()
def get_customer_orders(customer, limit=10, offset=0):
    """Get customer order history"""
    orders = frappe.get_all(
        "Food Order",
        filters={"customer": customer},
        fields=["name", "restaurant", "restaurant_name_display", "order_date",
               "order_status", "total_amount", "payment_status", "rating"],
        order_by="order_date desc",
        limit=int(limit),
        start=int(offset)
    )
    return orders


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Restaurant Manager" in frappe.get_roles(user):
        restaurants = frappe.get_all(
            "Restaurant",
            filters={"owner": user},
            pluck="name"
        )
        if restaurants:
            restaurant_list = "','".join(restaurants)
            return f"(`tabFood Order`.restaurant in ('{restaurant_list}'))"
        return "1=0"
    
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    if customer:
        return f"(`tabFood Order`.customer = '{customer}')"
    
    if "Delivery Agent" in frappe.get_roles(user):
        agent = frappe.db.get_value("Delivery Agent", {"email": user}, "name")
        if agent:
            return f"(`tabFood Order`.delivery_agent = '{agent}')"
    
    return "1=0"


def has_permission(doc, ptype, user):
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return True
    
    return None
