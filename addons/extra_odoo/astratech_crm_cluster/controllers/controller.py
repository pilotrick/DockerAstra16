
from odoo.http import request, route, JsonRPCDispatcher, Response
import xml.etree.ElementTree as ET
import base64
import json
from odoo import http
import secrets
import random
import hashlib
from werkzeug import exceptions, wrappers
from odoo.tools import date_utils
import logging


_logger = logging.getLogger(__name__)


def alternative_json_response(self, result=None, error=None):
    code = 200
    if error is not None:
        response = error
    if result is not None:
        response = result
        if 'code_status' in result:
            code = result['code_status']
            response.pop('code_status')

    return request.make_json_response(response, status=code)


def successful_response(status, dict_data):
    resp = wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        # headers = None,
        response=json.dumps(
            dict_data, ensure_ascii=False),
    )
    # Remove cookie session
    resp.set_cookie = lambda *args, **kwargs: None
    return resp


def error_response(status, error, error_descrip):

    content_type = request.httprequest.headers.get('Content-Type', '')

    if 'application/json' in content_type:
        request._response = alternative_json_response.__get__(
            request, JsonRPCDispatcher)
        response = {
            'code_status': status,
            'error': error,
            'error_descrip': error_descrip,
        }

        return response

    resp = wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        # headers = None,
        response=json.dumps({
            'error': error,
            'error_descrip': error_descrip,
        }, ensure_ascii=False),
    )
    # Remove cookie session
    resp.set_cookie = lambda *args, **kwargs: None
    return resp


def json_response(status, dict_data):
    request._response = alternative_json_response.__get__(request, JsonRPCDispatcher)
    dict_data['code_status'] = status
    return dict_data


def get_partner(data):
    partner = request.env['res.partner'].sudo()
    partner_id = partner.search([
        ('phone', '=', data.get('phone'))], limit=1)

    if partner_id:
        partner_id.update(data)
    else:
        partner_id = partner.create(data)
    return partner_id


def get_token_register(token):

    respond = request.env['token.register'].sudo().search([
        ('token', '=', token)], limit=1)

    return respond.token


class CRMApi(http.Controller):
    @route("/api/crm/customer", type='json', cors='*', csrf=False, auth="public", methods=["POST"])
    def crm_api_customer(self, **kwargs):
        x_astra_access_token = request.httprequest.headers.get('x-astra-access-token')

        if not x_astra_access_token:
            json_resp = {
                "error_descrip": "No access token was provided in request header!",
                "error": 'no_x_astra_access_token'
            }
            _logger.error(json_resp)
            return json_response(400, json_resp)

        token = get_token_register(x_astra_access_token)
        if not token:
            json_resp = {
                "error_descrip": "Token is invalid!",
                "error": 'invalid_token'
            }
            _logger.error(json_resp)
            return json_response(401, json_resp)

        data = json.loads(request.httprequest.data)
        data_input = [
            'name',
            'email',
            'pregnancy',
            'height',
            'weight',
            'bariatric',
            'diseases',
            'phone',
            'birthday',
            'IMC',
            'appliesTo'
        ]
    
        mandatory_input = [
            'name',
            'email',
            'pregnancy',
            'phone'
        ]
        fields_require = []
        for m in mandatory_input:
            if m not in data:
                fields_require.append(m)

        if fields_require:
            json_resp = {
                "error_descrip": "These field are required %s" % str(fields_require),
                "error": 'fields_required'
            }
            _logger.error(json_resp)
            return json_response(400, json_resp)

        partner_data = {}
        for d in data_input:
            partner_data[d] = data.get(d, False)

        partner = get_partner(partner_data)
        partner_data['partner_id'] = partner.id
        whatsapp_tag = request.env.ref('astratech_crm_cluster.whatsapp_tag')
        crm = request.env['crm.lead'].sudo()

        data_lead = crm.search([
            ('partner_id', '=', partner.id),
            ('stage_id', '=', request.env.ref('crm.stage_lead1').id)
        ],
            limit=1
        )

        if not data_lead:
            data_lead = crm.create(
                {
                    'partner_id': partner.id,
                    'name': 'Registro Whatsapp de: %s' % partner_data.get('name'),
                    'tag_ids': [(4, whatsapp_tag.id)],

                }
            )
        json_resp = {
            "info": "Register Correct %s" % str(partner_data.get('name')),
            'id': data_lead.id,
            'customer_id': partner.id,
            'state': data_lead.stage_id.name,
            "succes": 'correct_record'
        }
        _logger.error(json_resp)
        return json_response(200, json_resp)