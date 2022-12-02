{
    'name': 'Fleet Vehicle Log Fuel',
    'version':'1.2',
    'category': 'fleet/fuel',
    'description': """
This module adds the 'fuel' to fleet.
=============================================
    """,
    'license': 'OPL-1',
    'category': 'fleet/fuel',
    'depends': ['fleet'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/fleet_vehicle_cost_views.xml',
        'views/fleet_board_view.xml',
        'report/fleetVehicleLogFuel_report.xml',
        'report/fleetVehicleLogFuel_report_templates.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

