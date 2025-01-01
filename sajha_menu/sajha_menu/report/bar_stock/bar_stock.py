# Copyright (c) 2023, tuna and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    if not filters:
        return [], []

    columns = get_columns()

    data = []

    brand = filters.get("brand")
    
    if brand:
        main_bottle_item_code = frappe.db.get_value(
            "Item", {"brand": brand, "item_group": "Bar Items", "is_main_bottle": 1}, "item_code")
        loose_bottle_item_code = f"{brand}- Loose Bottle"
        main_bottle_stock_qty = frappe.db.sql(f"""
				SELECT actual_qty as stock_qty
				FROM `tabBin`
				WHERE item_code = "{main_bottle_item_code}"
			""", as_dict=True)[0].stock_qty

        loose_bottle_stock_qty = frappe.db.sql(f"""
				SELECT actual_qty as stock_qty
				FROM `tabBin`
				WHERE item_code = "{loose_bottle_item_code}"
			""", as_dict=True)[0].stock_qty

        if main_bottle_stock_qty <= 1:
            total_stock = str(main_bottle_stock_qty) + \
                " bottles and " + str(loose_bottle_stock_qty) + " ml"
        else:
            total_stock = str(main_bottle_stock_qty) + \
                " bottles and " + str(loose_bottle_stock_qty) + " ml"

        row = {
            "brand": brand,
            "bottle_stock": main_bottle_stock_qty,
            "loose_bottle_stock": loose_bottle_stock_qty,
            "total_stock": total_stock,
        }
        data.append(row)

    else:
        item_doc = frappe.db.get_all(
            "Item", filters={"item_group": "Bar Items"}, fields=["name"])
        for item in item_doc:
            
            main_bottle_item_code = frappe.db.get_value(
                "Item", {"name": item.name, "is_main_bottle": 1}, "item_code")
            if main_bottle_item_code: 
                brand = frappe.get_value("Item", {"item_code": main_bottle_item_code}, "brand")
                loose_bottle_item_code = f"{brand}- Loose Bottle"

                main_bottle_stock_qty = frappe.db.sql(f"""
                    SELECT actual_qty as stock_qty
                    FROM `tabBin`
                    WHERE item_code = "{main_bottle_item_code}"
                """, as_dict=True)[0].stock_qty
                
                loose_bottle_stock_qty = frappe.db.sql(f"""
                    SELECT actual_qty as stock_qty
                    FROM `tabBin`
                    WHERE item_code = "{loose_bottle_item_code}"
                """, as_dict=True)[0].stock_qty

                if main_bottle_stock_qty <= 1:
                    total_stock = str(main_bottle_stock_qty) + \
                        " bottle and " + str(loose_bottle_stock_qty) + " ml"
                else:
                    total_stock = total_stock = str(
                        main_bottle_stock_qty) + " bottles and " + str(loose_bottle_stock_qty) + " ml"
                row = {
                    "brand": brand,
                    "bottle_stock": main_bottle_stock_qty,
                    "loose_bottle_stock": loose_bottle_stock_qty,
                    "total_stock": total_stock,
                }
                data.append(row)
            else:
                pass
    return columns, data


def get_columns():
    return [
        {
            'label': _('Brand'),
            'fieldname': 'brand',
            'fieldtype': 'Link',
            'options': "Brand",
            'width': '120'
        },
        {
            'label': _('Bottle stock'),
            'fieldname': 'bottle_stock',
            'fieldtype': 'int',
            'width': '100'
        },
        {
            'label': _('Loose Bottle Stock'),
            'fieldname': 'loose_bottle_stock',
            'fieldtype': 'data',
            'width': '100'
        },
        {
            'label': _('Total Stock'),
            'fieldname': 'total_stock',
            'fieldtype': 'data',
            'width': '200'
        }
    ]
