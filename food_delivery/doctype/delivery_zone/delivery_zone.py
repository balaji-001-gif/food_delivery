import frappe
from frappe.model.document import Document


class DeliveryZone(Document):
    def validate(self):
        self.validate_pincodes()

    def validate_pincodes(self):
        if self.pincode_list:
            pincodes = [p.strip() for p in self.pincode_list.split(",")]
            for pincode in pincodes:
                if not pincode.isdigit() or len(pincode) != 6:
                    frappe.throw(f"Invalid pincode: {pincode}. Pincode must be 6 digits.")

    def get_pincodes(self):
        if self.pincode_list:
            return [p.strip() for p in self.pincode_list.split(",")]
        return []

    def is_pincode_in_zone(self, pincode):
        return pincode in self.get_pincodes()


@frappe.whitelist()
def get_zone_for_pincode(pincode):
    """Get delivery zone for given pincode"""
    zones = frappe.get_all(
        "Delivery Zone",
        filters={"is_active": 1},
        fields=["name", "zone_name", "delivery_charge", "pincode_list"]
    )
    
    for zone in zones:
        pincodes = [p.strip() for p in (zone.pincode_list or "").split(",")]
        if pincode in pincodes:
            return zone
    
    return None
