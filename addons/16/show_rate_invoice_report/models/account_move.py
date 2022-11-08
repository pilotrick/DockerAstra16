from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_currency_rate(self):
        invoice_date = self.invoice_date or fields.Date.today()
        currency_rate = 1 / (self.env.ref('base.USD').with_context(
            date=invoice_date).rate)

        return {
            'rate': currency_rate,
            'amount': self.amount_total * currency_rate,
        }

