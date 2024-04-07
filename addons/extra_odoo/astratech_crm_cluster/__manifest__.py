{
    'name': "Api CRM Cluster Bot",
    'summary': """
    This will connect to client's whatsapp bot
    """,

    'author': "Astra Tech SRL",
    'website': "https://astratech.com.do",
    'category': 'Accounting',
    'version': "16.0.0.0.1",
    'depends': ['sale_crm'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/whatsapp_bot.xml',
        'views/token_registre.xml',
        ],

    'installable': True
}
