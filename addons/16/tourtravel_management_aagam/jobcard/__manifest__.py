# -*- coding: utf-8 -*-
{
    'name': "Job Card",
    'category': 'Sales',
    'version': '16.0.1',
    'summary': """
        Job Card
    """,
    'description': """
        Job Card""",
    'depends': [
        'base', 'base_setup', 'product', 'account',
        'sale_management', ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/sale_order_view.xml',
        # 'views/reports.xml',
        'views/report_job_card.xml',
        # 'views/res_config_settings_views.xml',
        'views/job_card_view.xml',
        # 'views/menus.xml',
        # 'views/sequence.xml',
    ],
    'qweb': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'support': ': business@aagaminfotech.com',
    'author': 'Aagam Infotech',
    'website': 'http://aagaminfotech.com',
    'installable': True,
    'license': 'AGPL-3',
}
