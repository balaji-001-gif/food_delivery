import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart


def get_columns():
    return [
        {
            "label": "Date",
            "fieldname": "order_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "Restaurant",
            "fieldname": "restaurant",
            "fieldtype": "Link",
            "options": "Restaurant",
            "width": 200
        },
        {
            "label": "Total Orders",
            "fieldname": "total_orders",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "Delivered",
            "fieldname": "delivered_orders",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "Cancelled",
            "fieldname": "cancelled_orders",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "Total Revenue (\u20b9)",
            "fieldname": "total_revenue",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Avg Order Value (\u20b9)",
            "fieldname": "avg_order_value",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Total Tax (\u20b9)",
            "fieldname": "total_tax",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "Delivery Charges (\u20b9)",
            "fieldname": "total_delivery_charges",
            "fieldtype": "Currency",
            "width": 150
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT
            DATE(fo.order_date) as order_date,
            fo.restaurant,
            COUNT(*) as total_orders,
            SUM(CASE WHEN fo.order_status = 'Delivered' THEN 1 ELSE 0 END) as delivered_orders,
            SUM(CASE WHEN fo.order_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_orders,
            SUM(CASE WHEN fo.order_status = 'Delivered' THEN fo.total_amount ELSE 0 END) as total_revenue,
            AVG(CASE WHEN fo.order_status = 'Delivered' THEN fo.total_amount ELSE NULL END) as avg_order_value,
            SUM(CASE WHEN fo.order_status = 'Delivered' THEN fo.tax_amount ELSE 0 END) as total_tax,
            SUM(CASE WHEN fo.order_status = 'Delivered' THEN fo.delivery_charge ELSE 0 END) as total_delivery_charges
        FROM `tabFood Order` fo
        WHERE fo.docstatus = 1
        {conditions}
        GROUP BY DATE(fo.order_date), fo.restaurant
        ORDER BY order_date DESC, total_revenue DESC
    """, filters, as_dict=True)
    
    return data


def get_conditions(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND DATE(fo.order_date) >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND DATE(fo.order_date) <= %(to_date)s"
    
    if filters.get("restaurant"):
        conditions += " AND fo.restaurant = %(restaurant)s"
    
    if filters.get("order_status"):
        conditions += " AND fo.order_status = %(order_status)s"
    
    return conditions


def get_chart(data):
    if not data:
        return None
    
    # Group by date
    dates = []
    revenues = []
    orders = []
    
    date_data = {}
    for row in data:
        date_str = str(row.order_date)
        if date_str not in date_data:
            date_data[date_str] = {"revenue": 0, "orders": 0}
        date_data[date_str]["revenue"] += flt(row.total_revenue)
        date_data[date_str]["orders"] += row.total_orders
    
    for date, values in sorted(date_data.items()):
        dates.append(date)
        revenues.append(values["revenue"])
        orders.append(values["orders"])
    
    return {
        "data": {
            "labels": dates,
            "datasets": [
                {
                    "name": "Revenue (\u20b9)",
                    "values": revenues,
                    "chartType": "bar"
                },
                {
                    "name": "Total Orders",
                    "values": orders,
                    "chartType": "line"
                }
            ]
        },
        "type": "axis-mixed",
        "colors": ["#5e64ff", "#ff5e5e"]
    }
