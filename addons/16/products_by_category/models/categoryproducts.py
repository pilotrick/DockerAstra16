from odoo import models, fields, api

class CategoryInQuotation(models.Model):
    _inherit = 'sale.order'

    category_id = fields.Many2one('product.category', string='Product Category')

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            products = self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
            order_lines = []
            for product in products:
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': product.name,
                    'product_uom_qty': 1,
                    'price_unit': product.list_price,
                }))
            self.order_line = order_lines
