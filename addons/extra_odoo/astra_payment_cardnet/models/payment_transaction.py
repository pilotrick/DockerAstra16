# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from werkzeug import urls
import random
import string

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.payment import utils as payment_utils
from ..const import INTENT_STATUS_MAPPING, LIVE_URL, TEST_URL, SUPPORTED_CURRENCIES
from ..controllers.main import CardnetController


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    astra_payment_intent = fields.Char(string="Cardnet Payment Intent ID", readonly=True)
    astra_cardnet_session = fields.Char(string="Cardnet Session", readonly=True)
    AuthorizationCode = fields.Char(string="AuthorizationCode", readonly=True)
    CreditCardNumber = fields.Char(string="CreditCardNumber", readonly=True)
    RetrivalReferenceNumber = fields.Char(string="RetrivalReferenceNumber", readonly=True)
    TransactionId = fields.Char(string='TransactionId', size=6, unique=True)
    ResponseCode = fields.Char(string='ResponseCode', readonly=True)
    

    @api.model
    def create(self, vals):
        if 'TransactionId' not in vals or not vals['TransactionId']:
            vals['TransactionId'] = self._generate_TransactionId()
        return super(PaymentTransaction, self).create(vals)

    def _generate_TransactionId(self):
        TransactionId = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while self.search_count([('TransactionId', '=', TransactionId)]):
            TransactionId = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return TransactionId
    
    @api.model
    def _compute_reference(self, provider_code, prefix=None, separator='-', **kwargs):
        """ Override of payment to ensure that Sips requirements for references are satisfied.

        Sips requirements for transaction are as follows:
        - References can only be made of alphanumeric characters.
          This is satisfied by forcing the custom separator to 'x' to ensure that no '-' character
          will be used to append a suffix. Additionally, the prefix is sanitized if it was provided,
          and generated with 'tx' as default otherwise. This prevents the prefix to be generated
          based on document names that may contain non-alphanum characters (eg: INV/2020/...).
        - References must be unique at provider level for a given merchant account.
          This is satisfied by singularizing the prefix with the current datetime. If two
          transactions are created simultaneously, `_compute_reference` ensures the uniqueness of
          references by suffixing a sequence number.

        :param str provider: The provider of the acquirer handling the transaction
        :param str prefix: The custom prefix used to compute the full reference
        :param str separator: The custom separator used to separate the prefix from the suffix
        :return: The unique reference for the transaction
        :rtype: str
        """
        if provider_code == 'cardnet':
            # We use an empty separator for cosmetic reasons: As the default prefix is 'tx', we want
            # the singularized prefix to look like 'tx2020...' and not 'txx2020...'.
            prefix = payment_utils.singularize_reference_prefix(separator='')
            separator = 'x'  # Still, we need a dedicated separator between the prefix and the seq.
        return super()._compute_reference(provider_code, prefix=prefix, separator=separator, **kwargs)
    
    
    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Sips-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'cardnet':
            return res

        checkout_session = self._cardnet_create_checkout_session()
        session = checkout_session['SESSION']
        provider_url = TEST_URL
        if self.provider_id.state == "enabled":
            provider_url = LIVE_URL

        self.astra_cardnet_session = session
        return {
            'api_url': provider_url+"/authorize",
            'SESSION': session,
        }

    def _cardnet_create_checkout_session(self):
        """ Create and return a Checkout Session.

        :return: The Checkout Session
        :rtype: dict
        """
        # Create the session according to the operation and return it
        # customer = self._cardnet_create_customer()
        base_url = self.provider_id.get_base_url()
        
        currency_code = "214"
        if self.env.ref('base.USD').id == self.currency_id.id:
            currency_code = "840"
        
        if self.operation == 'online_redirect':
            return_url = urls.url_join(base_url, CardnetController._checkout_return_url)
            # Specify a future usage for the payment intent to:
            # 1. attach the payment method to the created customer
            # 2. trigger a 3DS check if one if required, while the customer is still present
            order = self.invoice_ids if self.invoice_ids else None
            if 'sale_order_ids' in self._fields:
                order = self.sale_order_ids if self.sale_order_ids and not order else order
            
            order_name = order[0].name
            if order[0].name == "/":
                order_name = order[0].id
                
            checkout_session = self.provider_id._cardnet_make_request(
                '/sessions', payload={
                    'TransactionType': self.provider_id.TransactionType,
                    'CurrencyCode': currency_code,
                    'AcquiringInstitutionCode' : '349',
                    'MerchantType' : self.provider_id.merchant_type,
                    'MerchantNumber' : self.provider_id.merchant_number,
                    'MerchantTerminal' : self.provider_id.merchant_terminal,
                    'MerchantTerminal_amex' : self.provider_id.merchant_terminal_amex,
                    'PageLanguaje': 'ESP',
                    'ReturnUrl': return_url,
                    'CancelUrl': return_url,
                    'OrdenID': order_name,
                    'TransactionId': self.TransactionId,  # self.TransactionId
                    'MerchantName': self.provider_id.merchant_name,
                    'Amount': payment_utils.to_minor_currency_units(
                        self.amount, self.currency_id
                    ),
                    'AVS': self.provider_id.AVS,
                    'Tax' : order[0].amount_tax,
                    '3DS_billAddr_city': self.partner_city or None,
                    '3DS_billAddr_country': self.partner_country_id.code or None,
                    '3DS_billAddr_line1': self.partner_address or None,
                    '3DS_billAddr_line2': self.partner_id.street2 or None,
                    '3DS_billAddr_postCode': self.partner_zip or None,
                    '3DS_billAddr_state': self.partner_state_id.name or None,
                    '3DS_email': self.partner_email or None,
                    '3DS_homePhone': self.partner_phone and self.partner_phone[:20] or None,
                    '3DS_mobilePhone': self.partner_id.mobile and self.partner_id.mobile[:20] or None,
                }
            )
            
            self.astra_payment_intent = checkout_session['session-key']
        return checkout_session

    @api.model
    def _get_tx_from_notification_data(self, provider_code, data):
        """ Override of payment to find the transaction based on Cardnet data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, data)
        if provider_code != 'cardnet':
            return tx

        reference = data.get('SESSION')
        
        if not reference:
            raise ValidationError("Cardnet: " + _("Received data with missing merchant reference"))

        tx = self.search([('astra_cardnet_session', '=', reference), ('provider_code', '=', 'cardnet')])
        if not tx:
            raise ValidationError(
                "Cardnet: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, data):
        """ Override of payment to process the transaction based on Adyen data.

        Note: self.ensure_one()

        :param dict data: The feedback data build from information passed to the return route.
                          Depending on the operation of the transaction, the entries with the keys
                          'payment_intent', 'charge', 'setup_intent' and 'payment_method' can be
                          populated with their corresponding Cardnet API objects.
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(data)
        if self.provider_code != 'cardnet':
            return
        
        intent_status = str(data.get('payment_intent', {}).get('ResponseCode'))
        if not intent_status:
            raise ValidationError(
                "Cardnet: " + _("Received data with missing intent status.")
            )
        
        if 'token' in data:
            self.provider_reference = data['token']
        
        if str(data.get('payment_intent', {}).get('AuthorizationCode')):
            self.AuthorizationCode = str(data.get('payment_intent', {}).get('AuthorizationCode'))
        
        if str(data.get('payment_intent', {}).get('CreditCardNumber')):
            self.CreditCardNumber = str(data.get('payment_intent', {}).get('CreditCardNumber'))
            
        if str(data.get('payment_intent', {}).get('RetrivalReferenceNumber')):
            self.RetrivalReferenceNumber = str(data.get('payment_intent', {}).get('RetrivalReferenceNumber'))
        
        self.ResponseCode = intent_status
        if intent_status in INTENT_STATUS_MAPPING['pending']:
            self._set_pending()
            status = "pending"
        elif intent_status in INTENT_STATUS_MAPPING['done']:
            # if self.tokenize:
            #     self._cardnet_tokenize_from_feedback_data(data)
            # self._create_payment()
            self._set_done()
            self._finalize_post_processing()
            status = "done"
        elif intent_status:
            status = "cancel"
            self._set_canceled()
        else:  # Classify unknown intent statuses as `error` tx state
            _logger.info("received data with invalid intent status: %s", status)
            self._set_error(
                "Cardnet: " + _("Received data with invalid intent status: %s", status)
            )
            
    def _send_payment_request(self):
        """ Override of payment to send a payment request to Adyen.

        Note: self.ensure_one()

        :return: None
        :raise: UserError if the transaction is not linked to a token
        """
        super()._send_payment_request()
        if self.provider_code != 'cardnet':
            return
        
        raise Warning("Paid")
        
        feedback_data = {'reference': self.reference}
        _logger.info("entering _handle_notification_data with data:\n%s", pprint.pformat(feedback_data))
        self._handle_notification_data('cardnet', feedback_data)