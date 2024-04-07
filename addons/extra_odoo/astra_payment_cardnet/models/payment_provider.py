# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import uuid
import json

import requests
from werkzeug.urls import url_encode, url_join

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from ..const import LIVE_URL, TEST_URL, SUPPORTED_CURRENCIES


_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('cardnet', "Cardnet")], ondelete={'cardnet': 'set default'})
    
    merchant_name = fields.Char(
        string="Merchant Name", required_if_provider='cardnet', groups='base.group_system')
    
    AVS = fields.Char(
        string="AVS", required_if_provider='cardnet', groups='base.group_system')
    
    merchant_number = fields.Char(
        string="Merchant Number", required_if_provider='cardnet', groups='base.group_system')
    
    merchant_terminal = fields.Char(
        string="Merchant Terminal", required_if_provider='cardnet', groups='base.group_system')
    
    merchant_terminal_amex = fields.Char(
        string="Merchant Terminal Amex", required_if_provider='cardnet', groups='base.group_system')
    
    merchant_type = fields.Char(
        string="Merchant Type", required_if_provider='cardnet', groups='base.group_system')
    fields.Selection(
        [
            ("draft", "Draft"),
            ("queue", "Queue"),
            ("active", "Active"),
            ("depleted", "Depleted"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
        copy=False,
    )
    
    TransactionType = fields.Selection(
        [
            ("0200", "Ventas Normal"),
            ("0100", "Preautorizacion"),
            ("2240", "Confirmacion de transaccion"),
        ],
        default="0200",
        string="Transaction Type", 
        equired_if_provider='cardnet',
        groups='base.group_system')
    
    @api.depends('code')
    def _compute_view_configuration_fields(self):
        """ Override of payment to hide the credentials page.

        :return: None
        """
        super()._compute_view_configuration_fields()
        self.filtered(lambda p: p.code == 'cardnet').update({
            'show_credentials_page': True,
            'show_payment_icon_ids': True,
            'show_pre_msg': True,
            'show_done_msg': True,
            'show_cancel_msg': True,
            'module_state': 'installed'
        })
        
        
    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist Cardnet acquirers when the currency is not supported. """
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in SUPPORTED_CURRENCIES:
            acquirers = acquirers.filtered(lambda a: a.provider != 'cardnet')

        return acquirers

    def _cardnet_make_request(
        self, endpoint, payload=None, method='POST', offline=False, idempotency_key=None
    ):
        """ Make a request to Cardnet API at the specified endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request
        :param dict payload: The payload of the request
        :param str method: The HTTP method of the request
        :param bool offline: Whether the operation of the transaction being processed is 'offline'
        :param str idempotency_key: The idempotency key to pass in the request.
        :return The JSON-formatted content of the response
        :rtype: dict
        :raise: ValidationError if an HTTP error occurs
        """
        self.ensure_one()
        provider_url = TEST_URL
        if self.state == "enabled":
            provider_url = LIVE_URL

        url = url_join(provider_url, endpoint)
        headers = {
            **self._get_cardnet_extra_request_headers(method),
        }
            
        if method == 'POST':
            payload = json.dumps(payload)
        # try:
        
        response = requests.request(method, url, data=payload, headers=headers, timeout=60)
        # Cardnet can send 4XX errors for payment failures (not only for badly-formed requests).
        # Check if an error code is present in the response content and raise only if not.
        # If the request originates from an offline operation, don't raise and return the resp.
        try:
            if not response.ok \
                    and not offline \
                    and 400 <= response.status_code < 500 \
                    and response.json().get('error'):  # The 'code' entry is sometimes missing
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError:
                    _logger.exception("invalid API request at %s with data %s", url, payload)
                    error_msg = response.json().get('error', {}).get('message', '')
                    raise ValidationError(
                        "Cardnet: " + _(
                            "The communication with the API failed.\n"
                            "Cardnet gave us the following info about the problem:\n'%s'", error_msg
                        )
                    )
        except requests.exceptions.ConnectionError:
            _logger.exception("unable to reach endpoint at %s", url)
            raise ValidationError("Cardnet: " + _("Could not establish the connection to the API."))
        return response.json()

    def _get_cardnet_extra_request_headers(self, method):
        """ Return the extra headers for the Cardnet API request.

        Note: This method serves as a hook for modules that would fully implement Cardnet Connect.

        :return: The extra request headers.
        :rtype: dict
        """
        header = {}
        if method == "POST":
            header = {
                'Content-Type': 'application/json',
            }
        return header

    # def _get_default_payment_method_id(self):
    #     self.ensure_one()
    #     if provider_code != 'cardnet':
    #         return super()._get_default_payment_method_id()
    #     return self.env.ref('astra_payment_cardnet.payment_method_cardnet').id
