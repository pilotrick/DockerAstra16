# See LICENSE file for full copyright and licensing details.
{
    'name': 'Hospital',
    'version': '16.0.3.3.0',
    'category': 'Customization',
    'summary': 'Maintaining records of doctors and patients',

    'author': 'Astratech',
    'website': 'https://t.me/ostapec_serg',

    'depends': [
        'base',
    ],

    'data': [
        'security/hr_hospital_odooschool_groups.xml',
        'security/ir.model.access.csv',
        'security/disease_security.xml',
        'data/disease_data.xml',
        'views/hr_hospital_odooschool_menus.xml',
        'views/diagnosis_views.xml',
        'wizard/create_appointment.xml',
        'wizard/add_diagnosis.xml',
        'wizard/change_doctor.xml',
        'wizard/change_visit_time.xml',
        'wizard/hospital_report.xml',
        'wizard/week_schedule.xml',
        'views/doctor_views.xml',
        'views/analysis_views.xml',
        'views/analysis_card_views.xml',
        'views/patient_visit_views.xml',
        'views/patient_views.xml',
        'views/disease_views.xml',
        'views/disease_category_views.xml',
        'views/contact_person_views.xml',
        'views/doctor_schedule_views.xml',
        'views/hr_history_changing_doctor.xml',
        'reports/doctor_report_templates.xml',
        'reports/report.xml',
    ],

    'demo': [
        'data/hr_hospital_odooschool_demo.xml',
    ],

    'images': [
        'static/description/icon.png',
    ],

    'currency': 'EUR',
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
