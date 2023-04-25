from odoo import api, fields, models ,SUPERUSER_ID
from odoo.exceptions import UserError

class SalesReceiptReport(models.AbstractModel):

    _name = 'receipt.pack.paper.sale'
    _description = 'Sales Receipt Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'proforma': True
        }
