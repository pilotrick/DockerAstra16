# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

class account_payment(models.Model):
    _inherit = "account.payment"

    reference_ids = fields.Many2many(comodel_name='account.move',compute='get_invoice_id', string='Reference Id')
    reference_number = fields.Text(string='Reference Number',readonly=True)

    @api.model
    def default_get(self, fields):
        rec = super(account_payment, self).default_get(fields)
        invoice_defaults = self.env['account.move'].search([('invoice_ids', 'in',rec.get('invoice_ids'))])
        number = []
        if invoice_defaults and len(invoice_defaults) == 1:
            number.append("Ref/%s" % datetime.now().strftime('%Y%m%d%H%M%S'))
            payment = self.env['account.payment'].search([('invoice_ids.number', '=', rec['communication'])])
            if payment:
                for id in payment:
                    number.append(id.reference_number)
            rec['reference_number'] = '\n'.join(set(' '.join(number).split()))
        return rec

    @api.depends('reconciled_invoice_ids')
    def get_invoice_id(self):
        if self.reconciled_invoice_ids:
            ids=[]
            for id in self.reconciled_invoice_ids:
                ids.append(id.id)
                self.reference_ids =[(6, 0,ids)]



class account_register_payments(models.TransientModel):
    _inherit = "account.payment.register"

    def _prepare_payment_vals(self, invoices):
        '''Create the payment values.
        :param invoices: The invoices that should have the same commercial partner and the same type.
        :return: The payment values as a dictionary.
        '''

        number = []
        number.append("Ref/%s" % datetime.now().strftime('%Y%m%d%H%M%S'))
        payment = self.env['account.payment'].search([])
        for id in payment:
            if id and id.invoice_ids in self.invoice_ids:
                number.append(id.reference_number)
        amount = self._compute_payment_amount(invoices) if self.multi else self.amount
        payment_type = ('inbound' if amount > 0 else 'outbound') if self.multi else self.payment_type
        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,  # DO NOT FORWARD PORT TO V12 OR ABOVE
            'invoice_ids': [(6, 0, invoices.ids)],
            'payment_type': payment_type,
            'amount': abs(amount),
            'currency_id': self.currency_id.id,
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'reference_number': '\n'.join(set(' '.join(number).split())),
        }
