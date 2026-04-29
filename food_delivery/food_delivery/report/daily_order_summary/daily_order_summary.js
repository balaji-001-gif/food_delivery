frappe.query_reports["Daily Order Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"reqd": 1
		},
		{
			"fieldname": "restaurant",
			"label": __("Restaurant"),
			"fieldtype": "Link",
			"options": "Restaurant"
		},
		{
			"fieldname": "order_status",
			"label": __("Order Status"),
			"fieldtype": "Select",
			"options": "\nPending\nConfirmed\nPreparing\nReady for Pickup\nOut for Delivery\nDelivered\nCancelled"
		}
	]
};
