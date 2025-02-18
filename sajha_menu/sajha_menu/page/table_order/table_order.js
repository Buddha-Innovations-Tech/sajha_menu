

frappe.pages['table-order'].on_page_load = function (wrapper) {

	new MyPage(wrapper);


}




MyPage = Class.extend({
	init: function (wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Table Orders',
			single_column: true
		});

		frappe.realtime.on('table_refresh', ({ data }) => {
			this.refresh()
		});

		//make page
		this.filters();
		this.make();
	},




	refresh: async function () {

		// window.location.reload()
		let me = $(this);
		let company = this.page.fields_dict['company'].value
		// let fromDate = this.page.fields_dict['fromDate'].value
		// let toDate = this.page.fields_dict['toDate'].value
		// let status = me[0].page.fields_dict['status'].value

		await frappe.call({
			method: "sajha_menu.sajha_menu.page.table_order.table_order.refreshKot",
			args: { "company": company },
			callback: function (r) {
				$("#body-main")[0].innerHTML = frappe.render_template(r.message)
			}
		})
	},


	filters: async function () {
		let me = $(this);

		async function changesTab() {
			let company = me[0].page.fields_dict['company'].value

			await frappe.call({
				method: "sajha_menu.sajha_menu.page.table_order.table_order.applyFilter",
				args: { "company": company },
				callback: function (r) {
					$("#body-main")[0].innerHTML = frappe.render_template(r.message)
				}
			})
			// push dom element to page
		}



		await frappe.call({
			method: "sajha_menu.sajha_menu.page.table_order.table_order.getCompanyList",
			callback: function (r) {
				companyName = r.message
			}
		})

		this.page.add_field({
			label: 'Company',
			fieldtype: 'Link',
			fieldname: 'company',
			options: "Company",
			change() {
				changesTab();
			}
		});

	},

	make: async function () {
		// grab the class 
		let me = $(this);


		// body content
		let body = await frappe.call({
			method: "sajha_menu.sajha_menu.page.table_order.table_order.getBodyHTML",
			callback: function (r) {
			}
		})
		// push dom element to page
		$(frappe.render_template(body.message, this)).appendTo(this.page.main)


		// execute methods
		// tableName();
	}

	// end of class
})



