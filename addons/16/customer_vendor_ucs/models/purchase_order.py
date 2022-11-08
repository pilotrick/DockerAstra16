from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    partner_id = fields.Many2one('res.partner', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('supplier_rank', '>', 0)]")