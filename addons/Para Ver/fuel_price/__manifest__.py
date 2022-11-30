
{
    "name": "Fuel Price",
    "summary": "Order Line Volume In Purchase and Report",
    "description": """Order Line Volume In Purchase and Report""",
    "version": "14.0.1.0.1",
    "category": 'Purchase/Purchase',
    "website": "https://www.warlocktechnologies.com/", 
    'author': 'Astratech',
    'company': 'Warlock Technologies',
    'maintainer': 'Warlock Technologies',
    "depends": ['fleet', 'base'],
    "data": [
        'security/ir.model.access.csv',
        'views/fuel_view.xml',
        'data/ir_cron.xml',
        # 'report/fleetVehicleLogFuel_report.xml',
        # 'report/fleetVehicleLogFuel_report_templates.xml'
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

