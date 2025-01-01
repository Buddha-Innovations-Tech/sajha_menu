frappe.ui.form.on('Item', {
    refresh:function(frm) {
        var item_group = frm.doc.item_group.split("-")[0].trim();
        if (item_group === "Bar Item") {
            frm.set_df_property('is_main_bottle', "hidden", 0);
            frm.set_df_property('bar_item_size_ml', "hidden", 0);
            frm.set_df_property('bar_item_size_ml', "mandatory", 1);
            frm.set_df_property('brand','mandatory',1);
            frm.fields_dict['section_break_11'].collapse();
            frm.refresh_field();
        }
    },
    item_group:function(frm) {
        var item_group = frm.doc.item_group.split("-")[0].trim();
        if (item_group === "Bar Item") {
            frm.set_df_property('is_main_bottle', "hidden", 0);
            frm.set_df_property('bar_item_size_ml', "hidden", 0);
            frm.fields_dict['section_break_11'].collapse();
            frm.refresh_field();
        }
    },
    before_save: async function(frm){
        var item_group = frm.doc.item_group.split("-")[0].trim();
        if (item_group === "Bar Item") {
            frm.doc.is_stock_item = 1;
            if(frm.doc.bar_item_size_ml == 0){
                frappe.throw(
                    msg='Bar Item Size cannot be empty for bar items',
                    title='Denied!',
                )
            }else if (typeof(frm.doc.brand) == 'undefined'){
                frappe.throw(
                    msg='Brand cannot be empty for bar items',
                    title='Denied!',
                )
            }
        }
    }
});
