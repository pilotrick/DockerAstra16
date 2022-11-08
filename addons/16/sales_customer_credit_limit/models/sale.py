# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('need_approval', 'To Approve'), ('sale', 'Sale Order')])

    def action_confirm(self):
        ctx = dict(self._context or {})
        _logger.info('======credit-limit-order-confirm-check====%r====%r',request.session, ctx)
        # txId = request.session.get('__payment_tx_ids__')
        for order in self:
            if 'website_force_confirm' in ctx:
                order.message_post(body="<b>Order is placed from backend & paid from website</b> so that credit limit module flow is ignored during order confirmation.")
            elif 'force_confirm' not in ctx and not order.website_id:
                res = order.check_credit_limit()
                if res:
                    return res
            elif order.website_id:
                order.message_post(body="<b>Order is placed from website</b> so that credit limit module flow is ignored during order confirmation.")
            else:
                order.send_approval_mail()
        return super(SaleOrder, self).action_confirm()

    def send_approval_mail(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        currentUser = self.env.user
        for order in self:
            salesPerson = order.user_id

            if not salesPerson or salesPerson == currentUser:
                continue

            if not salesPerson.partner_id.email: 
                raise UserError("Please add your email for related partner of your user %s ."%(salesPerson.name))

            subject = 'Order %s has been approved by %s' % (order.name, currentUser.name)
            message = '''
            Hi %s,<br/><br/>
            The Sales Order %s has been approved. You can proceed for further actions.
            <p>
                <a href="%s/mail/view?model=%s&amp;res_id=%s"
                        style="background-color: #9E588B; margin-top: 10px; padding: 10px; text-decoration: none; color: #fff; border-radius: 5px; font-size: 16px;">
                    View %s
                </a>
            </p><br/>
            Thanks & Regards,<br/>
            %s
            <p style="color:#9E588B;">Powered by <a href="https://www.odoo.com">Odoo</a>.</p>
            ''' % (salesPerson.name, order.name,
                   base_url, order._name, order.id,
                   order._description.lower(),
                   currentUser.name)

            order.message_post(body=message, subject=subject)

            values = {
                'email_from': currentUser.partner_id.email,
                'email_to': salesPerson.partner_id.email,
                'subject': subject,
                'body_html': message,
                'auto_delete': True,
            }
            mail = self.env['mail.mail'].sudo().create(values)
            mail.send()

    def action_approve(self):
        for order in self:
            if order._check_access_to_approve():
                context = {'force_confirm': True}
                order.with_context(context).action_confirm()
            else:
                raise UserError(
                    'No tiene los derechos para aprobar esta orden de venta.')

    def _check_access_to_approve(self):
        if self.env.user.has_group('sales_team.group_sale_manager'):
            return True
        manager = self.env.user.employee_ids and self.env.user.employee_ids[0]
        if not manager:
            return False
        for order in self:
            salesPerson = order.user_id.employee_ids and order.user_id.employee_ids[0]
            if not salesPerson or not salesPerson.parent_id or manager != salesPerson.parent_id:
                return False
        return True


    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['need_approval'])
        orders.write({
            'state': 'draft',
        })
        return super(SaleOrder, self).action_draft()

    def check_credit_limit(self):
        openInvoiceIds , overdueInvoices = [], []
        orderAmount = openInvoiceAmount = overdueInvoiceAmount = excessAmount = 0
        message = ''
        orderPartner = self.partner_id
        if orderPartner.is_company or not orderPartner.parent_id:
            partner = orderPartner
            creditLimitAmount = orderPartner.credit_limit
        else:
            partner = orderPartner.commercial_partner_id

        partnerCurrencyId = partner.currency_id
        creditLimitAmount = partner.credit_limit
        orderAmount = self.currency_id._convert(self.amount_total,partnerCurrencyId, self.company_id, self.date_order)

        openInvoices = self.env['account.move'].search([ 
            ('move_type', '=', 'out_invoice'),
            ('company_id', '=', self.company_id.id),
            ('state', 'not in', ['cancel']),('payment_state','not in', ['paid','in_payment','reversed']),
            ('partner_id', 'child_of', partner.id)
        ])
        openInvoiceIds = openInvoices.ids
        openInvoiceAmount = sum(openInvoices.mapped('amount_residual_signed'))

        draftInvoices = self.env['account.move'].search([ 
            ('move_type', '=', 'out_invoice'),
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ['draft']),
            ('partner_id', 'child_of', partner.id)
        ])
        draftInvoicesAmount = sum(draftInvoices.mapped('amount_total_signed'))

        # Total amout which is invoiced but not paid (Draft invoices + unpaid amout in open invoices.)
        remainingInvoicesAmount = openInvoiceAmount + draftInvoicesAmount

        confirmedOrders = self.env['sale.order'].search([ 
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ['need_approval' ,'sale', 'done']),
            ('invoice_status', 'in', ['to invoice']),
            ('partner_id', 'child_of', partner.id)
        ])
        confirmedOrdersAmount = sum(confirmedOrders.mapped(
            lambda order: order.currency_id._convert(order.amount_total, partnerCurrencyId, self.company_id, order.date_order))) if confirmedOrders else 0.0

        confirmedOrdersInvoices = confirmedOrders.mapped('invoice_ids').filtered(
            lambda invoice: invoice.move_type == 'out_invoice')
        confirmedOrdersInvoicesAmount = sum(confirmedOrdersInvoices.mapped('amount_total_signed'))

        # Total order amount for which invoice is not yet generated.
        remainingOrderAmount = confirmedOrdersAmount - confirmedOrdersInvoicesAmount

        totalPendingAmount = remainingOrderAmount + remainingInvoicesAmount
        totalPendingAmount = orderPartner.credit
        if creditLimitAmount > 0:
            overdueInvoices = openInvoices.filtered(
                lambda inv: inv.invoice_date_due < fields.Date.today() if inv.invoice_date_due else True)
            excessAmount = orderAmount + totalPendingAmount - creditLimitAmount
            if excessAmount > 0:
                if(remainingInvoicesAmount):
                    message = "El monto total excede el límite de crédito."
                else:
                    message = "El monto de este pedido excede el límite de crédito."
            elif(overdueInvoices):
                overdueInvoiceAmount = sum(overdueInvoices.mapped('amount_residual_signed'))
                overdueInvoiceAmount += sum(overdueInvoices.filtered(lambda inv: inv.state != 'open').mapped('amount_total_signed'))
                message = "Algunas facturas están vencidas."
        elif openInvoices:
            overdueInvoices = openInvoices
            message = "Algunas facturas ya están abiertas del mismo cliente para pedidos anteriores."
        elif remainingOrderAmount:
            message = "El cliente ya tiene pedidos confirmados para los que aún no se ha generado la factura completa."

        if overdueInvoices or excessAmount > 0 or (creditLimitAmount <= 0 and remainingOrderAmount ):
            wizardData = {
                'order_id': self.id,
                'pending_invoice_ids': [(6,0,openInvoiceIds)],
                'overdue_invoice_amount': overdueInvoiceAmount,
                'unpaid_order_ids': [(6,0,confirmedOrders.ids)],
                'pending_amount': totalPendingAmount,
                'exceeded_credit': excessAmount if excessAmount > 0 else 0,
                'order_amount': orderAmount,
                'message': message,
            }
            wizard = self.env['credit.limit.exceed.wizard'].create(wizardData)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer Credit Limit info',
                'res_model': 'credit.limit.exceed.wizard',
                'res_id': wizard.id,
                'view_mode': 'form',
                'view_id': self.env.ref(
                    'sales_customer_credit_limit.credit_limit_exceed_wizard').id,
                'target': 'new',
            }
        return False
