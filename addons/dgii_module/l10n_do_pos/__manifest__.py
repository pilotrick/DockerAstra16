# Copyright Adel Networks

{
    'name': "República Dominicana - POS",
    'summary': """
        Incorpora funcionalidades de facturación con NCF al POS
        """,
    'author': "Adel Networks S.R.L",
    'license': 'LGPL-3',
    'category': 'Localization',
    'version': '16.0.1.0.0',
    'depends': ['l10n_do_accounting', 'point_of_sale'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/pos_config.xml',
        'views/pos_view.xml',
        'views/pos_payment_method_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'l10n_do_pos/static/src/css/l10n_do_pos.css',
            'l10n_do_pos/static/src/js/models.js',
            'l10n_do_pos/static/src/js/Screens/PartnerListScreen/PartnerDetailsEdit.js',
            'l10n_do_pos/static/src/js/Screens/ReceiptScreen/OrderReceipt.js',
            'l10n_do_pos/static/src/js/Screens/TicketScreen/TicketScreen.js',
            'l10n_do_pos/static/src/js/Screens/PaymentScreen/PaymentScreen.js',
            'l10n_do_pos/static/src/xml/**/*',
        ],
    },
}
