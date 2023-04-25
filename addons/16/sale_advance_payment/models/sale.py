# Copyright 2017 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

class SaleOrder(models.Model):

    _inherit = "sale.order"

    account_payment_ids = fields.One2many(
        "account.payment", "sale_id", string="Pay sale advanced", readonly=True
    )
    amount_residual = fields.Float(
        "Residual amount",
        readonly=True,
        compute="_compute_advance_payment",
        store=True,
    )
    payment_line_ids = fields.Many2many(
        "account.move.line",
        string="Payment move lines",
        compute="_compute_advance_payment",
        store=True,
    )
    advance_payment_status = fields.Selection(
        selection=[
            ("not_paid", "Not Paid"),
            ("paid", "Paid"),
            ("partial", "Partially Paid"),
        ],
        store=True,
        readonly=True,
        copy=False,
        tracking=True,
        compute="_compute_advance_payment",
    )
    can_confirm_with_amount_residual = fields.Boolean(
        "Can Confirm With Amount Residual",
        readonly=True,
        compute="_compute_can_confirm_with_amount_residual",
        store=True,
    )

    has_amount_residual = fields.Boolean(
    "Has Amount Residual",
    readonly=True,
    compute="_compute_can_confirm_with_amount_residual",
    store=True,
    )

    is_credit_limit_installed = fields.Boolean(
        compue='_compute_can_confirm_with_amount_residual',
        string='Is Credit Limit Module Installed?'
    )

    show_confirm_button = fields.Boolean(
        compue='_compute_show_confirm_button',
        string='Has Credit To Confirm?',
        default=True
    )

    @api.depends(
        "currency_id",
        "company_id",
        "amount_total",
        "account_payment_ids",
        "account_payment_ids.state",
        "account_payment_ids.move_id",
        "account_payment_ids.move_id.line_ids",
        "account_payment_ids.move_id.line_ids.date",
        "account_payment_ids.move_id.line_ids.debit",
        "account_payment_ids.move_id.line_ids.credit",
        "account_payment_ids.move_id.line_ids.currency_id",
        "account_payment_ids.move_id.line_ids.amount_currency",
        "invoice_ids.amount_residual",
    )
    def _compute_advance_payment(self):
        for order in self:
            
            mls = order.account_payment_ids.mapped("move_id.line_ids").filtered(
                lambda x: x.account_id.account_type == "asset_receivable"
                and x.parent_state == "posted"
            )
            advance_amount = 0.0
            for line in mls:
                line_currency = line.currency_id or line.company_id.currency_id
                # Exclude reconciled pre-payments amount because once reconciled
                # the pre-payment will reduce invoice residual amount like any
                # other payment.
                line_amount = (
                    line.amount_residual_currency
                    if line.currency_id
                    else line.amount_residual
                )
                line_amount *= -1
                if line_currency != order.currency_id:
                    # corroborar que el metodo covert no deja el anticipo en 0
                    advance_amount += line.currency_id._convert(
                        line_amount,
                        order.currency_id,
                        order.company_id,
                        line.date or fields.Date.today(),
                    )
                else:
                    advance_amount += line_amount
            # Consider payments in related invoices.
            invoice_paid_amount = 0.0
            for inv in order.invoice_ids:
                invoice_paid_amount += inv.amount_total - inv.amount_residual
            # resta, imprimir por pantalla valor de advance amount
            # corroborar que advance amount = anticipo de la resta
            amount_residual = order.amount_total - advance_amount - invoice_paid_amount
            payment_state = "not_paid"
            if mls:
                has_due_amount = float_compare(
                    amount_residual, 0.0, precision_rounding=order.currency_id.rounding
                )
                if has_due_amount <= 0:
                    payment_state = "paid"
                elif has_due_amount > 0:
                    payment_state = "partial"
            order.payment_line_ids = mls
            order.amount_residual = amount_residual
            order.advance_payment_status = payment_state

    @api.depends('order_line.price_unit', 'amount_residual', 'payment_term_id')
    def _compute_can_confirm_with_amount_residual(self):
        module_name = 'dev_customer_credit_limit'
        Module = self.env['ir.module.module']
        is_credit_limit_installed = Module.search([('name', '=', module_name)])
        user = self.env.user
        is_admin_or_has_access = user.has_group('sale_advance_payment.group_advance_payment_access') or user.has_group('base.group_erp_manager')
        can_confirm_order = True
        has_amount_residual = False
        IMMEDIATE_PAYMENT_ID = 1
        for order in self:
            # If the payment term is immediate payment needs do advance payment
            if order.payment_term_id.id == IMMEDIATE_PAYMENT_ID or order.payment_term_id.id == False:
                can_confirm_order = order.amount_residual == 0 or is_admin_or_has_access
                order.can_confirm_with_amount_residual = can_confirm_order
                has_amount_residual = order.amount_residual != 0
                order.has_amount_residual = has_amount_residual
                order.is_credit_limit_installed = bool(is_credit_limit_installed)
            else:
                order.can_confirm_with_amount_residual = can_confirm_order
                order.has_amount_residual = has_amount_residual
                order.show_confirm_button = True
                

        if has_amount_residual:
            self._compute_show_confirm_button()

    @api.depends('partner_id')
    def _compute_show_confirm_button(self):
        module_name = 'dev_customer_credit_limit'
        Module = self.env['ir.module.module']
        module_installed = Module.search([('name', '=', module_name)])
        is_credit_limit_installed = bool(module_installed)
        if is_credit_limit_installed:
            partner_id = self.partner_id
            if self.partner_id.parent_id:
                partner_id = self.partner_id.parent_id
                
            if partner_id:
                for order in self:
                    order.show_confirm_button = True
                    for partner in partner_id:
                        if not order.can_confirm_with_amount_residual or partner.credit_limit < order.amount_total:
                            order.show_confirm_button = False
                            break


            
    """ def action_confirm(self):
        for order in self:
            if not order.can_confirm_with_amount_residual:
                msg = "No tiene permisos para confirmar esta orden hasta que realice un pago anticipado del importe residual pendiente."
                raise UserError(_('Solicitud de confirmación denegada %s') % msg)
            
            if order.is_credit_limit_installed:
                return self.action_sale_ok()        
        
        return super(SaleOrder,self).action_confirm() """