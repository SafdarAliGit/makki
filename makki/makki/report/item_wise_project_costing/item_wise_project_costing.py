# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "item_group",
            "label": _("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 200
        },
        {
            "fieldname": "so_qty",
            "label": _("SO Qty"),
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "so_amount",
            "label": _("SO Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "se_qty",
            "label": _("SE Qty"),
            "fieldtype": "Float",
            "width": 150
        },
        {
            "fieldname": "se_amount",
            "label": _("SE Amount"),
            "fieldtype": "Currency",
            "width": 170
        },
        {
            "fieldname": "gp",
            "label": _("Gross Profit"),
            "fieldtype": "Currency",
            "width": 150
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    # Combined query to get data grouped by Item Group only
    query = """
        SELECT 
            item.item_group,
            COALESCE(SUM(so_item.qty), 0) as so_qty,
            COALESCE(SUM(so_item.amount), 0) as so_amount,
            COALESCE(SUM(se_item.qty), 0) as se_qty,
            COALESCE(SUM(se_item.amount), 0) as se_amount
        FROM 
            `tabItem` item
        LEFT JOIN 
            `tabSales Order Item` so_item ON so_item.item_group = item.item_group
        LEFT JOIN 
            `tabSales Order` so ON so.name = so_item.parent AND so.docstatus = 1 {so_conditions}
        LEFT JOIN 
            `tabStock Entry Detail` se_item ON se_item.item_group = item.item_group
        LEFT JOIN 
            `tabStock Entry` se ON se.name = se_item.parent AND se.docstatus = 1 {se_conditions}
        WHERE 
            (so_item.name IS NOT NULL OR se_item.name IS NOT NULL)
        GROUP BY 
            item.item_group
        ORDER BY 
            item.item_group
    """.format(
        so_conditions=conditions.get('so_conditions', ''),
        se_conditions=conditions.get('se_conditions', '')
    )
    
    data = frappe.db.sql(query, filters, as_dict=1)
    
    # Calculate GP and GP percentage for each Item Group
    for row in data:
        row.gp = flt(row.so_amount) - flt(row.se_amount)
    
    return data

def get_conditions(filters):
    so_conditions = []
    se_conditions = []
    
    if filters.get("project"):
        so_conditions.append("AND so.project = %(project)s")
        se_conditions.append("AND se.project = %(project)s")
    
    if filters.get("customer"):
        so_conditions.append("AND so.customer = %(customer)s")
    
    if filters.get("sales_order"):
        # Handle multiple sales orders
        sales_orders = filters.get("sales_order")
        if isinstance(sales_orders, str):
            sales_orders = [sales_orders]
        
        if sales_orders:
            so_list = ", ".join([f"'{so}'" for so in sales_orders])
            so_conditions.append(f"AND so.name IN ({so_list})")
            
            # Link Stock Entry to Sales Order through Stock Entry Detail
            se_conditions.append(f"AND se.custom_sales_order IN ({so_list})")
    
    return {
        'so_conditions': ' '.join(so_conditions),
        'se_conditions': ' '.join(se_conditions)
    }