// Copyright (c) 2023, tuna and contributors
// For license information, please see license.txt


var previousQuantity = 0;
var edited = false
var previousDocs = []

frappe.ui.form.on('Bar Orders', {
	refresh: function (frm) {
		if (frm.doc.kot_status === "Cancelled") {
			frm.set_df_property("items", "read_only", 1);
		}

		if (frm.doc.status === "Done") {
			frm.set_df_property("items", "read_only", 1);
			frm.set_df_property("status", "read_only", 1);
		}

		frappe.call({
			method: "sajha_menu.sajha_menu.doctype.kitchen_orders.kitchen_orders.getServerDate",
			args: { "doc": frm.doc },
			callback: function (r) {

				if (r.message) {
					frm.set_df_property("items", "read_only", 1);
				}

				if (!r.message && frm.doc.kot_status !== "Cancelled") {
					frm.add_custom_button('Cancel KOT', () => {
						frappe.call({
							method: "sajha_menu.api.stopCancel",
							freeze: true,
							always: function (r) {
								if (r.message) {
									frm.reload_doc()
									frappe.throw(__("You don't have enough permission"))
								} else {
									frm.doc.bot_status = "Cancelled"

									for (var i = 0; i < frm.doc.items.length; i++) {
										frm.doc.items[i].removed_quantity = frm.doc.items[i].removed_quantity + frm.doc.items[i].quantity
									}
									for (var i = 0; i < frm.doc.items.length; i++) {
										frm.doc.items[i].quantity = 0
									}
									frm.refresh_fields()
									frm.set_df_property("items", "read_only", 1);
									edited = true
									frm.dirty();
									frm.save();
								}

							}
						})
					})

				}
			}
		})
	},
	before_save: function (frm) {
		if (edited) {
			frappe.call({
				method: "sajha_menu.api.stopCancel",
				freeze: true,
				always: function (r) {
					if (r.message) {
						frm.reload_doc()
						frappe.msgprint(__("You don't have enough permission"))
					} else {
						frappe.call({
							method: "sajha_menu.sajha_menu.doctype.bar_orders.bar_orders.changeStatus",
							args: { "doc": frm.doc, previousDocs },
							callback: function (r) {
								if (r.message) {

								}
							}
						})
					}

				}
			})

		}
	}
});

frappe.ui.form.on("Bar Child", {
	order_status: async function (frm, cdt, cdn) {
		var selected_row = frappe.get_doc(cdt, cdn);
		if (await selected_row.order_status == 0) {
			frappe.msgprint(
				msg = 'Order status cannot be changed!..',
				title = 'Permission Denied!',
			)
			frm.reload_doc();
		}
	},
	form_render: function (frm, doctype, id) {
		var child_row = frappe.get_doc(doctype, id)
		previousQuantity = child_row.quantity
	},
	quantity: function (form, doctype, id) {
		var child_table_row = frappe.get_doc(doctype, id)
		frappe.call({
			method: "sajha_menu.api.stopCancel",
			freeze: true,
			always: function (r) {
				if (r.message) {
					form.reload_doc()
					frappe.throw(__("You don't have enough permission"))
				}

			}
		})
		if (child_table_row.quantity > previousQuantity) {
			frappe.call({
				method: "sajha_menu.api.stopCancel",
				freeze: true,
				always: function (r) {

					if (!r.message) {
						form.reload_doc()
						frappe.throw(__("Previous Quantity is smaller than Current quantity. If you are adding quantity please create new KOT"))
					}

				}
			})
		}

		if (child_table_row.quantity != previousQuantity) {

			if (child_table_row.remarks === undefined) {
				frappe.call({
					method: "sajha_menu.api.stopCancel",
					freeze: true,
					always: function (r) {
						if (!r.message) {
							form.reload_doc()
							frappe.throw(__("Please add remarks before editing quantity"))
						}

					}
				})
			} else {
				form.doc.bot_status = "Edited"
				edited = true
				child_table_row.removed_quantity += previousQuantity - child_table_row.quantity
				form.refresh_field("bot_status")
				index = previousDocs.findIndex((e) => e.name === child_table_row.name)
				if (index > -1) {
					console.log('already here');
				} else {
					previousDocs.push({ ...child_table_row, quantity: previousQuantity })
				}
			}
		}
	}
})
