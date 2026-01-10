frappe.ui.form.on('Project', {
    sales_order: function(frm) {
        if (frm.doc.sales_order) {
            frappe.call({
                method: 'makki.makki.api.get_sales_order_items',
                args: {
                    sales_order: frm.doc.sales_order
                },
                callback: function(r) {
                    if (r.message) {
                        // Clear existing items in your child table
                        frm.clear_table('custom_project_items');
                        
                        // Add items from Sales Order
                        r.message.items.forEach(function(item) {
                            let row = frm.add_child('custom_project_items');
                            row.item_code = item.item_code;
                            row.item_group = item.item_group;
                            row.qty = item.qty;
                            row.uom = item.uom;
                            row.rate = item.rate;
                            row.amount = item.amount;
                        });
                        
                        frm.refresh_field('custom_project_items');
                        frm.set_value('custom_total_qty', r.message.total_qty);
                    }
                }
            });
        }
    }
});