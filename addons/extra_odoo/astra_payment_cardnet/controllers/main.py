# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hashlib
import hmac
import json
import logging
import pprint
from datetime import datetime

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import consteq

_logger = logging.getLogger(__name__)


class CardnetController(http.Controller):
    _checkout_return_url = '/payment/cardnet/checkout_return'
    _validation_return_url = '/payment/cardnet/validation_return'

    @http.route(_checkout_return_url, type='http', auth='public', csrf=False, save_session=False)
    def cardnet_return_from_checkout(self, **data):
        """ Process the data returned by Cardnet after redirection for checkout.

        :param dict data: The GET params appended to the URL in `_cardnet_create_checkout_session`
        """
        # Retrieve the tx and acquirer based on the tx reference included in the return url
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'cardnet', data
        )
        session = data['SESSION']
        acquirer_sudo = tx_sudo.provider_id

        #Fetch the PaymentIntent, Charge and PaymentMethod objects from Cardnet
        payment_intent = acquirer_sudo._cardnet_make_request(
            f'sessions/{session}?sk={tx_sudo.astra_payment_intent}', method='GET'
        )
        
        # _logger.info("received payment_intents response:\n%s", pprint.pformat(payment_intent))
        self._include_payment_intent_in_feedback_data(payment_intent, data)

        # Handle the feedback data crafted with Cardnet API objects
        tx_sudo._handle_notification_data('cardnet', data)

        # Redirect the user to the status page
        return request.redirect('/payment/status')

    @staticmethod
    def _include_payment_intent_in_feedback_data(payment_intent, data):
        data.update({'payment_intent': payment_intent})
        if payment_intent.get('ResponseCode'):
            token = payment_intent['TxToken']  # Use the latest charge object
            data.update({
                'token': token,
                'AuthorizationCode': payment_intent['AuthorizationCode'],
            })