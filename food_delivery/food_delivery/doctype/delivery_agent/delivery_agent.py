import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate


class DeliveryAgent(Document):
    def validate(self):
        self.validate_vehicle()

    def validate_vehicle(self):
        if self.vehicle_number:
            self.vehicle_number = self.vehicle_number.upper().replace(" ", "")

    def update_location(self, latitude, longitude):
        """Update agent's current location"""
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.last_location_update = now_datetime()
        self.save(ignore_permissions=True)

    def set_available(self):
        self.status = "Available"
        self.save(ignore_permissions=True)

    def set_busy(self):
        self.status = "Busy"
        self.save(ignore_permissions=True)

    def get_active_order(self):
        """Get current active order"""
        return frappe.db.get_value(
            "Food Order",
            {
                "delivery_agent": self.name,
                "order_status": ["in", ["Out for Delivery", "Ready for Pickup"]]
            },
            "name"
        )


@frappe.whitelist()
def get_available_agents(zone=None, latitude=None, longitude=None):
    """Get available delivery agents"""
    filters = {"status": "Available"}
    if zone:
        filters["assigned_zone"] = zone
    
    agents = frappe.get_all(
        "Delivery Agent",
        filters=filters,
        fields=["name", "agent_name", "phone", "current_latitude", 
               "current_longitude", "vehicle_type", "average_rating"]
    )
    
    if latitude and longitude:
        from food_delivery.food_delivery.utils.helpers import calculate_distance
        for agent in agents:
            if agent.current_latitude and agent.current_longitude:
                agent["distance"] = calculate_distance(
                    float(latitude), float(longitude),
                    float(agent.current_latitude), float(agent.current_longitude)
                )
        agents.sort(key=lambda x: x.get("distance", float("inf")))
    
    return agents


@frappe.whitelist()
def update_agent_location(agent_name, latitude, longitude):
    """Update delivery agent location"""
    agent = frappe.get_doc("Delivery Agent", agent_name)
    agent.update_location(latitude, longitude)
    return {"success": True}


@frappe.whitelist()
def assign_order_to_agent(order_name, agent_name):
    """Assign order to delivery agent"""
    order = frappe.get_doc("Food Order", order_name)
    agent = frappe.get_doc("Delivery Agent", agent_name)
    
    if agent.status != "Available":
        frappe.throw("Agent is not available")
    
    order.delivery_agent = agent_name
    order.save(ignore_permissions=True)
    
    agent.set_busy()
    
    return {"success": True}


def update_agent_status():
    """Scheduled: Update agents who haven't updated location in 1 hour"""
    frappe.db.sql("""
        UPDATE `tabDelivery Agent`
        SET status = 'Offline'
        WHERE status = 'Available'
        AND TIMESTAMPDIFF(HOUR, last_location_update, NOW()) >= 1
    """)
    frappe.db.commit()


@frappe.whitelist()
def generate_agent_performance_report():
    """Generate agent performance report (Scheduled Task placeholder)"""
    pass

