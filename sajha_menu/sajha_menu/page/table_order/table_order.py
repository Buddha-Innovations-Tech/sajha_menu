import frappe
from datetime import datetime
# from jinja2 import Template


# def clever_function():
#     return "Hello"


# template = Template("{{clever_function}}")
# template.globals['clever_function'] = clever_function


@frappe.whitelist(allow_guest=True)
def getTableName():
    names = []
    table_name = frappe.get_list("Tables", fields=['name'])
    for name in table_name:
        names.append(name['name'])
    return names


@frappe.whitelist()
def getBodyHTML():

    table_order = frappe.db.get_list("Tables")
    tableData = []
    for to in table_order:
        tables = frappe.get_doc("Tables", to.name)
        tableData.append(
            {"name": tables.name, "totalOrder": len(tables.orders), "currentOrder": len(tables.current_orders)})
    return frappe.render_template('sajha_menu/page/templates/tables.html', {'tables': tableData})


@frappe.whitelist()
def on_update():
    frappe.publish_realtime("kot_bot_refresh")


@frappe.whitelist()
def applyFilter(company):

    if company == "" or company == None:
        table_order = frappe.db.get_list("Tables")
    else:
        table_order = frappe.db.get_list("Tables", filters=[
            ['company', 'like', company]]
        )

    tableData = []
    for to in table_order:
        tables = frappe.get_doc("Tables", to.name)

        tableData.append(
            {"name": tables.name, "totalOrder": len(tables.orders), "currentOrder": len(tables.current_orders)})
    return frappe.render_template('sajha_menu/page/templates/tables.html', {'tables': tableData})


@frappe.whitelist()
def getCompanyList():
    names = []
    company = frappe.get_list("Company", fields=['name'])
    print(company)
    for name in company:
        names.append(name['name'])
    return names


@frappe.whitelist()
def refreshKot(company):
    if company == "" or company == None:
        table_order = frappe.db.get_list("Tables")
    else:
        table_order = frappe.db.get_list(
            "Tables", filters=[['company', 'like', company]])

    tableData = []
    for to in table_order:
        tables = frappe.get_doc("Tables", to.name)
        tableData.append(
            {"name": tables.name, "totalOrder": len(tables.orders), "currentOrder": len(tables.current_orders)})
    return frappe.render_template('sajha_menu/page/templates/tables.html', {'tables': tableData})
