import frappe
from datetime import datetime
# from jinja2 import Template


# def clever_function():
#     return "Hello"


# template = Template("{{clever_function}}")
# template.globals['clever_function'] = clever_function


@frappe.whitelist(allow_guest=True)
def getTableName():
    table_name = frappe.db.sql("""SELECT name from `tabTables`""")
    return table_name


@frappe.whitelist()
def getBodyHTML(fromDate, toDate):
    fromDate = datetime.strptime(fromDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    fromDate = datetime.strptime(fromDate, '%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%d-%m-%Y')

    bot_order = frappe.db.get_list("Bar Orders", filters=[
                                   ['created_date', 'between', [fromDate, toDate]]])

    botData = []
    for bot in bot_order:
        active = 0
        done = 0
        orders = frappe.get_doc("Bar Orders", bot.name)
        for order in orders.items:
            if order.order_status == 0:
                active = active + 1
            else:
                done = done + 1

        botData.append(
            {"name": orders.table_name, 'bot_status': orders.bot_status, "status": orders.status, "activeOrder": active, "doneOrder": done, "totalOrder": len(orders.items), "bot_number": orders.bot_id, "bot_name": bot.name})
    return frappe.render_template('sajha_menu/page/templates/bot_orders.html', {'bots': botData})


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

    if company == "":
        bot_order = frappe.db.get_list("Bar Orders", filters=[
            ['created_date', 'between', [fromDate, toDate]], ['status', '=', status]])
    else:
        bot_order = frappe.db.get_list("Bar Orders", filters=[
            ['created_date', 'between', [fromDate, toDate]], ['company', 'like', company], ['status', '=', status]])

    botData = []
    for bot in bot_order:
        active = 0
        done = 0
        orders = frappe.get_doc("Bar Orders", bot.name)
        for order in orders.items:
            if order.order_status == 0:
                active = active + 1
            else:
                done = done + 1

        botData.append(
            {"name": orders.table_name, 'bot_status': orders.bot_status, "status": orders.status, "activeOrder": active, "doneOrder": done, "totalOrder": len(orders.items), "bot_number": orders.bot_id, "bot_name": bot.name})
    return frappe.render_template('sajha_menu/page/templates/bot_orders.html', {'bots': botData})


@frappe.whitelist()
def getCompanyList():
    names = []
    company = frappe.get_list("Company", fields=['name'])
    print(company)
    for name in company:
        names.append(name['name'])
    return names


@frappe.whitelist()
def refreshKot(company, fromDate, toDate, status):
    fromDate = datetime.strptime(fromDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    fromDate = datetime.strptime(fromDate, '%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%Y-%m-%d').strftime('%d-%m-%Y')
    toDate = datetime.strptime(toDate, '%d-%m-%Y')

    if company == "" or company == None:
        bot_order = frappe.db.get_list("Bar Orders", filters=[
            ['created_date', 'between', [fromDate, toDate]], ['status', '=', status]])
    else:
        bot_order = frappe.db.get_list("Bar Orders", filters=[
            ['created_date', 'between', [fromDate, toDate]], ['company', 'like', company], ['status', '=', status]])

    botData = []
    for bot in bot_order:
        active = 0
        done = 0
        orders = frappe.get_doc("Bar Orders", bot.name)
        for order in orders.items:
            if order.order_status == 0:
                active = active + 1
            else:
                done = done + 1

        botData.append(
            {"name": orders.table_name, 'bot_status': orders.bot_status, "status": orders.status, "activeOrder": active, "doneOrder": done, "totalOrder": len(orders.items), "bot_number": orders.bot_id, "bot_name": bot.name})
    return frappe.render_template('sajha_menu/page/templates/bot_orders.html', {'bots': botData})
