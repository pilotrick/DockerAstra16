# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InvoiceSaleCommission(models.Model):
    _inherit = 'invoice.sale.commission'

    invoice_date = fields.Date("Invoice Date",compute="compute_load_invoice_date")
    payment_date = fields.Date("Payment Date",compute="compute_payment_dates")
    overdue_days = fields.Integer("Over Due Days",compute="compute_overdue_days")

    def compute_payment_dates(self):
        for rec in self:
            date = self.env['account.payment'].search([('ref','=',rec.invoice_id.payment_reference)])
            rec.payment_date = date.date

    def compute_load_invoice_date(self):
        for rec in self:
            rec.invoice_date = rec.invoice_id.invoice_date

    def compute_overdue_days(self):
        for rec in self:
            if rec.invoice_id:
                rec.overdue_days = (fields.Date().today() - rec.invoice_id.invoice_date_due).days
            else:
                rec.overdue_days = 0

    def get_mix_commission(self, commission_brw, invoice):
        res = super(InvoiceSaleCommission, self).get_mix_commission(commission_brw, invoice)
        for rec in res:
            rec.invoice_date = rec.invoice_id.invoice_date


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    commission_margin = fields.Many2one('sale.commission',string="Commission Margin")
    commission_amount = fields.Float("Commission Amount")

    @api.onchange('commission_margin')
    def onchange_commission_amount(self):
        if self.commission_margin.comm_type == 'standard':
            self.commission_amount = self.amount*self.commission_margin.standard_commission
