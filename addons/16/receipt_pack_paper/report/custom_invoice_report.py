# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details

from odoo import api, fields, models 

class InvoiceReceiptReport(models.AbstractModel):
    _name = 'receipt.pack.paper.invoice'
    _description = 'Receipt International Pack & Paper'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': docs,
            'proforma': True,
        }
