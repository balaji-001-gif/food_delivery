import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Agent ID",
            "fieldname": "agent_id",
            "fieldtype": "Link",
            "options": "Delivery Agent",
            "width": 130
        },
        {
            "label": "Agent Name",
            "fieldname": "agent_name",
            "fieldtype": "Data",
            "width": 160
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Total Deliveries",
            "fieldname": "total_deliveries",
            "fieldtype": "Int",
            "width": 140
        },
        {
            "label": "Successful Deliveries",
            "fieldname": "successful_deliveries",
            "fieldtype": "Int",
            "width": 170
        },
        {
            "label": "Avg Delivery Time (mins)",
            "fieldname": "avg_delivery_time",
            "fieldtype": "Float",
            "precision": 1,
            "width": 180
        },
        {
            "label": "Total Earnings (\u20b9)",
            "fieldname": "total_earnings",
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
            "label": "Vehicle Type",
            "fieldname": "vehicle_type",
            "fieldtype": "Data",
            "width": 130
        }
    ]


def get_data(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND DATE(fo.order_date) >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND DATE(fo.order_date) <= %(to_date)s"
    if filters.get("agent_status"):
        conditions += " AND da.status = %(agent_status)s"
    
    data = frappe.db.sql(f"""
        SELECT
            da.name as agent_id,
            da.agent_name,
            da.status,
            da.vehicle_type,
            da.average_rating as avg_rating,
            COUNT(fo.name) as total_deliveries,
            SUM(CASE WHEN fo.order_status = 'Delivered' THEN 1 ELSE 0 END) as successful_deliveries,
            AVG(
                CASE WHEN fo.order_status = 'Delivered' AND fo.actual_delivery_time IS NOT NULL
                THEN TIMESTAMPDIFF(MINUTE, fo.order_date, fo.actual_delivery_time)
                ELSE NULL END
            ) as avg_delivery_time,
            SUM(CASE WHEN fo.order_status = 'Delivered' THEN fo.delivery_charge ELSE 0 END) as total_earnings
        FROM `tabDelivery Agent` da
        LEFT JOIN `tabFood Order` fo ON fo.delivery_agent = da.name
        {('AND ' + conditions[5:]) if conditions else ''}
        GROUP BY da.name
        ORDER BY successful_deliveries DESC
    """, filters, as_dict=True)
    
    return data
