import frappe


def delivery_slip_connector_socketio(arg1, arg2):
    print("===========Connector")
    frappe.publish_realtime(
        "custom_connector", "{'message':'test','custom_app'}")
