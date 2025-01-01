# Copyright (c) 2023, tuna and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ItemCategory(Document):
    def before_save(doc):
        for i in range(0, len(doc.items)):
            itemTax = frappe.get_doc("Item", doc.items[i].item_code)
            taxTemplate = None
            taxRate = 0.0
            if len(itemTax.taxes) > 0:
                taxTemplate = itemTax.taxes[0].item_tax_template

                dataTax = frappe.get_doc("Item Tax Template Detail", {
                    "parent": f"{taxTemplate}"})
                taxRate = dataTax.get("tax_rate")
            company = itemTax.get('item_defaults')[0].company
            doc.items[i].company = company
            doc.items[i].tax = doc.items[i].rate * (taxRate/100)
            doc.items[i].parent_name = doc.name
