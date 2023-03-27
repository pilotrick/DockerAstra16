{
    'name': "Currency of Dominican Banks",
    'summary': """
    Updates company secondary currency rates from dominican banks
    """,

    'author': "Astra Tech SRL",
    'website': "https://astratech.com.do",
    'category': 'Accounting',
    'version': "15.0.0.0.1",
    'depends': ['account'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/ir_config_parameter_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True
}
