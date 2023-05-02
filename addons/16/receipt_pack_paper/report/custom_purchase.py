from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _name = 'receipt.pack.paper.purchase'
    _description = 'Purchase Receipt Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'proforma': True
        }

class PurchaseOrderQuotation(models.Model):
    _name = 'receipt.pack.paper.purchase.quotation'
    _description = 'Purchase Receipt Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'proforma': True
        }