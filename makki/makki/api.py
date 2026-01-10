import frappe

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
    