import frappe
from frappe.utils import now_datetime, add_to_date
import random

def run():
    """Entry point for demo data creation via bench execute"""
    print("Initializing demo data generation...")
    
    try:
        create_zones()
        create_restaurants()
        create_agents()
        create_coupon_codes()
        create_customers()
        create_orders()
        
        frappe.db.commit()
        print("Demo data created successfully!")
        
    except Exception as e:
        frappe.db.rollback()
        print(f"Error generating demo data: {str(e)}")
        raise e

def create_zones():
    print("Creating Delivery Zones...")
    zones = [
        {"zone_name": "Central Zone", "city": "Chennai", "state": "Tamil Nadu"},
        {"zone_name": "North Zone", "city": "Chennai", "state": "Tamil Nadu"},
        {"zone_name": "South Zone", "city": "Chennai", "state": "Tamil Nadu"},
        {"zone_name": "West Zone", "city": "Chennai", "state": "Tamil Nadu"},
        {"zone_name": "East Zone", "city": "Chennai", "state": "Tamil Nadu"}
    ]
    for z in zones:
        if not frappe.db.exists("Delivery Zone", z["zone_name"]):
            doc = frappe.get_doc({
                "doctype": "Delivery Zone",
                "zone_name": z["zone_name"],
                "city": z["city"],
                "state": z["state"],
                "is_active": 1
            })
            doc.insert(ignore_permissions=True)

def create_restaurants():
    print("Creating Restaurants and Menus...")
    restaurants = [
        {
            "restaurant_name": "Pizza Palace",
            "owner_name": "John Doe",
            "email": "pizza@palace.com",
            "phone": "9876543210",
            "address_line1": "123 Main St",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "600001",
            "opening_time": "10:00:00",
            "closing_time": "23:00:00",
            "status": "Active",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "delivery_charge": 40,
            "free_delivery_above": 500,
            "tax_rate": 5,
            "preparation_time": 30,
            "delivery_time": 25,
            "menu": [
                {"category": "Pizza", "item_name": "Margherita", "rate": 199, "is_veg": 1},
                {"category": "Pizza", "item_name": "Pepperoni Feast", "rate": 399, "is_veg": 0},
                {"category": "Sides", "item_name": "Garlic Bread", "rate": 99, "is_veg": 1},
                {"category": "Beverages", "item_name": "Coke 330ml", "rate": 40, "is_veg": 1}
            ]
        },
        {
            "restaurant_name": "Burger Barn",
            "owner_name": "Jane Smith",
            "email": "contact@burgerbarn.com",
            "phone": "9876543211",
            "address_line1": "45 Park Ave",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "600002",
            "opening_time": "11:00:00",
            "closing_time": "22:00:00",
            "status": "Active",
            "latitude": 13.0012,
            "longitude": 80.2565,
            "delivery_charge": 30,
            "free_delivery_above": 300,
            "tax_rate": 5,
            "preparation_time": 15,
            "delivery_time": 20,
            "menu": [
                {"category": "Burgers", "item_name": "Classic Veggie Burger", "rate": 120, "is_veg": 1},
                {"category": "Burgers", "item_name": "Double Cheese Chicken Burger", "rate": 250, "is_veg": 0},
                {"category": "Sides", "item_name": "Peri Peri Fries", "rate": 80, "is_veg": 1}
            ]
        }
    ]
    
    for r_data in restaurants:
        if not frappe.db.exists("Restaurant", r_data["restaurant_name"]):
            r_doc = frappe.get_doc({
                "doctype": "Restaurant",
                "restaurant_name": r_data["restaurant_name"],
                "owner_name": r_data["owner_name"],
                "email": r_data["email"],
                "phone": r_data["phone"],
                "address_line1": r_data["address_line1"],
                "city": r_data["city"],
                "state": r_data["state"],
                "pincode": r_data["pincode"],
                "opening_time": r_data["opening_time"],
                "closing_time": r_data["closing_time"],
                "status": r_data["status"],
                "latitude": r_data["latitude"],
                "longitude": r_data["longitude"],
                "delivery_charge": r_data["delivery_charge"],
                "free_delivery_above": r_data["free_delivery_above"],
                "tax_rate": r_data["tax_rate"],
                "preparation_time": r_data["preparation_time"],
                "delivery_time": r_data["delivery_time"]
            })
            r_doc.insert(ignore_permissions=True)
            
            # Create Categories and Items
            for m_item in r_data["menu"]:
                if not frappe.db.exists("Menu Category", m_item["category"]):
                    c_doc = frappe.get_doc({
                        "doctype": "Menu Category",
                        "category_name": m_item["category"]
                    })
                    c_doc.insert(ignore_permissions=True)
                
                if not frappe.db.exists("Menu Item", {"item_name": m_item["item_name"], "restaurant": r_doc.name}):
                    i_doc = frappe.get_doc({
                        "doctype": "Menu Item",
                        "restaurant": r_doc.name,
                        "category": m_item["category"],
                        "item_name": m_item["item_name"],
                        "rate": m_item["rate"],
                        "is_veg": m_item["is_veg"],
                        "is_available": 1
                    })
                    i_doc.insert(ignore_permissions=True)

def create_agents():
    print("Creating Delivery Agents...")
    agents = [
        {
            "naming_series": "DA-.####",
            "agent_name": "Ravi Kumar",
            "phone": "9876543220",
            "email": "ravi@frappe.com",
            "status": "Available",
            "vehicle_type": "Motorcycle",
            "vehicle_number": "TN01AB1234",
            "assigned_zone": "Central Zone"
        },
        {
            "naming_series": "DA-.####",
            "agent_name": "Amit Singh",
            "phone": "9876543221",
            "email": "amit@frappe.com",
            "status": "Available",
            "vehicle_type": "Scooter",
            "vehicle_number": "TN01CD5678",
            "assigned_zone": "South Zone"
        }
    ]
    
    for a_data in agents:
        if not frappe.db.exists("Delivery Agent", {"phone": a_data["phone"]}):
            doc = frappe.get_doc({
                "doctype": "Delivery Agent",
                "naming_series": a_data["naming_series"],
                "agent_name": a_data["agent_name"],
                "phone": a_data["phone"],
                "email": a_data["email"],
                "status": a_data["status"],
                "vehicle_type": a_data["vehicle_type"],
                "vehicle_number": a_data["vehicle_number"],
                "assigned_zone": a_data["assigned_zone"]
            })
            doc.insert(ignore_permissions=True)


def create_coupon_codes():
    print("Creating Coupons...")
    coupons = [
        {
            "coupon_code": "WELCOME50",
            "discount_type": "Percentage",
            "discount_value": 50,
            "minimum_order": 200,
            "max_discount": 100,
            "expiry_date": add_to_date(now_datetime(), days=30),
            "is_active": 1
        },
        {
            "coupon_code": "FLAT100",
            "discount_type": "Flat Amount",
            "discount_value": 100,
            "minimum_order": 500,
            "expiry_date": add_to_date(now_datetime(), days=30),
            "is_active": 1
        }
    ]
    
    for c_data in coupons:
        if not frappe.db.exists("Coupon Code", c_data["coupon_code"]):
            doc = frappe.get_doc({
                "doctype": "Coupon Code",
                "coupon_code": c_data["coupon_code"],
                "discount_type": c_data["discount_type"],
                "discount_value": c_data["discount_value"],
                "minimum_order": c_data["minimum_order"],
                "max_discount": c_data.get("max_discount", 0),
                "expiry_date": c_data["expiry_date"],
                "is_active": c_data["is_active"]
            })
            doc.insert(ignore_permissions=True)

def create_customers():
    print("Creating Customers...")
    customers = [
        {"name": "Balaji", "email_id": "balaji@example.com", "mobile_no": "9999999999"},
        {"name": "Guest User", "email_id": "guest@example.com", "mobile_no": "8888888888"}
    ]
    
    for c_data in customers:
        if not frappe.db.exists("Customer", {"email_id": c_data["email_id"]}):
            doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": c_data["name"],
                "email_id": c_data["email_id"],
                "mobile_no": c_data["mobile_no"]
            })
            doc.insert(ignore_permissions=True)

def create_orders():
    print("Creating Sample Orders...")
    customers = frappe.get_all("Customer", pluck="name")
    restaurants = frappe.get_all("Restaurant", pluck="name")
    
    if not customers or not restaurants:
        return
        
    # Create 1 Pending Order
    restaurant = frappe.get_doc("Restaurant", restaurants[0])
    menu_items = frappe.get_all("Menu Item", filters={"restaurant": restaurant.name}, limit=2)
    
    if not menu_items:
        return
        
    order1 = frappe.get_doc({
        "doctype": "Food Order",
        "naming_series": "ORD-.YYYY.-.MM.-.DD.-.####",
        "customer": customers[0],
        "restaurant": restaurant.name,
        "order_date": now_datetime(),
        "order_status": "Pending",
        "payment_status": "Pending",
        "delivery_address": "Apt 101, Central Plaza, Central Zone",
        "contact_number": "9999999999",
        "payment_method": "UPI",
        "items": [
            {
                "item_name": menu_items[0].name,
                "quantity": 2,
                "rate": 199,
                "amount": 398
            }
        ]
    })
    order1.insert(ignore_permissions=True)
    
    # Create 1 Delivered Order
    if len(restaurants) > 1:
        restaurant2 = frappe.get_doc("Restaurant", restaurants[1])
        menu_items2 = frappe.get_all("Menu Item", filters={"restaurant": restaurant2.name}, limit=1)
        agents = frappe.get_all("Delivery Agent", pluck="name")
        
        if menu_items2 and agents:
            order2 = frappe.get_doc({
                "doctype": "Food Order",
                "naming_series": "ORD-.YYYY.-.MM.-.DD.-.####",
                "customer": customers[0],
                "restaurant": restaurant2.name,
                "order_date": add_to_date(now_datetime(), hours=-24),
                "order_status": "Delivered",
                "payment_status": "Paid",
                "delivery_agent": agents[0],
                "delivery_address": "12 Sector C, South Zone",
                "contact_number": "9999999999",
                "payment_method": "Online Payment",
                "items": [
                    {
                        "item_name": menu_items2[0].name,
                        "quantity": 1,
                        "rate": 250,
                        "amount": 250
                    }
                ]
            })
            order2.insert(ignore_permissions=True)
            order2.submit()
