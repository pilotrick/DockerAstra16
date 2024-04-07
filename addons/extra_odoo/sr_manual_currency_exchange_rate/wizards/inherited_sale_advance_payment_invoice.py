# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        invoice_id = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
        invoice_id.write({
            'active_manual_currency_rate':sale_orders.active_manual_currency_rate,
            'apply_manual_currency_exchange': sale_orders.apply_manual_currency_exchange,
            'manual_currency_exchange_rate': sale_orders.manual_currency_exchange_rate
        })
        return invoice_id
