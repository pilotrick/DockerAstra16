# -*- coding: utf-8 -*-

{
    "name": 'Odoo Change Vendor in Purchase Order',
    "author": "Astratech",
    "version": '16.0.1.0',
    "live_test_url": "",
    "images":['static/description/main_screenshot.png'],
    "summary": "Change Vendor in Purchase Order",
    "description": """ 
                    
Odoo Change Vendor in Purchase Order
                    """,
    "license" : "OPL-1",
    "depends": ['base','purchase' , 'stock'],
    "data": [
            'security/ir.model.access.csv',
            'security/security.xml',
            'wizard/update_vendor_view.xml',
            'views/purchase_order_view.xml',
            ],
    "installable": True,
    "auto_install": False,
    "price": 00,
    "currency": "EUR",
    "category": 'Sales',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
