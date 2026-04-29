import frappe
from frappe.model.document import Document


class PaymentTransaction(Document):
    def validate(self):
        if self.amount <= 0:
            frappe.throw("Amount must be greater than 0")

    def on_submit(self):
        if self.status == "Success" and self.transaction_type == "Payment":
            # Update order payment status
            frappe.db.set_value("Food Order", self.order, "payment_status", "Paid")
            frappe.db.set_value("Food Order", self.order, "transaction_id", self.reference_id)
            
            # Submit the food order
            order = frappe.get_doc("Food Order", self.order)
            if order.docstatus == 0:
                order.submit()
        
        elif self.status == "Success" and self.transaction_type == "Refund":
            frappe.db.set_value("Food Order", self.order, "payment_status", "Refunded")
        
        frappe.db.commit()
