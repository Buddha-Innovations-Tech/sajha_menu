import frappe
import json


@frappe.whitelist()
def replace_name(doc):
    doc = json.loads(doc)
    sli = frappe.get_doc("Sales Invoice", doc['name'])
    sli.menu = doc['menu']
    for item in sli.items:
        it = frappe.db.get_value("Item", item.item_code, "dummy_name")
        item.menu_name = it if doc['menu'] == 1 else ""
    sli.save()
    return "OK"
