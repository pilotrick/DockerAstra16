# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Portal Customer / Vendor Statements PDF',
    'version' : '15.0.0.0',
    'category': 'Accounting/Accounting',
    'depends' : [
        'account_reports',
        'portal',
        'website',
     ],
    'author': 'Astratech',
    'images': ['static/description/image.jpg'],
    'price': 99.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': 'Partner Ledger Report Print from Customer Portal Customer Statements and Vendor Statements Print from Website',
    'website': 'www.probuse.com',
    'live_test_url' : 'http://probuseappdemo.com/probuse_apps/portal_customer_statement_ent/318',#'https://youtu.be/fIx9DAu9nmI',
    'description': ''' 
Partner Ledger Report Print from Customer Portal
Portal Customer / Vendor Statements
Partner Ledger Report Print from Customer Portal Customer Statements and Vendor Statements Print from Website
 ''',
    'data' : [
        'views/partner_view.xml',
        'views/template.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
