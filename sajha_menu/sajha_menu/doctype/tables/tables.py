# Copyright (c) 2022, tuna and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import frappe.utils
import json
from frappe import _
from frappe.utils import flt
from datetime import datetime


class Tables(Document):
    def on_update(self):
        totalCharges = 0.00
        if len(self.get("orders")) > 0:
            for o in self.get("orders"):
                itemCategory = frappe.get_doc(
                    "Sub Category Items", {"item_code": o.item})
                totalCharges = totalCharges + \
                    (o.quantity * (itemCategory.rate))
            table = frappe.get_doc("Tables", self.get("name"))
            table.total_charges = totalCharges
            table.db_update()

        else:
            table = frappe.get_doc("Tables", self.get("name"))
            table.total_charges = 0.00
            table.db_update()


# @frappe.whitelist()
# def updateTotal(doc):
#     doc = json.loads(doc)
#     orders = doc.get('orders')
#     totalCharges = 0.00
#     if len(orders) > 0:
#         for o in orders:
#             item = frappe.db.get_value("Item Price", {'item_code': o['item'], 'selling': 1}, [
#                 'name', 'item_code', 'price_list_rate', 'item_name', 'uom',], as_dict=True)
#             totalCharges = totalCharges + \
#                 (o['quantity'] * item['price_list_rate'])
#         table = frappe.get_doc("Tables", doc.get("name"))
#         table.total_charges = totalCharges
#         table.db_update()
#         print(table.total_charges)
#         return table.total_charges
#     else:
#         table = frappe.get_doc("Tables", doc.get("name"))
#         table.total_charges = 0.00
#         table.db_update()
#         return table.total_charges

"""
This function validates the split bill details provided in the 'doc' parameter.

Parameters:
- doc (str): A JSON string representing the split bill details. It should contain the following keys:
    - split_bill (int): A flag indicating whether the bill is split or not.
    - split_bill_customer (list): A list of dictionaries representing the split bill customers. Each dictionary should contain the following keys:
        - bill_amount (float): The amount of the bill for the customer.

Returns:
- str: Returns 'no_customer' if there are no split bill customers provided. Returns 'mismatch' if the total bill amount of the split customers does not match the total charges. Returns 'ok' if the split bill details are valid.

Example:
    validate_split('{"split_bill": 1, "split_bill_customer": [{"bill_amount": 100}, {"bill_amount": 200}]}')
    # Returns 'ok'
"""
@frappe.whitelist()
def validate_split(doc):
    doc = json.loads(doc)
    if doc.get('split_bill'):
        if len(doc.get('split_bill_customer')) == 0:
            return 'no_customer'
        splitTotal = 0.00
        splitCustomer = doc.get('split_bill_customer')
        for sc in splitCustomer:

            if sc['bill_amount'] == None:
                sc['bill_amount'] = 0.00
            splitTotal = splitTotal + sc['bill_amount']

        if splitTotal != doc.get('total_charges'):
            return 'mismatch'
        else:
            return 'ok'

"""
Create sales invoice based on the provided document and index.

Parameters:
- doc (str): A JSON string representing the document containing the sales details. It should contain the following keys:
    - name (str): The name of the document.
    - split_bill_customer (list): A list of dictionaries representing the split bill customers. Each dictionary should contain the following keys:
        - customer (str): The name of the customer.
        - bill_amount (float): The amount of the bill for the customer.
    - total_charges (float): The total charges for the bill.
    - orders (list): A list of dictionaries representing the order items. Each dictionary should contain the following keys:
        - item (str): The item code.
        - quantity (float): The quantity of the item.
    - kot_bot (list): A list of dictionaries representing the KOT/BOT details. Each dictionary should contain the following keys:
        - ticket_number (str): The ticket number.
        - ticket_name (str): The ticket name.
- index (int): The index of the split bill customer for which the sales invoice is being created.

Returns:
- str: Returns the name of the created sales invoice.

Raises:
- frappe.exceptions.ValidationError: If a draft invoice already exists and single draft mode is enabled.

Example:
    create_sales('{"name": "Table 1", "split_bill_customer": [{"customer": "John", "bill_amount": 100}, {"customer": "Jane", "bill_amount": 200}], "total_charges": 300, "orders": [{"item": "Item 1", "quantity": 2}, {"item": "Item 2", "quantity": 3}], "kot_bot": [{"ticket_number": "123", "ticket_name": "KOT 123"}]}', 1)
    # Returns the name of the created sales invoice.
"""
@frappe.whitelist()
def create_sales(doc, index):
    doc = json.loads(doc)
    if doc.get("name"):
        single_draft = frappe.db.get_single_value(
            "Sajha Menu Settings", "single_draft")

        if single_draft == True:
            inv = frappe.db.get_list("Sales Invoice", {"docstatus": 0})
            if len(inv) > 0:
                frappe.throw(
                    f"Please submit draft invoice <a target='__blank' href='/app/sales-invoice/{inv[0].name}'>{inv[0].name}</a>")
                return {"code": "DRA_EXISTS", "name": inv[0].name}
        table = frappe.get_doc("Tables", doc.get('name'))
        splitCustomer = doc.get("split_bill_customer")
        totalCharges = doc.get('total_charges')
        splitRatio = splitCustomer[int(index)]['bill_amount']/totalCharges
        orders = []
        orderItems = doc['orders']
        kot_bot = doc['kot_bot']

        for o in orderItems:
            item = frappe.db.get_value("Item Price", {'item_code': o['item'], 'selling': 1}, [
                'name', 'item_code', 'price_list_rate', 'item_name', 'uom',], as_dict=True)
            itemTax = frappe.get_doc("Item", o["item"])

            taxTemplate = None
            if len(itemTax.taxes) > 0:
                taxTemplate = itemTax.taxes[0].item_tax_template

            itemCategory = frappe.get_doc(
                "Sub Category Items", {"item_code": o['item']})

            orders.append({
                'item_code': item['item_code'],
                'item_name': item['item_name'],
                'qty': o['quantity'],
                'rate': flt((itemCategory.rate) * splitRatio, 3),
                'amount': flt((o['quantity'] * itemCategory.rate) * splitRatio, 3),
                'uom': item['uom'],
                "description": "Test Description",
                "tax_template": taxTemplate
            })

        sales_invoice = frappe.new_doc('Sales Invoice')
        sales_invoice.customer = splitCustomer[int(index)]['customer']
        sales_invoice.table_name = doc.get("name")
        sales_invoice.company = doc.get('company')
        sales_invoice.due_date = frappe.utils.nowdate()
        sales_invoice.update_stock = 1

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

        restaurantName = frappe.get_doc(
            "Restaurant names", table.get("restaurant_names"))
        sales_invoice.naming_series = restaurantName.naming_series

        for ko in kot_bot:
            kot_bot_itm = sales_invoice.append("kot_bot", {})
            kot_bot_itm.ticket_number = ko['ticket_number']
            kot_bot_itm.ticket_name = ko['ticket_name']

        for o in orders:
            if o['qty'] > 0:
                default_account = None
                itemAccount = frappe.get_doc("Item", o['item_code'])
                for itm in itemAccount.item_defaults:
                    if doc.get('company') == itm.company:
                        default_account = itm.income_account
                        break
                sales_invoice_itm = sales_invoice.append('items', {})
                sales_invoice_itm.item_code = o['item_code']
                sales_invoice_itm.item_name = o['item_name']
                sales_invoice_itm.rate = o['rate']
                sales_invoice_itm.amount = o['amount']
                sales_invoice_itm.description = o['description']
                sales_invoice_itm.uom = o['uom']
                sales_invoice_itm.qty = o['qty']
                if o['tax_template']:
                    sales_invoice_itm.item_tax_template = o['tax_template']
                sales_invoice_itm.cost_center = default_cost_center
                if default_account != None:
                    sales_invoice_itm.income_account = default_account
                else:
                    sales_invoice_itm.income_account = default_incm_account

        sales_invoice.insert(ignore_permissions=True, ignore_links=True,
                                ignore_if_duplicate=True, ignore_mandatory=True)

        table.split_bill_customer[int(index)].invoice_status = "Done"

        table.save()

        table = frappe.get_doc("Tables", doc.get('name'))
        pendingBills = False
        for tab in table.get('split_bill_customer'):
            if tab.invoice_status == "Pending":
                pendingBills = True
                break
            else:
                pendingBills = False
        if pendingBills:
            return sales_invoice.name
        else:
            table.orders = []
            table.split_bill_customer = []
            table.split_bill = 0
            table.total_charges = 0.0
            table.kot_bot = []

        table.save()

        return sales_invoice.name

"""
Move the orders from a table to a room folio and create a sales invoice.

Parameters:
- doc (str): A JSON string representing the document containing the order details. It should contain the following keys:
    - name (str): The name of the document.
    - room_folio (str): The name of the room folio.
    - move_to_room (int): A flag indicating whether the orders should be moved to the room folio or not.
    - room_customer (str): The name of the customer for the room folio.
    - orders (list): A list of dictionaries representing the order items. Each dictionary should contain the following keys:
        - item (str): The item code.
        - quantity (float): The quantity of the item.
- index (int): The index of the split bill customer for which the sales invoice is being created. Set to -1 if the orders are not split.

Returns:
- str: Returns the name of the created sales invoice.

Example:
    moveToRoomFolio('{"name": "Table 1", "room_folio": "Room 123", "move_to_room": 1, "room_customer": "John Doe", "orders": [{"item": "Item 1", "quantity": 2}, {"item": "Item 2", "quantity": 3}]}', 1)
"""
# @frappe.whitelist()
# def moveToRoomFolio(doc, index):
#     doc = json.loads(doc)
#     index = int(index)
#     roomFolio = frappe.get_doc("Room Folio HMS", doc.get('room_folio'))
#     table = frappe.get_doc("Tables", doc.get('name'))
#     if doc.get("name"):
#         orders = []
#         orderItems = doc['orders']
#         splitRatio = 0.0

#         if index != -1:
#             splitCustomer = doc.get("split_bill_customer")
#             totalCharges = doc.get('total_charges')
#             splitRatio = splitCustomer[int(index)]['bill_amount']/totalCharges

#         for o in orderItems:
#             item = frappe.db.get_value("Item Price", {'item_code': o['item'], 'selling': 1}, [
#                 'name', 'item_code', 'price_list_rate', 'item_name', 'uom',], as_dict=True)
#             itemTax = frappe.get_doc("Item", o["item"])
#             taxTemplate = None
#             if len(itemTax.taxes) > 0:
#                 taxTemplate = itemTax.taxes[0].item_tax_template
#             orders.append({
#                 'item_code': item['item_code'],
#                 'item_name': item['item_name'],
#                 'qty': o['quantity'],
#                 'rate': flt(item['price_list_rate']) if index == -1 else flt(item['price_list_rate'] * splitRatio, 3),
#                 'amount': flt((o['quantity'] * item['price_list_rate'])) if index == -1 else flt((o['quantity'] * item['price_list_rate']) * splitRatio, 3),
#                 'uom': item['uom'],
#                 'income_account': "Entertainment Expenses - Y",
#                 "description": "Test Description",
#                 "tax_template": taxTemplate
#             })

#         sales_invoice = frappe.new_doc('Sales Invoice')
#         if index != -1:
#             sales_invoice.customer = table.split_bill_customer[int(
#                 index)].customer
#         else:
#             if doc.get('move_to_room') == 1:
#                 if doc.get('room_customer') == None or doc.get('room_customer') == '':
#                     sales_invoice.customer = roomFolio.customer
#                 else:
#                     sales_invoice.customer = doc.get('room_customer')

#         sales_invoice.table_name = doc.get("name")
#         sales_invoice.due_date = frappe.utils.nowdate()

#         default_incm_account = frappe.db.get_value(
#             "Company", {"name": doc.get("company")}, ['default_income_account'])
#         default_cost_center = frappe.db.get_value(
#             "Company", {"name": doc.get("company")}, ['cost_center'])

#         for o in orders:
#             if o['qty'] > 0:
#                 default_account = None
#                 itemAccount = frappe.get_doc("Item", o['item_code'])
#                 for itm in itemAccount.item_defaults:
#                     if doc.get('company') == itm.company:
#                         default_account = itm.income_account
#                         break
#                 sales_invoice_itm = sales_invoice.append('items', {})
#                 sales_invoice_itm.item_code = o['item_code']
#                 sales_invoice_itm.item_name = o['item_name']
#                 sales_invoice_itm.rate = o['rate']
#                 sales_invoice_itm.amount = o['amount']
#                 sales_invoice_itm.description = o['description']
#                 sales_invoice_itm.uom = o['uom']
#                 sales_invoice_itm.qty = o['qty']
#                 if o['tax_template']:
#                     sales_invoice_itm.item_tax_template = o['tax_template']
#                 sales_invoice_itm.cost_center = default_cost_center
#                 if default_account != None:
#                     sales_invoice_itm.income_account = default_account
#                 else:
#                     sales_invoice_itm.income_account = default_incm_account

#         sales_invoice.insert(ignore_permissions=True, ignore_links=True,
#                              ignore_if_duplicate=True, ignore_mandatory=True)

#         roomFolioInvoice = roomFolio.append('restrurant_invoice', {})

#         roomFolioInvoice.reference = sales_invoice.name

#         roomFolio.save()

#         if index != -1:
#             pendingBills = False
#             table.split_bill_customer[int(index)].invoice_status = "Done"
#             table.save()
#             for tab in table.get('split_bill_customer'):
#                 if tab.invoice_status == "Pending":
#                     pendingBills = True
#                     break
#                 else:
#                     pendingBills = False

#             if pendingBills:
#                 return sales_invoice.name
#             else:
#                 table.orders = []
#                 table.split_bill_customer = []
#                 table.split_bill = 0
#                 table.total_charges = 0.0
#         else:
#             table.orders = []
#             table.total_charges = 0.0

#         table.save()
#         return sales_invoice.name

"""
This function filters and retrieves a list of room folios based on the provided filters.

Parameters:
- doctype (str): The doctype of the document.
- txt (str): The search text.
- searchfield (str): The field to search in.
- start (int): The starting index of the results.
- page_len (int): The number of results per page.
- filters (dict): A dictionary containing the filter parameters. It should contain the following keys:
    - status (str): The status of the room folios to filter by.
    - category (str): The category of the room folios to filter by. Can be either "Room" or "Other".
    - company (str): The company name to filter by.
    - room_no (str): The room number to filter by for the "Room" category.
    - room_number (str): The room number to filter by for the "Other" category.

Returns:
- tuple: Returns a tuple of room folio names that match the provided filters.

Example:
    room_folio_fltr("Room Folio HMS", "123", "name", 0, 10, {"status": "Open", "category": "Room", "company": "ABC Corp", "room_no": "101"})
"""
# @frappe.whitelist()
# def room_folio_fltr(doctype, txt, searchfield, start, page_len, filters):
#     status = filters['status']
#     if filters['category'] == "Room":
#         room_folio_list = frappe.db.get_list('Room Folio HMS', filters={'status': [
#             '=', status], 'company': ['like', filters['company']], 'room_no': ['=', filters['room_no']]})
#     else:
#         room_folio_list = frappe.db.get_list('Room Folio HMS', filters={'status': [
#             '=', status], 'company': ['like', filters['company']], 'room_no': ['=', filters['room_number']]})
#     available_folio = []

#     for rc in room_folio_list:
#         available_folio.append([rc.name])

#     return tuple(available_folio)

"""
This function retrieves the split bill customers for a given room folio.

Parameters:
- roomFolio (str): The name of the room folio.

Returns:
- list or str: Returns a list of dictionaries representing the split bill customers if the room folio has a split bill. Returns 'no-split-bill' if the room folio does not have a split bill.

Example:
    splitCustomer('Room 123')
"""
# @frappe.whitelist()
# def splitCustomer(roomFolio):
#     doc = frappe.get_doc("Room Folio HMS", roomFolio)
#     if doc.split_bill == 1:
#         return doc.split_bill_customer
#     else:
#         return "no-split-bill"
