from odoo import fields,models


class InheritSaleorder(models.Model):
    _inherit = 'sale.order'
    
    new_sale_order_line = fields.Char()