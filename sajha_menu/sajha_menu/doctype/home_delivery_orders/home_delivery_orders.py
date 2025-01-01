# Copyright (c) 2023, tuna and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from datetime import datetime


class HomeDeliveryOrders(Document):
    pass


@frappe.whitelist()
def ConfirmOrder(doc):
    doc = json.loads(doc)
    order = frappe.get_doc("Home Delivery Orders", doc['name'])
    order.status = "Order Confirmed"
    order.save()
    return True


@frappe.whitelist()
def MarkAsDelivered(doc):
    doc = json.loads(doc)
    order = frappe.get_doc("Home Delivery Orders", doc['name'])
    order.status = "Order Delivered"
    order.save()
    return True


@frappe.whitelist()
def CancelOrder(doc):
    doc = json.loads(doc)
    order = frappe.get_doc("Home Delivery Orders", doc['name'])
    order.status = "Order Cancelled"
    order.save()
    return True


def create_kot_order(order_number, orderItem, company):
    count = frappe.db.count("Kitchen Orders", filters={"company": company})
    if (count > 0):
        last_doc = frappe.get_last_doc(
            "Kitchen Orders", filters={"company": company})
        if last_doc.created_date < datetime.now().date():
            kot_id = 1
        else:
            kot_id = int(last_doc.get("kot_id")) + 1
    else:
        kot_id = 1

    created_date = datetime.now().date()

    doc = frappe.get_doc({"doctype": "Kitchen Orders",
                          "order_number": order_number, "kot_id": kot_id, "items": orderItem, "company": company, "created_date": created_date})
    doc.insert()
    return doc


@frappe.whitelist()
def getLastKotBotNumber(company):
    kotCount = frappe.db.count("Kitchen Orders", filters={"company": company})
    if (kotCount > 0):
        last_doc = frappe.get_last_doc(
            "Kitchen Orders", filters={"company": company})
        if last_doc.created_date < datetime.now().date():
            kot_id = 1
        else:
            kot_id = int(last_doc.get("kot_id")) + 1
    else:
        kot_id = 1

    barCount = frappe.db.count("Bar Orders", filters={"company": company})
    if (barCount > 0):
        last_doc = frappe.get_last_doc(
            "Bar Orders", filters={"company": company})
        if last_doc.created_date < datetime.now().date():
            bot_id = 1
        else:
            bot_id = int(last_doc.get("bot_id")) + 1
    else:
        bot_id = 1

    frappe.local.response['data'] = {"kotId": kot_id, "botId": bot_id}


# Create BOT order
# ROLE: WAITER ONLY
def create_bot_order(order_number, orderItem, company):

    count = frappe.db.count("Bar Orders", filters={"company": company})
    if (count > 0):
        last_doc = frappe.get_last_doc(
            "Bar Orders", filters={"company": company})
        if last_doc.created_date < datetime.now().date():
            bot_id = 1
        else:
            bot_id = int(last_doc.get("bot_id")) + 1
    else:
        bot_id = 1

    created_date = datetime.now().date()
    doc = frappe.get_doc(
        {"doctype": "Bar Orders", "order_number": order_number, "bot_id": bot_id, "items": orderItem, "company": company, 'created_date': created_date})
    doc.insert()
    return doc


# CREATE ORDER
@frappe.whitelist()
def create_kot_or_bot_order(order_number, orderItem, company):
    orderItem = json.loads(orderItem)
    foodItem = []
    barItem = []
    kotid = 1
    botid = 1

    for item in orderItem:
        sub_item = frappe.db.get_value(
            'Sub Category Items', {'item_code': f"{item['item_code']}"}, ['parent'])
        sub_child = frappe.db.get_value(
            'Item Category Child', {'item_category': sub_item}, ['parent'])
        sub_cat = frappe.db.get_value(
            'Super Sub Category Child', {'ssc_name': sub_child}, ['parent'])

        cat = frappe.db.get_value("Sub Category Child", {
            'sub_category': sub_cat}, ['parent'])
        type = frappe.db.get_value("Category", {'name': cat}, ['type'])

        if type == "Bar":
            barItem.append(item)
        else:
            foodItem.append(item)

    if len(foodItem) > 0:
        kot = create_kot_order(order_number, foodItem, company)
        kotid = kot.kot_id

    if len(barItem) > 0:
        bot = create_bot_order(order_number, barItem, company)
        botid = bot.bot_id

    orderdoc = frappe.get_doc("Home Delivery Orders", order_number)

    orderdoc.ticket_created = True

    orderdoc.save()

    # topic = str(company).replace(" ", "-").lower()
    # push_service.notify_topic_subscribers(
    #     topic_name=topic, message_title="New Order", message_body=f"Order from {table_name}")

    frappe.publish_realtime('kot_bot_refresh')

    frappe.local.response['data'] = {
        "kot_id": kotid,
        "bot_id": botid
    }


@frappe.whitelist()
def createSalesInvoice(doc):
    doc = json.loads(doc)
    if doc.get("name"):
        orders = []
        orderItems = doc['delivery_items']

        for o in orderItems:
            item = frappe.db.get_value("Item Price", {'item_code': o['item_code'], 'selling': 1}, [
                'name', 'item_code', 'price_list_rate', 'item_name', 'uom',], as_dict=True)
            itemtax = frappe.get_doc("Item", o['item_code'])
            taxTemplate = None
            if len(itemtax.taxes) > 0:
                taxTemplate = itemtax.taxes[0].item_tax_template
            orders.append({
                'item_code': item['item_code'],
                'item_name': item['item_name'],
                'qty': o['quantity'],
                'rate': item['price_list_rate'],
                'amount': int(o['quantity']) * item['price_list_rate'],
                'uom': item['uom'],
                "description": "Test Description",
                'tax_template': taxTemplate
            })

        customer = frappe.get_doc("Customer", {"user": doc.get("email")})

        sales_invoice = frappe.new_doc('Sales Invoice')
        sales_invoice.customer = customer.customer_name
        sales_invoice.table_name = doc.get("name")
        sales_invoice.due_date = frappe.utils.nowdate()

        default_taxes_and_charges = frappe.db.get_value("Sales Taxes and Charges Template", {
            "company": doc.get('company'), "is_default": 1})
        default_incm_account = frappe.db.get_value(
            "Company", {"name": doc.get("company")}, ['default_income_account'])
        default_cost_center = frappe.db.get_value(
            "Company", {"name": doc.get("company")}, ['cost_center'])

        sales_invoice.taxes_and_charges = default_taxes_and_charges

        company = frappe.get_doc("Company", doc.get('company'))

        sales_charges = sales_invoice.append('taxes', {})
        sales_charges.charge_type = "On Net Total"
        sales_charges.account_head = f"VAT - {company.abbr}"

        for o in orders:
            if int(o['qty']) > 0:
                default_account = None
                itemAccount = frappe.get_doc("Item", o['item_code'])
                for itm in itemAccount.item_defaults:
                    if doc.get('company') == itm.company:
                        default_account = itm.income_account
                        break
                sales_invoice_itm = sales_invoice.append('items', {})
                sales_invoice_itm.item_code = o['item_code']
                sales_invoice_itm.item_name = o['item_name']
                sales_invoice_itm.description = o['description']
                sales_invoice_itm.uom = o['uom']
                sales_invoice_itm.qty = int(o['qty'])
                if o['tax_template'] != None:
                    sales_invoice_itm.item_tax_template = o['tax_template']
                sales_invoice_itm.cost_center = default_cost_center
                if default_account != None:
                    sales_invoice_itm.income_account = default_account
                else:
                    sales_invoice_itm.income_account = default_incm_account

        sales_invoice.insert(ignore_permissions=True, ignore_links=True,
                             ignore_if_duplicate=True, ignore_mandatory=True)

        order = frappe.get_doc("Home Delivery Orders", doc.get('name'))
        order.sales_invoice_reference = sales_invoice.name
        order.save()

        return sales_invoice.name
