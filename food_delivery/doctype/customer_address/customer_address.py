import frappe
from frappe.model.document import Document


class CustomerAddress(Document):
    def validate(self):
        self.validate_pincode()

    def validate_pincode(self):
        if self.pincode and not self.pincode.isdigit():
            frappe.throw("Invalid pincode")

    def before_save(self):
        if self.is_default:
            # Remove default from other addresses
            frappe.db.sql("""
                UPDATE `tabCustomer Address`
                SET is_default = 0
                WHERE customer = %s AND name != %s
            """, (self.customer, self.name))
