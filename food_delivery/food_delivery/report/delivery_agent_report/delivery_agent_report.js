frappe.query_reports["Delivery Agent Report"] = {
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
			"fieldname": "agent_status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nAvailable\nBusy\nOffline"
		}
	]
};
