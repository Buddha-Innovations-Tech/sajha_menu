import frappe

def create_custom_perm():
    doc = frappe.db.sql("SELECT * FROM `tabCustomer` WHERE name = 'Sajha Customer'", as_dict=1)
    if len(doc) == 0:
        customer = frappe.new_doc("Customer")
        customer.customer_name= "Sajha Customer"
        customer.Territory= "All Territories"
        customer.customer_type= "Individual"
        customer.customer_group= "Individual"
        customer.save()

    ROLE = "Sajha Front"
    LEVEL = 0

    sajha_front_perm_list = [
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Territory",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Stock Entry",
            'select':1,
            'read':1,
            'write':1,
            'create':1,
            'delete':0,
            'submit':1,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Payment Entry",
            'select':1,
            'read':1,
            'write':1,
            'create':1,
            'delete':0,
            'submit':1,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Naming Series",
            'select':0,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Mode of Payment",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Item Tax Template",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Item Price",
            'select':1,
            'read':1,
            'write':1,
            'create':1,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Item",
            'select':1,
            'read':1,
            'write':1,
            'create':1,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Gender",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "GL Entry",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Fiscal Year",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Customer Group",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Customer",
            'select':1,
            'read':1,
            'write':0,
            'create':1,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Currency",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Country",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Bank Account",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Bank",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Contact",
            'select':1,
            'read':1,
            'write':1,
            'create':1,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Address",
            'select':1,
            'read':1,
            'write':1,
            'create':1,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Account",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Sales Invoice",
            'select':1,
            'read':1,
            'write':1,
            'create':1,
            'delete':0,
            'submit':1,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Sales Order",
            'select':1,
            'read':1,
            'write':1,
            'create':1,
            'delete':0,
            'submit':1,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Company",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
    ]

    create_new_doc_perm(permission_list=sajha_front_perm_list, role= ROLE)


    ROLE = "Waiter"
    LEVEL = 0
    waiter_perm_list = [
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Item Price",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Access Log",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Item",
            'select':1,
            'read':1,
            'write':0,
            'create':0,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
        {
            'role': ROLE,
            'level': LEVEL,
            'parent': "Stock Entry",
            'select':1,
            'read':1,
            'write':1,
            'create':1,
            'delete':0,
            'submit':0,
            'cancel':0,
            'amend':0,
            'print': 1,
        },
    ]

    create_new_doc_perm(permission_list= waiter_perm_list, role= ROLE)


def create_new_doc_perm(permission_list, role):
    for perm in permission_list:
        exists = frappe.db.get_value("Custom DocPerm", {'parent':perm.get("parent"), "role": role}, 'name')
        if exists is None:
            perm_doc = frappe.new_doc("Custom DocPerm")
            perm_doc.role = perm.get("role")
            perm_doc.permlevel = perm.get("level")
            perm_doc.parent = perm.get("parent")
            perm_doc.select = perm.get("select")
            perm_doc.read = perm.get("read")
            perm_doc.write = perm.get("write")
            perm_doc.create = perm.get("create")
            perm_doc.delete = perm.get("delete")
            perm_doc.submit = perm.get("submit")
            perm_doc.cancel = perm.get("cancel")
            perm_doc.amend = perm.get("amend")
            perm_doc.print = perm.get("print")

            perm_doc.save(ignore_permissions=True)