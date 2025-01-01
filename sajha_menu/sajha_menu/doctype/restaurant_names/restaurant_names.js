// Copyright (c) 2023, tuna and contributors
// For license information, please see license.txt

frappe.ui.form.on('Restaurant names', {
	refresh: function (frm) {
		frappe.call({
			method: "sajha_menu.api.get_naming_series",
			args: {},
			callback: function (r) {
				let naming_series = r.message
				frm.set_df_property('naming_series', 'options', naming_series.split('\n'))
				frm.refresh_fields()
			}
		})
	}
});
