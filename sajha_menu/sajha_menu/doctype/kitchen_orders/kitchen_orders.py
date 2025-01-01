# Copyright (c) 2023, tuna and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from datetime import datetime


class KitchenOrders(Document):
    def on_update(self):
        frappe.publish_realtime('table_refresh', {'data': 'success'})
    
    
    
    """
    Update the stock entry for a given quantity of a food item.

    Parameters:
    - None

    Returns:
    None

    Raises:
    None
    """
    def before_save(self):
            Available_stock = 0
            for item in self.items:
                if item.order_status == 1 or self.status == "Done":
                    item_code = item.item_code   #momo
                    order_quantity = int(item.quantity) # 5
                    item_doc = frappe.get_doc("Item", item_code) 
                    item_group = item_doc.item_group
                    items_needed_preperation= frappe.get_all("Pre prep items",filters ={"parent":f"{item_code}"}, fields = ['name','item','quantity','uom'],ignore_permissions=True)
                    for item in items_needed_preperation:
                        item_needed = item['item']
                        quantity_needed = item['quantity']
                        uom = item['uom']
                        item_main = frappe.get_doc("Item", item_needed)
                        total_order_qty = quantity_needed * order_quantity
                        main_food_item_weight = item_main.food_item_weight
                        count = 0
                        new_open_packet_food_item_stock = 0
                        initial_open_packet_food_item_stock = 0
                        default_warehouse = frappe.db.get_value(
                            'Item Default', {'parent': item_needed}, 'default_warehouse')
                        food_stock = frappe.get_value(
                            "Bin", {"item_code":item_needed, "warehouse": default_warehouse}, "actual_qty")
                        open_packet_food_item = frappe.get_value(
                            "Item", {"item_code": f"{item_needed}-open packet"})
                        
                        if not open_packet_food_item:
                        # create open packet item
                            new_item = frappe.new_doc('Item')
                            new_item.item_code = f"{item_needed}-open packet"
                            new_item.item_name = f"{item_needed}-open packet"
                            new_item.item_group = item_group
                            new_item.stock_uom = uom
                            new_item.is_stock_item = 1
                            new_item.has_variants = 0
                            new_item.description = 'This is a  open food packet'
                            new_item.append('item_defaults', {
                                            'default_warehouse': default_warehouse})
                            new_item.append('taxes', {
                                    'item_tax_template': item_main.taxes[0].item_tax_template})
                            new_item.insert()
                            
                        # checks stock of open packet item
                        open_packet_food_item_stock = frappe.get_value(
                            "Bin", {"item_code": f"{item_needed}-open packet", "warehouse": default_warehouse}, "actual_qty")
                        
                        if open_packet_food_item_stock:
                            new_open_packet_food_item_stock = open_packet_food_item_stock
                            initial_open_packet_food_item_stock= open_packet_food_item_stock
                        if Available_stock == 0:
                            Available_stock = f"{food_stock} packets and {initial_open_packet_food_item_stock} open packet."
                        
                        while new_open_packet_food_item_stock < total_order_qty:
                            if not open_packet_food_item_stock:
                                new_open_packet_food_item_stock = main_food_item_weight
                                open_packet_food_item_stock = main_food_item_weight
                                count += 1
                            else:
                                new_open_packet_food_item_stock += main_food_item_weight
                                count += 1
                        
                        if count > 0:
                            if food_stock >= count:
                                # reduce stock from Main food item
                                
                                stock_entry_update(
                                    count, item_needed, "Material Issue", default_warehouse)

                                # update stock of open packet
                                stock_entry_update(new_open_packet_food_item_stock - initial_open_packet_food_item_stock,
                                                f"{item_needed}-open packet", "Material Receipt", default_warehouse)

                                # reduce stock of open packet
                                stock_entry_update(
                                    total_order_qty, f"{item_needed}-open packet", "Material Issue", default_warehouse)

                            else:
                                frappe.throw(
                                    f"Not enough stock of {item_needed}- for {item_code} preperation.Available stock is  {Available_stock}")
                        else:
                            # reduce the stock frome open packet
                            stock_entry_update(
                                total_order_qty, f"{item_needed}-open packet", "Material Issue", default_warehouse)

"""
Update the stock entry for a given quantity of a food item.

Parameters:
- qty_to_update (int): The quantity to update in the stock entry.
- food_type (str): The code of the food item.
- stock_entry_type (str): The type of stock entry (Material Issue or Material Receipt).
- default_warehouse (str): The default warehouse for the stock entry.

Returns:
None

Raises:
None

"""                                        
def stock_entry_update(qty_to_update, food_type, stock_entry_type, default_warehouse):
    if stock_entry_type == "Material Issue":
        warehouse = "s_warehouse"
    else:
        warehouse = "t_warehouse"
    new_stock_entry = frappe.new_doc(
        "Stock Entry")
    new_stock_entry.stock_entry_type = stock_entry_type
    new_stock_entry.append("items", {
        "item_code": food_type,
        warehouse: default_warehouse,
        "qty": qty_to_update,
        "allow_zero_valuation_rate": 1
    })
    new_stock_entry.insert()
    new_stock_entry.submit()


"""
Change the status of a document and update the stock entry for a given quantity of a food item.

Parameters:
- doc (str): The document to change the status of, in JSON format.
- previousDocs (str): The previous documents related to the stock entry, in JSON format.

Returns:
str: A debugging message.

Raises:
None
"""
@frappe.whitelist()
def changeStatus(doc, previousDocs):
    doc = json.loads(doc)
    previousOrders = []
    previousDocs = frappe.get_doc("Kitchen Orders", doc.get("name"))
    for po in previousDocs.items:
        p = frappe.get_doc('Food Child', po.name)
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

            order.quantity = order.quantity + orders[index]['quantity'] - previousOrders[index].quantity 
                            #total order quantity +  new kot order quantity - old kot quantity
            if order.quantity == 0:
                frappe.db.delete('Total Order', o.name)
            order.db_update()
    return "Debugging"


@frappe.whitelist()
def getServerDate(doc):
    doc = json.loads(doc)   
   
    data = frappe.db.get_value("KOT_BOT", {'parenttype': 'Sales Invoice', 'ticket_name': doc.get('name')})
    if data is not None:
        return True
    else:
        return False
   

    
