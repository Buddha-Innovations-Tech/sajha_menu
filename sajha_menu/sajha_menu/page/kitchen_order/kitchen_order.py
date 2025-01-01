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
def getBodyHTML(fromDate, toDate):
    fromDate = datetime.strptime(fromDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    fromDate = datetime.strptime(fromDate, '%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%d-%m-%Y')
    theme = frappe.db.get_value("User", frappe.session.user, "desk_theme")

    kot_order = frappe.db.get_list("Kitchen Orders", filters=[
                                   ['created_date', 'between', [fromDate, toDate]]])
    kotData = []
    for kot in kot_order:
        active = 0
        done = 0
        orders = frappe.get_doc("Kitchen Orders", kot.name)
        for order in orders.items:
            if order.order_status == 0:
                active = active + 1
            else:
                done = done + 1

        kotData.append(
            {"name": orders.table_name, 'kot_status': orders.kot_status, "status": orders.status, "activeOrder": active, "doneOrder": done, "totalOrder": len(orders.items), "kot_number": orders.kot_id, "kot_name": kot.name})
    return frappe.render_template('sajha_menu/page/templates/body.html', {'kots': kotData, "theme": theme})


@frappe.whitelist()
def on_update():
    frappe.publish_realtime("kot_bot_refresh")


@frappe.whitelist()
def applyFilter(company, fromDate, toDate, status):
    if status == "":
        status = None

    fromDate = datetime.strptime(fromDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    fromDate = datetime.strptime(fromDate, '%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%d-%m-%Y')
    theme = frappe.db.get_value("User", frappe.session.user, "desk_theme")
    if company == "" or company == None:
        kot_order = frappe.db.get_list("Kitchen Orders", filters=[
            ['created_date', 'between', [fromDate, toDate]], ['status', '=', status]])
    else:
        kot_order = frappe.db.get_list("Kitchen Orders", filters=[
            ['created_date', 'between', [fromDate, toDate]], [
                'company', 'like', company], ['status', '=', status]
        ]
        )

    kotData = []
    for kot in kot_order:
        active = 0
        done = 0
        orders = frappe.get_doc("Kitchen Orders", kot.name)
        for order in orders.items:
            if order.order_status == 0:
                active = active + 1
            else:
                done = done + 1

        kotData.append(
            {"name": orders.table_name, 'kot_status': orders.kot_status, "status": orders.status, "activeOrder": active, "doneOrder": done, "totalOrder": len(orders.items), "kot_number": orders.kot_id, "kot_name": kot.name})
    return frappe.render_template('sajha_menu/page/templates/body.html', {'kots': kotData, 'theme': theme})


@frappe.whitelist()
def getCompanyList():
    names = []
    company = frappe.get_list("Company", fields=['name'])
    for name in company:
        names.append(name['name'])
    return names


@frappe.whitelist()
def refreshKot(company, fromDate, toDate, status):
    if status == "":
        status = None

    fromDate = datetime.strptime(fromDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    fromDate = datetime.strptime(fromDate, '%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%d-%m-%Y')
    theme = frappe.db.get_value("User", frappe.session.user, "desk_theme")
    if company == "" or company == None:
        kot_order = frappe.db.get_list("Kitchen Orders", filters=[
            ['created_date', 'between', [fromDate, toDate]], ['status', '=', status]])
    else:
        kot_order = frappe.db.get_list("Kitchen Orders", filters=[
            ['created_date', 'between', [fromDate, toDate]], ['company', 'like', company], ['status', '=', status]])

    kotData = []
    for kot in kot_order:
        active = 0
        done = 0
        orders = frappe.get_doc("Kitchen Orders", kot.name)
        for order in orders.items:
            if order.order_status == 0:
                active = active + 1
            else:
                done = done + 1

        kotData.append(
            {"name": orders.table_name, 'kot_status': orders.kot_status, "status": orders.status, "activeOrder": active, "doneOrder": done, "totalOrder": len(orders.items), "kot_number": orders.kot_id, "kot_name": kot.name})
    return frappe.render_template('sajha_menu/page/templates/body.html', {'kots': kotData, 'theme': theme})
