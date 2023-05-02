
{
    'name': 'Top/Least Selling Product Report',
    'version': '16.0.1.0.0',
    'summary': 'Top Selling and Least Selling Product Reports',
    'description': 'Top Selling Products,Fast Moving Products,Most Selling Products,Top Growing Products,Least Selling Products,',
     'author': 'Banibro IT Solutions Pvt Ltd.',
    'company': 'Banibro IT Solutions Pvt Ltd.',
    'website': 'https://banibro.com',
    'depends': ['base', 'sale_management', 'stock', 'sale'],
    'category': 'Sale',
    'data': ['wizard/top_selling_wizard.xml',
             'report/top_selling_report.xml',
             'report/top_selling_report_template.xml',
             'security/ir.model.access.csv'
             ],
    'images': ['static/description/banner.png'],
     'license': 'AGPL-3',
    'email': "support@banibro.com",
    'installable': True,
    'auto_install': False,
    'application': False,
}
