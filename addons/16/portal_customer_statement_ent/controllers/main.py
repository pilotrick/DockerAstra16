# -*- coding: utf-8 -*-

from odoo import http, _, fields 
from odoo.http import request, content_disposition
from datetime import datetime, timedelta
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

from odoo.exceptions import UserError

from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape

import json


class CustomerPortal(CustomerPortal):

    @http.route(['/my/custom/customer/statements'], type='http', auth="user", website=True)
    def portal_my_customer_statement_custom(self, **kw):
        if not request.env.user.partner_id.allow_print_statement_portal:
            return request.redirect("/")
        response = super(CustomerPortal, self)
        values = {}
        partner_id = request.env.user.partner_id
        values.update({
            'partner_id' : partner_id,
            'default_url': '/my/custom/customer/statements',
            'page_name': 'custom_customer_statement',
        })
        return request.render("portal_customer_statement_ent.print_filter_customer_statement", values)
    
    def _get_statement_report_options_custom(self, **kw):
        partner_ids = request.env['res.partner'].search(['|', ('commercial_partner_id', '=', request.env.user.partner_id.id), ('id', '=', request.env.user.partner_id.commercial_partner_id.id)])
        return {
            'unfolded_lines': [],
            'date': {'string': 'From %s to %s'%(kw.get('date_from'), kw.get('date_to')), 'period_type': 'custom', 'mode': 'range', 'strict_range': False, 'date_from': kw.get('date_from'), 'date_to':  kw.get('date_to'), 'filter': 'custom'},
            'account_type': [{'id': 'receivable', 'name': 'Receivable', 'selected': False}, {'id': 'payable', 'name': 'Payable', 'selected': False}], 
            'all_entries': False ,
            'partner': True,
            'partner_ids': partner_ids.ids,
            'partner_categories': [],
            'selected_partner_ids': partner_ids.ids,
            'selected_partner_categories': [],
            'unfold_all': False,
            'unreconciled': False,
            'unposted_in_period': True,
            'headers': [[{}, {'name': 'JRNL'}, {'name': 'Account'}, {'name': 'Ref'}, {'name': 'Due Date', 'class': 'date'}, {'name': 'Matching Number'}, {'name': 'Initial Balance', 'class': 'number'}, {'name': 'Debit', 'class': 'number'}, {'name': 'Credit', 'class': 'number'}, {'name': 'Balance', 'class': 'number'}]]
        }

    @http.route('/custom/account_reports', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def get_statement_report_custom(self, model, **kw):
        if not request.env.user.partner_id.allow_print_statement_portal:
            return request.redirect("/")
        uid = request.session.uid
        account_report_model = request.env['account.report']
        options = self._get_statement_report_options_custom(**kw)
        cids = request.httprequest.cookies.get('cids', str(request.website.company_id.id or request.env.user.company_id.id))
        allowed_company_ids = [int(cid) for cid in cids.split(',')]
        report_obj = request.env[model].with_user(uid).with_context(allowed_company_ids=allowed_company_ids).sudo()
        report_name = report_obj.get_report_filename(options)
        try:
            response = request.make_response(
                report_obj.get_pdf(options),
                headers=[
                    ('Content-Type', account_report_model.get_export_mime_type('pdf')),
                    ('Content-Disposition', content_disposition(report_name + '.pdf'))
                ]
            )
            return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
