# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details

from odoo import fields, models, api

class AccountPayment(models.AbstractModel):
    _name = 'receipt.pack.paper.account.pyment'
    _description = 'Receipt International Pack & Paper'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.payment',
            'docs': docs,
            'proforma': True,
        }