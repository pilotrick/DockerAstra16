# -*- encoding: utf-8 -*-
{
    'name': "Requisicion",
    'version': '16.0.0.1',
    'sequence': 1,
    'summary': 'Requsiciones para el departamento de compras.',
    'category': 'Purchase',
    'description': """Requsiciones para el departamento de compras.""",
    'author': 'AstraTech',
    "depends" : ['sale', 'purchase','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/requisicion_view.xml',
        'security/requisicion_security.xml',
        'views/menu_requisicion.xml',
        'data/data.xml',
    ],
    'license': 'AGPL-3',
    # 'license': 'LGPLdd-3',
    'qweb': [], 
    'installable': True,
    'application': True,
    'auto_install': False,
}
# 'views/sale_order_line_report.xml'