# -*- coding: utf-8 -*-

{
    'name': "Autodeterminacion TSS",

    'summary': """
        Autodeterminacion TSS
        """,

    'description': """

    """,

    'author': 'Astra Tech SRL',
    'website': 'https://astratech.com.do',
    'category': 'Localization',
    'version': '14.0.0.1',

    'depends': ['hr_payroll', 'l10n_do_hr_payroll'],

    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/tss_report_views.xml',
        'wizard/tss_report_regenerate_wizard_views.xml'

    ],

}
