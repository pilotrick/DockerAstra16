# -*- coding: utf-8 -*-
{
    'name': "Visualización del detalle e indicadores de un coste en destino o liquidación",

    'summary': """
        Incluye una vista con el detalle del coste en destino o liquidación 
        y una pestaña con indicadores de interés, así como la posibilidad 
        de imprimir la liquidación y sus indicadores""",

    'description': """
        Incluye una vista con el detalle del coste en destino o liquidación 
        basado en las transferencias asociadas al mismo. 
        Incluye una pestaña con indicadores de interés generados por la información 
        del detalle del coste en destino. Incluye una opción de impresión de la liquidación 
        y sus indicadores.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '16.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase_stock', 'stock_landed_costs',  'landed_cost_vo'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'report/report_stock_landed_costs_indicators.xml',
        'report/report_stock_landed_costs_indicators_view.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'lc_detail_and_indicators/static/src/tabble_template.xml',
            'lc_detail_and_indicators/static/src/tabble_widget.js',
        ],
    },
}
