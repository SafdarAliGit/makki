import frappe
from frappe.utils import nowdate
from frappe import _
@frappe.whitelist()
def get_sales_order_items(sales_order):
    """
    Fetch items from Sales Order's Packed Items child table
    Only returns data if the Sales Order is submitted
    
    Args:
        sales_order (str): Sales Order name
        
    Returns:
        list: List of dictionaries containing item details
    """
    if not sales_order:
        frappe.throw("Sales Order is required")
    
    # Check if Sales Order exists and is submitted
    so_doc = frappe.get_doc("Sales Order", sales_order)
    
    if so_doc.docstatus != 1:
        frappe.throw(f"Sales Order {sales_order} is not submitted")
    
    # Fetch packed items from Sales Order
    total_qty = so_doc.get("total_qty",0)
    items = frappe.get_all(
        "Sales Order Item",
        filters={"parent": sales_order, "parenttype": "Sales Order"},
        fields=[
            "item_code",
            "item_group",
            "qty",
            "uom",
            "rate",
            "amount"
        ],
        order_by="idx"
    )
    data = {
        "items": items,
        "total_qty": total_qty
    }
    return data
    



@frappe.whitelist()
def create_material_issue_from_so(sales_order):
    """Create and return Material Issue Stock Entry from Sales Order"""

    # Get Sales Order
    so = frappe.get_doc("Sales Order", sales_order)
    
    # Validate
    if so.status == "Cancelled":
        frappe.throw(_("Cannot create Material Issue from cancelled Sales Order"))
    
    if not so.items:
        frappe.throw(_("Sales Order has no items"))
    
    # Get source warehouse
    source_warehouse = so.set_warehouse
    if not source_warehouse:
        frappe.throw(_("No Source warehouse found"))
    
    # Create new Stock Entry
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Issue"
    stock_entry.purpose = "Material Issue"
    stock_entry.custom_sales_order = sales_order
    stock_entry.project = so.project
    stock_entry.company = so.company
    stock_entry.posting_date = nowdate()
    stock_entry.set_posting_time = 1
    stock_entry.remarks = _("Material Issue from Sales Order {0}").format(sales_order)
    
    # Add items from Sales Order
    for item in so.items:
        # Skip non-stock items
        item_doc = frappe.get_cached_doc("Item", item.item_code)
        if not item_doc.is_stock_item:
            continue
        
               
        # Add to Stock Entry items
        se_item = stock_entry.append("items")
        se_item.s_warehouse = source_warehouse
        se_item.item_code = item.item_code
        se_item.qty = item.qty
        se_item.uom = item.uom
        se_item.stock_uom = item_doc.stock_uom,
        se_item.allow_zero_valuation_rate = 1
    
    # Check if any items were added
    
    
    # Insert the document (but don't submit)
    stock_entry.insert(ignore_permissions=True)
    
    # Return document name for opening
    return stock_entry



