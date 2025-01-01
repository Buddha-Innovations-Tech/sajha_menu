# Copyright (c) 2022, tuna and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SubCategoryItems(Document):
    def on_change(self):
        itemCode = self.item_code
        doc = frappe.get_doc("Item Price", itemCode)
        print("here")
    pass
