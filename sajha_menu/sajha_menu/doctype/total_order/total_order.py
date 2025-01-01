# Copyright (c) 2023, tuna and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TotalOrder(Document):
    def on_trash():
        frappe.throw("Deleteing not allowed")
    pass
