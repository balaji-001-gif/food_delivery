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
            "label": "Restaurant",
            "fieldname": "restaurant",
            "fieldtype": "Link",
            "options": "Restaurant",
            "width": 200
        },
        {
            "label": "City",
            "fieldname": "city",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Total Orders",
            "fieldname": "total_orders",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "Completed Orders",
            "fieldname": "completed_orders",
            "fieldtype": "Int",
            "width": 140
        },
        {
            "label": "Cancelled Orders",
            "fieldname": "cancelled_orders",
            "fieldtype": "Int",
            "width": 140
        },
        {
            "label": "Completion Rate (%)",
            "fieldname": "completion_rate",
            "fieldtype": "Percent",
            "width": 150
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
            "label": "Avg Rating",
            "fieldname": "avg_rating",
            "fieldtype": "Float",
            "precision": 1,
            "width": 110
        },
        {
            "label": "Total Reviews",
            "fieldname": "total_reviews",
            "fieldtype": "Int",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND DATE(fo.order_date) >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND DATE(fo.order_date) <= %(to_date)s"
    if filters.get("city"):
        conditions += " AND r.city = %(city)s"
    
    data = frappe.db.sql(f"""
        SELECT
            fo.restaurant,
            r.city,
            COUNT(*) as total_orders,
            SUM(CASE WHEN fo.order_status = 'Delivered' THEN 1 ELSE 0 END) as completed_orders,
            SUM(CASE WHEN fo.order_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_orders,
            ROUND(
                (SUM(CASE WHEN fo.order_status = 'Delivered' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
                2
            ) as completion_rate,
            SUM(CASE WHEN fo.order_status = 'Delivered' THEN fo.total_amount ELSE 0 END) as total_revenue,
            AVG(CASE WHEN fo.order_status = 'Delivered' THEN fo.total_amount ELSE NULL END) as avg_order_value,
            r.average_rating as avg_rating,
            r.total_reviews
        FROM `tabFood Order` fo
        INNER JOIN `tabRestaurant` r ON r.name = fo.restaurant
        WHERE fo.docstatus = 1
        {conditions}
        GROUP BY fo.restaurant
        ORDER BY total_revenue DESC
    """, filters, as_dict=True)
    
    return data


def get_chart(data):
    if not data:
        return None
    
    labels = [d.restaurant for d in data[:10]]
    revenues = [flt(d.total_revenue) for d in data[:10]]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Revenue (\u20b9)",
                    "values": revenues,
                    "chartType": "bar"
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }
