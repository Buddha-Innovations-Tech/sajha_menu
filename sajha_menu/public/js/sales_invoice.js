frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.set_df_property('menu', 'hidden', 1)
        }
    },

    menu(frm) {
        frappe.call({
            method: "sajha_menu.sajha_menu.replace_name.replace_name",
            freeze: true,
            args: {
                'doc': frm.doc
            },
            always: function (d) {
                frm.reload_doc()
            }
        })
    }
})


