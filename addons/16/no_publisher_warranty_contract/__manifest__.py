# -*- coding: utf-8 -*-
{
    'name': "Bypass publisher Warranty Contract",

    'summary': """Bypass publisher Warranty Contract""",

    'description': """
        This module will enable you to use Odoo enterprise for free.
    """,

    'author': "Babatope Ajepe",
    'website': "https://ajepe.github.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    'auto_install': True,

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        #'views/res_config_settings_views.xml'
        'data/ir_cron_data.xml',
    ],

    
    'assets': {
        'web.assets_qweb': [
            'no_publisher_warranty_contract/static/src/**/*.xml',
        ],
    },
    "pre_init_hook": "run_pre_init_hook",
    "pre_init_hook": "run_post_init_hook",
}
