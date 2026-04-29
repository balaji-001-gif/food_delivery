import frappe
from frappe.utils import today, add_days


@frappe.whitelist()
def get_dashboard_data():
    """Get dashboard statistics"""
    today_date = today()
    yesterday = add_days(today_date, -1)
    
    # Today's stats
    today_stats = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) as delivered,
            SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled,
            SUM(CASE WHEN order_status NOT IN ('Delivered', 'Cancelled') THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN order_status = 'Delivered' THEN total_amount ELSE 0 END) as revenue
        FROM `tabFood Order`
        WHERE DATE(order_date) = %s
        AND docstatus = 1
    """, today_date, as_dict=True)[0]
    
    # Active orders by status
    active_orders = frappe.db.sql("""
        SELECT order_status, COUNT(*) as count
        FROM `tabFood Order`
        WHERE order_status NOT IN ('Delivered', 'Cancelled')
        AND docstatus = 1
        GROUP BY order_status
    """, as_dict=True)
    
    # Top Restaurants by Revenue
    top_restaurants = frappe.db.sql("""
        SELECT 
            restaurant,
            SUM(total_amount) as revenue,
            COUNT(*) as total_orders
        FROM `tabFood Order`
        WHERE order_status = 'Delivered'
        AND docstatus = 1
        GROUP BY restaurant
        ORDER BY revenue DESC
        LIMIT 5
    """, as_dict=True)
    
    # Recent Orders
    recent_orders = frappe.get_all(
        "Food Order",
        fields=["name", "restaurant", "customer_name", "total_amount", "order_status", "order_date"],
        limit=10,
        order_by="order_date desc"
    )
    
    return {
        "today_stats": today_stats,
        "active_orders": active_orders,
        "top_restaurants": top_restaurants,
        "recent_orders": recent_orders
    }
