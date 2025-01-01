// Copyright (c) 2023, tuna and contributors
// For license information, please see license.txt

frappe.ui.form.on('Home Delivery Orders', {
	refresh: function (frm) {
		if (frm.doc.status === "Order Received") {
			frm.add_custom_button(__("Confirm Order"),
				function () {
					frappe.call({
						method: 'sajha_menu.sajha_menu.doctype.home_delivery_orders.home_delivery_orders.ConfirmOrder',
						args: {
							doc: frm.doc,
						},
						always: function (r) {
							if (r.message) {
								frm.reload_doc()
							}
						}
					})
				}
			)
		}

		if (frm.doc.status === "Order Confirmed") {
			frm.add_custom_button(__("Mark as Delivered"),
				function () {
					frappe.call({
						method: 'sajha_menu.sajha_menu.doctype.home_delivery_orders.home_delivery_orders.MarkAsDelivered',
						args: {
							doc: frm.doc,
						},
						always: function (r) {
							if (r.message) {
								frm.reload_doc()
							}
						}
					})
				}
			)
		}


		if (frm.doc.status !== "Order Cancelled" && frm.doc.ticket_created === 0) {
			frm.add_custom_button(__("Cancel Order"),
				function () {
					frappe.call({
						method: 'sajha_menu.sajha_menu.doctype.home_delivery_orders.home_delivery_orders.CancelOrder',
						args: {
							doc: frm.doc,
						},
						always: function (r) {
							if (r.message) {
								frm.reload_doc()
							}
						}
					})
				}
			)
		}


		if (frm.doc.ticket_created === 0) {
			frm.add_custom_button('Create KOT/BOT', () => {

				frappe.call({
					method: "sajha_menu.sajha_menu.doctype.home_delivery_orders.home_delivery_orders.create_kot_or_bot_order",
					args: { "order_number": frm.doc.name, "orderItem": frm.doc.delivery_items, 'company': frm.doc.company },
					callback: function (r) {
						frm.reload_doc()

						// frm.current_order = []

					}
				})


			}).css
				({ 'background-color': '#1034A6', 'color': 'white', 'font-weight': '700' })
		}

		if (frm.doc.ticket_created === 1 && frm.doc.sales_invoice_reference === undefined) {
			frm.add_custom_button('Create Sales Invoice', () => {

				frappe.call({
					method: "sajha_menu.sajha_menu.doctype.home_delivery_orders.home_delivery_orders.createSalesInvoice",
					args: { "doc": frm.doc },
					callback: function (r) {
						frm.reload_doc()

						// frm.current_order = []

					}
				})


			})
		}
	}
});
