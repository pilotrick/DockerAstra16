from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_invoiced_amount = fields.Monetary(
        string="Total Invoiced Amount",
        compute="_compute_total_amounts",
        store=False,
        readonly=True
    )

    total_due_amount = fields.Monetary(
        string="Total Due Amount",
        compute="_compute_total_amounts",
        store=False,
        readonly=True
    )

    @api.depends('partner_id')
    def _compute_total_amounts(self):
        for order in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', order.partner_id.id),
                ('state', 'in', ['posted', 'draft']),
                ('move_type', '=', 'out_invoice')
            ])
            total_invoiced = sum(invoices.mapped('amount_total'))
            total_due = sum(invoices.mapped('amount_residual'))
            order.total_invoiced_amount = total_invoiced
            order.total_due_amount = total_due


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_due_amount = fields.Monetary(
            string="Total Due Amount",
            compute="_compute_partner_amount",
            store=False,
            readonly=True
        )

    total_invoiced_amount = fields.Monetary(
            string="Total Invoiced Amount",
            compute="_compute_partner_amount",
            store=True,
            readonly=True
        )

    def _compute_partner_amount(self):
        for partner in self:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['posted', 'draft']),
                ('move_type', '=', 'out_invoice')
            ])
            total_invoiced = sum(invoices.mapped('amount_total'))
            total_due = sum(invoices.mapped('amount_residual'))
            partner.total_invoiced_amount = total_invoiced
            partner.total_due_amount = total_due