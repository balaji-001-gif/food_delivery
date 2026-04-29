import frappe


@frappe.whitelist(allow_guest=True)
def get_restaurants(city=None, cuisine=None, sort_by="rating", page=1, page_size=10):
    """Get list of restaurants"""
    filters = {"status": "Active"}
    
    if city:
        filters["city"] = city
    
    if cuisine:
        filters["cuisine_type"] = ["like", f"%{cuisine}%"]
    
    order_by_map = {
        "rating": "average_rating DESC",
        "orders": "total_orders DESC",
        "delivery_time": "delivery_time ASC",
        "name": "restaurant_name ASC"
    }
    
    order_by = order_by_map.get(sort_by, "average_rating DESC")
    
    total = frappe.db.count("Restaurant", filters)
    
    restaurants = frappe.get_all(
        "Restaurant",
        filters=filters,
        fields=[
            "name", "restaurant_name", "logo", "banner_image",
            "average_rating", "total_reviews", "total_orders",
            "delivery_charge", "preparation_time", "delivery_time",
            "minimum_order_amount", "cuisine_type", "is_featured",
            "opening_time", "closing_time", "city", "address_line1"
        ],
        order_by=order_by,
        limit=int(page_size),
        start=(int(page) - 1) * int(page_size)
    )
    
    return {
        "restaurants": restaurants,
        "total": total,
        "page": int(page),
        "page_size": int(page_size)
    }


@frappe.whitelist(allow_guest=True)
def get_restaurant_menu(restaurant_name):
    """Get complete restaurant menu"""
    from food_delivery.doctype.restaurant.restaurant import get_restaurant_details
    return get_restaurant_details(restaurant_name)


@frappe.whitelist(allow_guest=True)
def search_restaurants(query, city=None):
    """Search restaurants by name or cuisine"""
    filters = {"status": "Active"}
    if city:
        filters["city"] = city
    
    restaurants = frappe.get_all(
        "Restaurant",
        filters=filters,
        or_filters={
            "restaurant_name": ["like", f"%{query}%"],
            "cuisine_type": ["like", f"%{query}%"],
            "city": ["like", f"%{query}%"]
        },
        fields=[
            "name", "restaurant_name", "logo", "average_rating",
            "delivery_charge", "delivery_time", "cuisine_type", "city"
        ],
        limit=20
    )
    return restaurants


@frappe.whitelist(allow_guest=True)
def get_featured_restaurants(city=None):
    """Get featured restaurants"""
    filters = {"status": "Active", "is_featured": 1}
    if city:
        filters["city"] = city
    
    return frappe.get_all(
        "Restaurant",
        filters=filters,
        fields=[
            "name", "restaurant_name", "logo", "banner_image",
            "average_rating", "delivery_charge", "delivery_time", "cuisine_type"
        ],
        limit=10
    )


@frappe.whitelist(allow_guest=True)
def get_cuisines():
    """Get all available cuisines"""
    cuisines = frappe.db.sql("""
        SELECT DISTINCT cuisine_type
        FROM `tabRestaurant`
        WHERE status = 'Active'
        AND cuisine_type IS NOT NULL
        AND cuisine_type != ''
    """, as_dict=True)
    
    all_cuisines = set()
    for r in cuisines:
        if r.cuisine_type:
            for cuisine in r.cuisine_type.split(","):
                all_cuisines.add(cuisine.strip())
    
    return sorted(list(all_cuisines))
