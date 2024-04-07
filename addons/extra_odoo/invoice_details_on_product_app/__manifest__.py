# -*- coding: utf-8 -*-
{
	'name': "Invoice Details on Product",
	'author': "Astratech",
	'version': "16.0.1.0",
    'live_test_url': "https://youtu.be/zKxHNKuaIUg",
    "images":['static/description/main_screenshot.png'],
	'summary': "Product Invoice Details On Product View Invoice Quantity On Product Invoice Amount On Product Invoice Amount and Invoice Quantity On Product Invoice Amount and Quantity On Product Invoice Detail On Product Product Invoice Link Invoice Product Link",
	'description': """Invoice Quantity On Product Invoice Amount On Product Invoice Amount and Invoice Quantity On Product Invoice Amount and Quantity On Product Invoice Detail On Product Product Invoice Link Invoice Product Link
					""",
    "license" : "OPL-1",
	"live_test_url":'https://youtu.be/zKxHNKuaIUg',
	"images":['static/description/main_screenshot.png'],
    'depends': ['base', 'product','account','sale_management','purchase'],
	'data': [
			'views/product_invoice_link_view.xml',
			],
	'installable': True,
	'auto_install': False,
	'application': False,
	'category': "Product",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
