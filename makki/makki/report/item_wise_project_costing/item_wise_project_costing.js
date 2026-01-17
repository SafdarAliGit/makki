// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Item Wise Project Costing"] = {
	"filters": [
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 1,
			"on_change": function() {
				// Reset dependent filters when customer changes
				frappe.query_report.set_filter_value('project', '');
				frappe.query_report.set_filter_value('sales_order', []);
			}
		},
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"reqd": 1,
			"get_query": function() {
				var customer = frappe.query_report.get_filter_value('customer');
				if (customer) {
					return {
						"filters": {
							"customer": customer
						}
					};
				}
			},
			"on_change": function() {
				// Reset sales order when project changes
				frappe.query_report.set_filter_value('sales_order', []);
			}
		},
		{
			"fieldname": "sales_order",
			"label": __("Sales Order"),
			"fieldtype": "MultiSelectList",
			"reqd": 1,
			"get_data": function(txt) {
				var customer = frappe.query_report.get_filter_value('customer');
				var project = frappe.query_report.get_filter_value('project');
				
				var filters = {
					'docstatus': 1
				};
				
				if (customer) {
					filters['customer'] = customer;
				}
				
				if (project) {
					filters['project'] = project;
				}
				
				return frappe.db.get_link_options('Sales Order', txt, filters);
			}
		}
	]
};