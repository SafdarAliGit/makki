frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        // Add button to "Create" dropdown menu
        frm.add_custom_button('Create Stock Entry', function() {
            create_and_open_material_issue(frm);
        }, __('Create')); // <-- This adds it to the "Create" dropdown
    }
});

function create_and_open_material_issue(frm) {
    // Show loading indicator
    frappe.show_alert({
        message: __('Creating Material Issue...'),
        indicator: 'blue'
    });
    
    // Call server method to create Stock Entry
    frappe.call({
        method: 'makki.makki.api.create_material_issue_from_so',
        args: {
            'sales_order': frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.name) {
                // OPEN STOCK ENTRY DIRECTLY
                frappe.set_route('Form', 'Stock Entry', r.message.name);
                
                // Show success message
                frappe.show_alert({
                    message: __('Material Issue created successfully'),
                    indicator: 'green'
                });
            } else {
                frappe.msgprint(__('Failed to create Material Issue'));
            }
        },
        error: function(err) {
            frappe.msgprint(__('Error: ') + err.responseText);
        }
    });
}