# -*- coding: utf-8 -*-
{
    'name': "Tour and travel management in odoo, tour booking, tour packages, tour reservation in odoo",
    'category': 'Sales',
    'version': '16.0.6',
    'description': """
    Tour management, tour and travel management, tour booking, tour packages, tour reservation in odoo, hotel booking, hotel management for travel agency, tour and travel package, room reservation tour booking and travel management Visa and Passport Management Odoo Manage Hotels information custom tour creation Tour Itinerary odoo Agents management for tours in odoo 16,15, 14, 13, 12""",
    'summary': """
        Tour management, tour and travel management, tour booking, hotel booking for travel agency management tour reservation in odoo tour packages tour hotel management tour and travel package Agents management room reservation tour booking Visa and Passport Management Odoo Manage Hotels information custom tour creation Tour Itinerary odoo Agents management for tours in odoo 15 Tour Program Itinerary travel management in odoo 16 tour management 13 odoo travel Management travel booking Transport Booking
    """,
   
    #'depends': ['base','product', 'account', 'jobcard',],
    'depends': ['base', 'mass_mailing', 'sale_management'],
    # always loaded
    'data': [
        'security/tour_management_security.xml',
        'security/ir.model.access.csv',
        # 'views/assets.xml',
        'views/res_partner_view.xml',
        'views/tour_reservation_view.xml',
        'views/booking_service_view.xml',
        'views/booking_accomodation_view.xml',
        'views/flight_view.xml',
        'views/ferry_view.xml',
        'views/tour_views.xml',
        'views/travel_information_view.xml',
        'views/itinerary_view.xml',
        'views/sale_order_views.xml',
        'views/tour_visa_view.xml',
        'views/tour_deshboard_action.xml',
        'views/day_sheet_view.xml',
        'views/account_invoice_view.xml',
        'views/report_day_sheet.xml',
        'views/report_tour_reservation.xml',
        'views/report_tour_program.xml',
        'views/reports.xml',
        'views/res_config_settings_views.xml',
        'views/transfer_excursion_view.xml',
        'views/menus.xml',
        'views/sequence.xml',
        'views/report_invoice.xml',
        'views/account.xml',
        'views/accomodation_information_view.xml',
        'views/custom_booking_information_view.xml',
        'views/insurance_view.xml',
        'views/agent_commission_view.xml',
        'reports/tour_creator_report_action.xml',
        'reports/tour_creator_report_template.xml',
        'reports/tour_itinerary_report_template.xml',
        'reports/tour_itinerary_report_action.xml',
        'reports/tour_accommodation_report_action.xml',
        'reports/tour_accommodation_report_template.xml',
        'reports/tour_booking_report_action.xml',
        'reports/tour_booking_report_template.xml',
        'reports/flight_report_action.xml',
        'reports/flight_report_template.xml',
        'reports/custom_tour_booking_action.xml',
        'reports/custom_tour_booking_template.xml',
        'data/mail_data.xml',
        'data/visa_documentation_list.xml',


    ],
     # only loaded in demonstration mode
    'demo': [
    ],
    'images': [
        'static/description/images/tour_travel_banner_aagam.png',
    ],
    
    'installable': True,

    'assets': {
        'web.assets_backend': [
            'tourtravel_management_aagam/static/src/xml/**/*',
            '/tourtravel_management_aagam/static/src/js/tour_dashboard.js',
            '/tourtravel_management_aagam/static/src/js/Chart.js',
            '/tourtravel_management_aagam/static/src/css/nv.d3.css',
        ],
    },
    'license': 'OPL-1',
    'price': 230,
    'currency': 'USD',
    'support': ': business@aagaminfotech.com',
    'author': 'Aagam Infotech',
    'website': 'http://aagaminfotech.com',
}
