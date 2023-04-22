from odoo import models, api, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_user_id = fields.Many2one('res.users', string='Vendedor de factura', store=True, compute='_compute_invoice_user_id', readonly=False)

    @api.depends('move_id')
    def _compute_invoice_user_id(self):
        for payment in self:
            if payment.move_id:
                invoice = payment.move_id
                payment.invoice_user_id = invoice.invoice_user_id.id

