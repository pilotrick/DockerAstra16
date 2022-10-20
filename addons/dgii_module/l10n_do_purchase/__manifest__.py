{
    'name': "Purchase Journal",
    'version': '14.0.1.0.0',
    'summary': """
    Add new field "Purchase Journal" in suppliers if this field is set
    the invoices generated for these suppliers take this journal by default.
    """,
   
    'author': 'Astra Tech SRL',
    'website': 'https://astratech.com.do',
    'license': 'LGPL-3',
    'category': 'Localization',
    'depends': ['l10n_do_accounting', 'purchase'],
    'data': ['views/res_partner_views.xml'],
}