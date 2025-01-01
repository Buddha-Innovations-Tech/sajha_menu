import frappe
import json

@frappe.whitelist()
def set_naming_series(doc):
    doc =json.loads(doc)
    company = doc['company'] 
    print(doc)
    com_doc = frappe.get_doc('Company',company)
    default_series = com_doc.default_series
    print(default_series)
    return default_series
