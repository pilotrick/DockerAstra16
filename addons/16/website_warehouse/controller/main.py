# -*- coding: utf-8 -*-

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers import portal as PaymentProcessing
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.addons.website_sale.controllers.main import PaymentPortal
from odoo.fields import Command


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        """
        overriding
        :param post:
        :return:
        """
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        render_values['warehouse'] = request.env['stock.warehouse'].sudo().search([('show_website','=',True)])
        render_values['user'] = request.env.user
        print(render_values)
        return request.render("website_sale.payment", render_values)

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if order and not order.amount_total and not tx:
            order.with_context(send_email=True).action_confirm()
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        PaymentPostProcessing.remove_transactions(tx)
        return request.redirect('/shop/confirmation')

#     @http.route(['/shop/payment/transaction/',
#                  '/shop/payment/transaction/<int:so_id>',
#                  '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public",
#                 website=True)
#     def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
#         """ Json method that creates a payment.transaction, used to create a
#         transaction when the user clicks on 'pay now' button. After having
#         created the transaction, the event continues and the user is redirected
#         to the acquirer website.
# 
#         :param int acquirer_id: id of a payment.acquirer record. If not set the
#                                 user is redirected to the checkout page
#         """
#         # Ensure a payment acquirer is selected
#         if not acquirer_id:
#             return False
# 
#         try:
#             acquirer_id = int(acquirer_id)
#         except:
#             return False
# 
#         # Retrieve the sale order
#         if so_id:
#             env = request.env['sale.order']
#             domain = [('id', '=', so_id)]
#             if access_token:
#                 env = env.sudo()
#                 domain.append(('access_token', '=', access_token))
#             order = env.search(domain, limit=1)
#         else:
#             order = request.website.sale_get_order()
# 
#         # Ensure there is something to proceed
#         if not order or (order and not order.order_line):
#             return False
# 
#         assert order.partner_id.id != request.website.partner_id.id
# 
#         # Create transaction
#         vals = {'acquirer_id': acquirer_id,
#                 'return_url': '/shop/payment/validate'}
# 
#         if save_token:
#             vals['type'] = 'form_save'
#         if token:
#             vals['payment_token_id'] = int(token)
# 
#         transaction = order._create_payment_transaction(vals)
# 
#         # store the new transaction into the transaction list and if there's an old one, we remove it
#         # until the day the ecommerce supports multiple orders at the same time
#         last_tx_id = request.session.get('__website_sale_last_tx_id')
#         last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
#         if last_tx:
#             PaymentProcessing.remove_payment_transaction(last_tx)
#         PaymentProcessing.add_payment_transaction(transaction)
#         request.session['__website_sale_last_tx_id'] = transaction.id
#         print('warehouse',kwargs.get('warehouse'))
#         order.update({'warehouse_id':kwargs.get('warehouse')})
#         return transaction.render_sale_button(order)

    def checkout_values(self, **kw):
        res = super(WebsiteSale, self).checkout_values(**kw)
        res['warehouse'] = request.env['stock.warehouse'].sudo().search([('show_website','=',True)])
        return res

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        result = super(WebsiteSale, self).address(**kw)
        result.qcontext['warehouse'] = request.env['stock.warehouse'].sudo().search([('show_website','=',True)])
        result.qcontext['user'] = request.env.user
        return result

    def _get_mandatory_billing_fields(self):
        rec = super(WebsiteSale, self)._get_mandatory_billing_fields()
        rec.append("warehouse_id")
        return rec

    def _get_mandatory_shipping_fields(self):
        record = super(WebsiteSale, self)._get_mandatory_shipping_fields()
        record.append("warehouse_id")
        return record


class PaymentPortalCustom(PaymentPortal):

    @http.route(
        '/shop/payment/transaction/<int:order_id>', type='json', auth='public', website=True
    )
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """ Create a draft transaction and return its processing values.

        :param int order_id: The sales order to pay, as a `sale.order` id
        :param str access_token: The access token used to authenticate the request
        :param dict kwargs: Locally unused data passed to `_create_transaction`
        :return: The mandatory values for the processing of the transaction
        :rtype: dict
        :raise: ValidationError if the invoice id or the access token is invalid
        """
        # Check the order id and the access token
        try:
            self._document_check_access('sale.order', order_id, access_token)
        except MissingError as error:
            raise error
        except AccessError:
            raise ValidationError("The access token is invalid.")

        kwargs.update({
            'reference_prefix': None,  # Allow the reference to be computed based on the order
            'sale_order_id': order_id,  # Include the SO to allow Subscriptions to tokenize the tx
        })
        kwargs.pop('custom_create_values', None)  # Don't allow passing arbitrary create values
        tx_sudo = self._create_transaction(
            custom_create_values={'sale_order_ids': [Command.set([order_id])]}, **kwargs,
        )

        # Store the new transaction into the transaction list and if there's an old one, we remove
        # it until the day the ecommerce supports multiple orders at the same time.
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            soid = request.env['sale.order'].browse(order_id).sudo()
            if soid and kwargs.get('warehouse'):
                soid.write({'warehouse_id': int(kwargs['warehouse'])})
            PaymentPostProcessing.remove_transactions(last_tx)
        kwargs.update({'warehouse': False})
        request.session['__website_sale_last_tx_id'] = tx_sudo.id

        return tx_sudo._get_processing_values()
