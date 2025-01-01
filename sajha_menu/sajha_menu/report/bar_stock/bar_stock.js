// Copyright (c) 2023, tuna and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bar Stock"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand",
		},
	]
};
