// Copyright (c) 2024, tuna and contributors
// For license information, please see license.txt

frappe.ui.form.on("Floor Plan", {
    refresh(frm) {

    },

    setup(frm) {
        frm.set_query("table_name", "table_list", function (doc) {
            return {
                filters: {
                    restaurant_names: ["in", [`${frm.doc.outlet_name}`]],
                }
            };
        });
    },
});
