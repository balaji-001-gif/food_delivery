app_name = "food_delivery"
app_title = "Food Delivery"
app_publisher = "Your Company"
app_description = "Food Delivery Application like Swiggy"
app_email = "admin@yourcompany.com"
app_license = "MIT"
app_version = "1.0.0"

# Include JS and CSS files in header of desk.html
app_include_css = [
    "/assets/food_delivery/css/food_delivery.css",
    "/assets/food_delivery/css/dashboard.css"
]

app_include_js = [
    "/assets/food_delivery/js/food_delivery.js"
]

# Web Include
web_include_css = [
    "/assets/food_delivery/css/web_food_delivery.css"
]

web_include_js = [
    "/assets/food_delivery/js/web_food_delivery.js"
]

# Fixtures
fixtures = [
    "Food Delivery Settings",
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Food Delivery"]]
    }
]

# Document Events
doc_events = {
    "Food Order": {
        "on_submit": "food_delivery.doctype.food_order.food_order.on_submit",
        "on_cancel": "food_delivery.doctype.food_order.food_order.on_cancel",
        "after_insert": "food_delivery.doctype.food_order.food_order.after_insert",
    },
    "Payment Transaction": {
        "on_submit": "food_delivery.doctype.payment_transaction.payment_transaction.on_submit",
    }
}

# Scheduled Tasks
scheduler_events = {
    "cron": {
        "*/5 * * * *": [
            "food_delivery.doctype.food_order.food_order.update_order_status",
        ],
        "0 0 * * *": [
            "food_delivery.doctype.restaurant.restaurant.reset_daily_stats",
        ],
    },
    "daily": [
        "food_delivery.doctype.coupon_code.coupon_code.expire_coupons",
    ],
    "hourly": [
        "food_delivery.doctype.delivery_agent.delivery_agent.update_agent_status",
    ]
}

# Website Route Rules
website_route_rules = [
    {"from_route": "/restaurants", "to_route": "restaurant"},
    {"from_route": "/restaurants/<name>", "to_route": "restaurant_detail"},
    {"from_route": "/order/<name>", "to_route": "order_tracking"},
]

# Permissions
permission_query_conditions = {
    "Food Order": "food_delivery.doctype.food_order.food_order.get_permission_query_conditions",
    "Restaurant": "food_delivery.doctype.restaurant.restaurant.get_permission_query_conditions",
}

has_permission = {
    "Food Order": "food_delivery.doctype.food_order.food_order.has_permission",
}

# On Login
on_login = "food_delivery.api.customer.on_login"

# Jinja Environments
jinja = {
    "methods": [
        "food_delivery.utils.helpers.format_currency",
        "food_delivery.utils.helpers.get_rating_stars",
    ]
}

