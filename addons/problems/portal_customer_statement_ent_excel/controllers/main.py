# -*- coding: utf-8 -*-

from odoo import http, _ 
from odoo.http import request, content_disposition
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape

import json


class CustomerPortal(CustomerPortal):

    @http.route('/custom/account_reports', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def get_statement_report_custom(self, model, **kw):
        if not request.env.user.partner_id.allow_print_statement_portal:
            return request.redirect("/")
        if kw.get('report_type') == 'excel':
            uid = request.session.uid
            account_report_model = request.env['account.report']
            options = self._get_statement_report_options_custom(**kw)
            cids = request.httprequest.cookies.get('cids', str(request.website.company_id.id or request.env.user.company_id.id))
            allowed_company_ids = [int(cid) for cid in cids.split(',')]
            report_obj = request.env[model].with_user(uid).with_context(allowed_company_ids=allowed_company_ids).sudo()
            report_name = report_obj.get_report_filename(options)
            try:
                response = request.make_response(
                    report_obj.get_xlsx(options),
                    headers=[
                        ('Content-Type', account_report_model.get_export_mime_type('xlsx')),
                        ('Content-Disposition', content_disposition(report_name + '.xlsx'))
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
        else:
            return super(CustomerPortal, self).get_statement_report_custom(model, **kw)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
