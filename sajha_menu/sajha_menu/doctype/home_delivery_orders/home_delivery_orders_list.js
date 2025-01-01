frappe.listview_settings['Home Delivery Orders'] = {

    get_indicator: function (doc) {
        if (doc.status === "Order Received") {
            return [__("Order Received"), "gray", "status,=,Order Received"];
        } else if (doc.status === "Order Confirmed") {
            return [__("Order Confirmed"), "yellow", "status,=,Order Confirmed"];
        } else if (doc.status === "ON THE WAY") {
            return [__("ON THE WAY"), "green", "status,=,ON THE WAY"];
        } else if (doc.status === "DELIVERED") {
            return [__("DELIVERED"), "green", "status,=,DELIVERED"];
        } else if (doc.status === "Order Cancelled") {
            return [__("Order Cancelled"), "red", "status,=,Order Cancelled"];
        }

    },
}