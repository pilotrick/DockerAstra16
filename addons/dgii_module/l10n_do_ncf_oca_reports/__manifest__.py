# Part of Domincana Premium.
# See LICENSE file for full copyright and licensing details.
# © 2021 Jeffry J. De La Rosa <jeffry@astratech.com.do>

{
    "name": "Declaraciones DGII",
    "summary": """
        Este módulo extiende las funcionalidades del l10n_do_accounting,
        integrando los reportes de declaraciones fiscales""",
    "author": "Indexa, SRL, " "iterativo SRL, " "Astra Tech SRL",
    "license": "LGPL-3",
    "category": "Accounting",
    "version": "16.0.1.1.0",
    # any module necessary for this one to work correctly
    "depends": ["l10n_do_accounting"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/res_partner_views.xml",
        "views/account_account_views.xml",
        "views/account_invoice_views.xml",
        "views/dgii_report_views.xml",
        "wizard/dgii_report_regenerate_wizard_views.xml",
    ],

    'assets': {
        'web.assets_backend': [
            'l10n_do_ncf_oca_reports/static/src/less/dgii_reports.css',
            'l10n_do_ncf_oca_reports/static/src/js/widget.js',
        ]

    }

}
