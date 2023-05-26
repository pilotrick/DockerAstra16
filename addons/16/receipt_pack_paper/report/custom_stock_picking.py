from odoo import api, fields, models

class StockReceiptReport(models.AbstractModel):

    _name = 'receipt.pack.paper.stock'
    _description = 'Stock Receipt Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            'proforma': True
        }
        
class StockReceiptReportInvoice(models.AbstractModel):

    _name = 'receipt.pack.paper.stock.invoice'
    _description = 'Stock Receipt Report Invoice'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            'proforma': True
        }