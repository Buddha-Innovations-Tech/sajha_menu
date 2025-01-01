// Copyright (c) 2023, tuna and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Category', {
  refresh: function (frm) {
    // frappe.call({
    //   method: 'sajha_menu.api.getItems',
    //   args: { items: frm.items },
    // });
  },
});

frappe.ui.form.on('Sub Category Items', {
  item_code(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    frappe
      .call({
        method: 'sajha_menu.api.getItemRate',
        args: { itemCode: row.item_code },
      })
      .done((r) => {
        let index = frm.doc.items.findIndex((e) => e.name === cdn);

        if (r['message'].toString().includes("object is not subscriptable")) {

          frm.reload_doc();
          frappe.throw(__("Item price not found for the item"))
          return
        }

        frm.doc.items[index].rate = r['message']['item'];


        frm.refresh_fields();
      });
  },


});
