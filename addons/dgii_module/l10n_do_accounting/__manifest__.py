{
    "name": "Fiscal Accounting (Rep. Dominicana)",
    "summary": """
        Este módulo implementa la administración y gestión de los números de
         comprobantes fiscales para el cumplimento de la norma 06-18 de la
         Dirección de Impuestos Internos en la República Dominicana.""",
    "author": "Astratech",
    "category": "Localization",
    "license": "LGPL-3",
    "version": "16.0.1.0.0",
    # any module necessary for this one to work correctly
    "depends": ["l10n_do", "l10n_latam_invoice"],
    # always loaded
    "data": [
       # 'data/ir_config_parameters.xml',
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/l10n_latam.document.type.csv",
        "wizard/account_move_reversal_views.xml",
        "views/account_tax_views.xml",
        "wizard/account_move_cancel_views.xml",
        "wizard/account_debit_note_views.xml",
        "views/res_config_settings.xml",
        "wizard/account_fiscal_sequence_validate_wizard_views.xml",
        "views/account_fiscal_sequence_views.xml",
        "views/res_config_settings_view.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
        "views/account_journal_views.xml",
        "views/l10n_latam_document_type_views.xml",
        "views/report_invoice.xml",
        "views/account_journal_views.xml",
    ],

    'assets': {
        'web.assets_backend': [
            'l10n_do_accounting/static/src/js/l10n_do_accounting.js',
        ]

    },

    # only loaded in demonstration mode
    "installable": True,
    "auto_install": False,
    "application": False,
    "post_init_hook": "post_init_hook",
}
