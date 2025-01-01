// Copyright (c) 2022, tuna and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tables', {
	setup: function (frm) {

		frm.set_query('room_folio', function () {
			return {
				query: "sajha_menu.sajha_menu.doctype.tables.tables.room_folio_fltr",
				filters: {
					status: "Checked In",
					company: frm.doc.company,
					room_no: frm.doc.name,
					category: frm.doc.category,
					room_number: frm.doc.room_number ?? ""
				}
			}
		})
	},

	// onload: function (frm) {
	// 	frappe.call({
	// 		method: "sajha_menu.sajha_menu.doctype.tables.tables.updateTotal",
	// 		args: { "doc": frm.doc },
	// 		callback: function (d) {

	// 		}
	// 	})
	// },

	refresh: function (frm) {
		if (frm.doc.current_orders.length > 0) {
			frm.add_custom_button('Create KOT/BOT', () => {

				frappe.call({
					method: "sajha_menu.api.create_kot_or_bot_order",
					args: { "table_name": frm.docname, "orderItem": frm.doc.current_orders, 'company': frm.doc.company },
					callback: function (r) {
						frm.reload_doc()

						// frm.current_order = []

					}
				})


			}).css({ 'background-color': '#1034A6', 'color': 'white', 'font-weight': '700' })
		}

		frm.add_custom_button('Switch to POS', () => {
			window.location.href = "/sajha_menu"
		}).css({ 'background-color': '#177245', 'color': 'white', 'font-weight': '700' })

		frm.set_df_property('room_folio', 'hidden', 1)
		frm.set_df_property('move_to', 'hidden', 1)
		frm.set_df_property('room_number', 'hidden', 1)
		frm.set_df_property('room_customer', 'hidden', 1)



		if (!frm.doc.split_bill) {
			frm.set_df_property('split_bill_customer', 'hidden', 1)
			frm.set_df_property('create_sales_invoice', 'hidden', 0)

			frm.set_df_property('move_to_room', 'hidden', 0)
			frm.set_df_property('room_folio', 'hidden', 1)
			frm.set_df_property('room_number', 'hidden', 1)
			frm.set_df_property('move_to', 'hidden', 1)
			frm.set_value('room_number', '')
			frm.set_value('room_folio', '')

		} else {
			frm.set_df_property('split_bill_customer', 'hidden', 0)
			frm.set_df_property('create_sales_invoice', 'hidden', 1)
			frm.set_df_property('move_to_room', 'hidden', 1)
			frm.set_df_property('room_folio', 'hidden', 0)
			frm.set_df_property('room_number', 'hidden', 0)
			frm.set_df_property('move_to', 'hidden', 1)
		}

		frm.set_value('move_to_room', 0)

		frappe.call({
			method: "sajha_menu.api.tuna_hms_enabled",
			args: {},
			callback: function (r) {

				// frm.current_order = []
				if (r.message === 0) {
					frm.set_df_property('move_to_room', 'hidden', 1)
				}

			}
		})

		frm.add_custom_button('Clear Table', () => {
			frappe.call({
				method: "sajha_menu.api.clearTable",
				args: { "table_name": frm.docname },
				callback: function (r) {

					// frm.current_order = []
					frm.reload_doc();
				}
			})

		}).css({ 'background-color': ' #9F1D35', 'color': 'white', 'font-weight': '700' })
	},

	before_save(frm) {
		frappe.call({
			method: "sajha_menu.sajha_menu.doctype.tables.tables.validate_split",
			args: { "doc": frm.doc },
			freeze: true,
			always: function (r) {

				if (r.message === 'no_customer') {
					frappe.throw(
						__("Split bill is selected but no customer added to the list"))
					return false
				}

				if (r.message === 'mismatch') {
					frappe.throw(
						__("Split total is not equal to total charges of the table"))
					return false
				}

				if (r.message === 'ok') {
					return true

				}

			}
		})
	},


	category: function (frm) {
		frappe.call({
			method: "sajha_menu.api.stopremove",
			freeze: true,
			always: function (r) {
				if (r.message) {
					frm.reload_doc()
					frappe.throw(__("You don't have enough permission"))
				}

			}
		})
	},

	company: function (frm) {
		frappe.call({
			method: "sajha_menu.api.stopremove",
			freeze: true,
			always: function (r) {
				if (r.message) {
					frm.reload_doc()
					frappe.throw(__("You don't have enough permission"))
				}

			}
		})
	},

	split_bill: function (frm) {
		if (frm.doc.split_bill === 1) {
			frm.set_value('move_to_room', 0)
			frm.set_df_property('move_to', 'hidden', 1)
			frm.set_df_property('room_folio', 'hidden', 1)
			frm.set_df_property('move_to_room', 'hidden', 1)
			frm.set_value('room_customer', '')
			frm.set_df_property('room_customer', 'hidden', 1)
			frm.set_df_property('create_sales_invoice', 'hidden', 1)
			frm.set_df_property('split_bill_customer', 'hidden', 0)
			frm.set_df_property('room_folio', 'hidden', 0)
			frm.set_df_property('room_number', 'hidden', 0)
			frm.set_df_property('confirm_split', 'hidden', 0)
			// frm.refresh_fields()
		} else {
			var child_table = frm.fields_dict['split_bill_customer'].grid;
			var data = child_table.get_data();

			for (var i = 0; i < data.length; i++) {
				if (data[i].invoice_status === "Done") {

					frm.reload_doc()
					frappe.throw(__("Cannot toggle `split bill`, since one of the customer already have sales invoice created"))
					return
				}
			}

			if (data.length > 0) {
				if (data.length > 0) {
					child_table.remove_all();
					frm.refresh_field('split_bill_customer')
				}
			}
			frm.set_df_property('create_sales_invoice', 'hidden', 0)
			frm.set_df_property('split_bill_customer', 'hidden', 1)
			frm.set_df_property('room_number', 'hidden', 1)
			frm.set_df_property('room_folio', 'hidden', 1)
			frm.set_df_property('move_to_room', 'hidden', 0)
		}
	},

	room_folio: function (frm) {
		if (frm.doc.room_folio !== "") {
			frappe.call({
				method: "sajha_menu.sajha_menu.doctype.tables.tables.splitCustomer",
				args: { "roomFolio": frm.doc.room_folio },
				callback: async function (r) {
					if (r.message === 'no-split-bill') {

						frm.set_df_property('room_customer', 'hidden', 1)
					} else {
						var customer = []

						for (var i = 0; i < r.message.length; i++) {
							customer.push(r.message[i].customer)
						}
						if (frm.doc.move_to_room === 1) {
							frm.set_df_property('room_customer', 'hidden', 0)
							frm.set_df_property('room_customer', 'options', customer)
							refresh_field('room_customer')

						}

					}
				}
			})
		}

	},

	room_number: function (frm) {
		frm.set_value('room_folio', "")
		frm.set_df_property('room_customer', 'options', [])
		frm.set_df_property('room_customer', 'hidden', 1)
	},

	move_to_room: function (frm) {
		if (frm.doc.move_to_room === 1) {
			frm.set_value('split_bill', 0)
			frm.set_df_property('split_bill', 'hidden', 1)
			frm.set_value('room_customer', '')
			frm.set_df_property('room_customer', 'hidden', 1)
			frm.set_df_property('room_folio', 'hidden', 0)
			frm.set_df_property('room_number', 'hidden', 0)
			frm.set_df_property('move_to', 'hidden', 0)
			frm.set_df_property('create_sales_invoice', 'hidden', 1)
		} else {
			frm.set_df_property('split_bill', 'hidden', 0)
			frm.set_df_property('room_folio', 'hidden', 1)
			frm.set_df_property('move_to', 'hidden', 1)
			frm.set_df_property('room_number', 'hidden', 1)
			frm.set_df_property('create_sales_invoice', 'hidden', 0)
		}
	},

	// room_number: function (frm) {
	// 	frm.set_query('room_folio', function () {
	// 		return {
	// 			query: "sajha_menu.sajha_menu.doctype.tables.tables.room_folio_fltr",
	// 			filters: {
	// 				status: "Checked In",
	// 				company: frm.doc.company,
	// 				room_no: frm.doc.name,
	// 				category: frm.doc.category,
	// 				room_number: frm.doc.room_number
	// 			}
	// 		}
	// 	})
	// }

});


frappe.ui.form.on('Total Order', {
	before_orders_remove: function (form, doctype, id) {
		frappe.call({
			method: "sajha_menu.api.stopremove",
			freeze: true,
			args: { "doc": form.doc.orders },
			always: function (r) {

				if (r.message) {
					frappe.throw(__("You don't have enough permission"))
					form.reload_doc()
				}
			}
		})

	}
})

frappe.ui.form.on('Split Bill', {
	create(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn)

		if (frm.doc.__unsaved === 1) {
			frappe.throw(__('Please save/update the form before creating sales invoice'))
			return false
		}

		if (row.invoice_status === "Done") {
			frappe.throw(__('Invoice already created'))
			return false
		}

		let index = frm.doc.split_bill_customer.findIndex((e) => e.name == cdn)

		frappe.call({
			method: "sajha_menu.sajha_menu.doctype.tables.tables.create_sales",
			args: { "doc": frm.doc, 'index': index },
			callback: function (r) {
				frm.reload_doc()
				window.open(`/app/sales-invoice/${r.message}`)
			}
		})


	},
	move_split(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn)

		if (frm.doc.__unsaved === 1) {
			frappe.throw(__('Please save/update the form before creating sales invoice'))
			return false
		}

		if (row.invoice_status === "Done") {
			frappe.throw(__('Invoice already created'))
			return false
		}

		if (frm.doc.room_folio === undefined || frm.doc.room_folio === '') {
			frappe.throw(__('Room Folio is required to move'))
			return false
		}

		let index = frm.doc.split_bill_customer.findIndex((e) => e.name == cdn)

		frappe.call({
			method: "sajha_menu.sajha_menu.doctype.tables.tables.moveToRoomFolio",
			args: { "doc": frm.doc, 'index': index },
			callback: function (r) {
				frm.reload_doc()
				window.open(`/app/sales-invoice/${r.message}`)
			}
		})

	}


})


// frappe.ui.form.on("Tables", "create_sales_invoice", async function (frm, cdt, cdn) {
// 	await frappe.call({
// 		method: "sajha_menu.api.createSalesInvoice",
// 		args: { "doc": frm.doc },
// 		callback: function (r) {
// 			if (r.message) {
// 				frappe.set_route("Form", "Sales Invoice", r.message)
// 			}
// 		}
// 	})
// })

frappe.ui.form.on("Tables", "move_to", async function (frm, cdt, cdn) {

	if (frm.fields_dict.room_customer.df.options.length) {
		if (frm.doc.room_customer === undefined || frm.doc.room_customer === "") {
			frappe.throw(__("This room folio have multiple customer, please select one customer name"))
			return
		}
	}



	await frappe.call({
		method: "sajha_menu.sajha_menu.doctype.tables.tables.moveToRoomFolio",
		args: { "doc": frm.doc, "index": -1 },
		callback: function (r) {
			if (r.message) {
				frm.orders = []
				frm.set_value('move_to_room', 0)
				window.open(`/app/sales-invoice/${r.message}`);
				frm.reload_doc()
			}
		}
	})
})





// frappe.ui.form.on("Table Order", 'refresh', function(frm){
// 	var rows = cur_frm.fields_dict['orders'].grid.grid_rows;
// 	console.log(rows);
// 	$.each(rows, function(index, row){
// 		row.wrapper.find(".grid-delete-row").hide();
// 	})
// })