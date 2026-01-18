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
    
    # Get Sales Order data grouped by item_group
    so_query = """
        SELECT 
            so_item.item_group,
            SUM(so_item.qty) as so_qty,
            SUM(so_item.amount) as so_amount
        FROM 
            `tabSales Order Item` so_item
        INNER JOIN 
            `tabSales Order` so ON so.name = so_item.parent
        WHERE 
            so.docstatus = 1
            {so_conditions}
        GROUP BY 
            so_item.item_group
    """.format(so_conditions=conditions.get('so_conditions', ''))
    
    # Get Stock Entry data grouped by item_group
    se_query = """
        SELECT 
            se_item.item_group,
            SUM(se_item.qty) as se_qty,
            SUM(se_item.amount) as se_amount
        FROM 
            `tabStock Entry Detail` se_item
        INNER JOIN 
            `tabStock Entry` se ON se.name = se_item.parent
        WHERE 
            se.docstatus = 1
            {se_conditions}
        GROUP BY 
            se_item.item_group
    """.format(se_conditions=conditions.get('se_conditions', ''))
    
    so_data = frappe.db.sql(so_query, filters, as_dict=1)
    se_data = frappe.db.sql(se_query, filters, as_dict=1)
    
    # Create dictionaries for easy lookup
    so_dict = {row.item_group: row for row in so_data}
    se_dict = {row.item_group: row for row in se_data}
    
    # Get all unique item groups
    all_item_groups = set(so_dict.keys()) | set(se_dict.keys())
    
    # Combine the data
    data = []
    for item_group in sorted(all_item_groups):
        so_row = so_dict.get(item_group, {})
        se_row = se_dict.get(item_group, {})
        
        so_qty = flt(so_row.get('so_qty', 0))
        so_amount = flt(so_row.get('so_amount', 0))
        se_qty = flt(se_row.get('se_qty', 0))
        se_amount = flt(se_row.get('se_amount', 0))
        
        data.append({
            'item_group': item_group,
            'so_qty': so_qty,
            'so_amount': so_amount,
            'se_qty': se_qty,
            'se_amount': se_amount,
            'gp': so_amount - se_amount
        })
    
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
            # Link Stock Entry to Sales Order through custom field
            se_conditions.append(f"AND se.custom_sales_order IN ({so_list})")
    
    return {
        'so_conditions': ' '.join(so_conditions),
        'se_conditions': ' '.join(se_conditions)
    }