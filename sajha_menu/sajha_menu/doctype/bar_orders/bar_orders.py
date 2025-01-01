# Copyright (c) 2023, tuna and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import __version__ as app_version

                                                                                                                                   
class BarOrders(Document):
    def validate(self):
        try:
            Available_stock = 0
            for item in self.items:
                order_status = frappe.db.get_value("Bar Child", item.name, 'order_status')
                if (item.order_status == 1 or self.status == "Done") and order_status == 0:
                    order_quantity = int(item.quantity)
                    item_code = item.item_code
                    item_doc = frappe.get_doc("Item", item_code)
                    brand = item_doc.brand
                    item_group = item_doc.item_group
                    item_packs_ml = item_doc.bar_item_size_ml
                    company,default_warehouse = frappe.db.get_value(
                        'Item Default', {'parent': item_code}, ['company','default_warehouse'])
                    main_bottle_itemcode = frappe.db.get_value(
                        "Item",{"brand": brand,"is_main_bottle":1},"item_code"
                    )
                    item_main = frappe.get_doc("Item", main_bottle_itemcode)
                    item_bottle_ml = item_main.bar_item_size_ml
                    total_order_qty = item_packs_ml * order_quantity
                    count = 0
                    new_loose_bottle_quantity = 0
                    initial_loose_bottle_stock = 0
                    bottle_stock = 0
                    bottle_stock = frappe.db.get_value(
                        "Bin", {"item_code": main_bottle_itemcode, "warehouse": default_warehouse}, "actual_qty")
                    loose_bottle_item = frappe.db.get_value(
                        "Item", {"item_code": f"{brand}- Loose Bottle","brand": brand})
                    if not loose_bottle_item:
                        # create loose bottle item
                        new_item = frappe.new_doc('Item')
                        new_item.item_code = f"{brand}- Loose Bottle"
                        new_item.item_name = f"{brand}- Loose Bottle"
                        new_item.item_group = item_group
                        new_item.stock_uom = 'Millilitre'
                        new_item.is_stock_item = 1
                        new_item.has_variants = 0
                        new_item.brand = brand
                        new_item.is_taxable = 1
                        new_item.description = f'This is a loose bottle item of brand {brand}'
                        new_item.append('item_defaults', {
                                        'default_warehouse': default_warehouse, 'company':company})
                        new_item.append('taxes', {
                                        'item_tax_template': item_main.taxes[0].item_tax_template})
                        new_item.insert()
                    # checks stock of loose item bottle
                    loose_bottle_stock = frappe.db.get_value(
                        "Bin", {"item_code": f"{brand}- Loose Bottle", "warehouse": default_warehouse}, "actual_qty")
                    if loose_bottle_stock:
                        new_loose_bottle_quantity = loose_bottle_stock
                        initial_loose_bottle_stock = loose_bottle_stock
                    if Available_stock == 0:
                        Available_stock = f"{bottle_stock} bottles and {initial_loose_bottle_stock}ml."
                    while new_loose_bottle_quantity < total_order_qty:
                        if not loose_bottle_stock:
                            new_loose_bottle_quantity = item_bottle_ml
                            loose_bottle_stock = item_bottle_ml
                            count += 1
                        else:
                            new_loose_bottle_quantity += item_bottle_ml
                            count += 1
                    if count > 0:
                        if bottle_stock >= count:
                            # reduce stock from Main Bottel
                            stock_entry_update(
                                count, main_bottle_itemcode, "Material Issue", default_warehouse,self.company)
                            # update stock of Losse bootel
                            stock_entry_update(new_loose_bottle_quantity - initial_loose_bottle_stock,
                                            f"{brand}- Loose Bottle", "Material Receipt", default_warehouse,self.company)
                            # reduce stock of Loose bottel
                            stock_entry_update(
                                total_order_qty, f"{brand}- Loose Bottle", "Material Issue", default_warehouse,self.company)
                            # stock entry for item packs
                            stock_entry_update(
                                order_quantity, item_code, "Material Receipt", default_warehouse,self.company)
                            # reduce stock of orderd item
                            # stock_entry_update(
                            #     order_quantity, item_code, "Material Issue", default_warehouse)
                        else:
                            frappe.throw(
                                f"Not enough stock for {brand}- Bottle Available stock is  {Available_stock}")
                    else:
                        # reduce the stock frome loosebottel
                        stock_entry_update(
                            total_order_qty, f"{brand}- Loose Bottle", "Material Issue", default_warehouse,self.company)
                        # stock entry for item packs
                        stock_entry_update(
                            order_quantity, item_code, "Material Receipt", default_warehouse,self.company)
                        # reduce stock of orderd item
                        # stock_entry_update(
                        #     order_quantity, item_code, "Material Issue", default_warehouse)
        except Exception as e:
            frappe.throw(str(e))
            frappe.log_error(frappe.get_traceback(), f"{e}")

def stock_entry_update(qty_to_update, bottle_type, stock_entry_type, default_warehouse, company):
    if stock_entry_type == "Material Issue":
        warehouse = "s_warehouse"
    else:
        warehouse = "t_warehouse"
    new_stock_entry = frappe.new_doc(
        "Stock Entry")
    # Check the initial state of the item
    initial_is_stock_item = frappe.db.get_value(
        "Item", bottle_type, "is_stock_item")
    # Convert non-stock items to stock items for stock entry update
    if not initial_is_stock_item:
        frappe.db.set_value("Item", bottle_type, "is_stock_item", 1)
    new_stock_entry.stock_entry_type = stock_entry_type
    new_stock_entry.company = company
    new_stock_entry.append("items", {
        "item_code": bottle_type,
        warehouse: default_warehouse,
        "qty": qty_to_update,
        "allow_zero_valuation_rate": 1
    })
    new_stock_entry.insert()
    new_stock_entry.submit()
    # Revert items back to their original status
    frappe.db.set_value("Item", bottle_type,
                        "is_stock_item", initial_is_stock_item)


@frappe.whitelist()
def changeStatus(doc, previousDocs):
    doc = json.loads(doc)
    previousOrders = []
    previousDocs = frappe.get_doc("Bar Orders", doc.get("name"))
    for po in previousDocs.items:
        p = frappe.get_doc('Bar Child', po.name)
        previousOrders.append(p)
    table = frappe.get_doc("Tables", doc.get(
        'table_name'), ['name', 'item_code'])
    orders = doc.get('items')
    for o in table.orders:
        order = frappe.get_doc("Total Order", o.name)
        def item_code_check(v):
            return v['item_code'] == order.item
        item = next(filter(item_code_check, orders), None)
        if item:
            index = next(i for i, x in enumerate(
                orders) if x['item_code'] == order.item)
            order.quantity = order.quantity + \
                orders[index]['quantity'] - previousOrders[index].quantity
            if order.quantity == 0:
                frappe.db.delete('Total Order', o.name)
            order.db_update()
    return "Debugging"
