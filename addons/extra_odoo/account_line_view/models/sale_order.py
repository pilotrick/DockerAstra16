from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    product = fields.Many2one(comodel_name='product.template', string='Producto', related='order_line.product_template_id')
    categ_product = fields.Many2one(comodel_name='product.category', string='Categoria de producto', related='order_line.product_template_id.categ_id')
    price_unit = fields.Float(string='Precio por unidad', related='order_line.price_unit')
    cost = fields.Float(string='Costo', related='order_line.product_template_id.standard_price')
    subtotal = fields.Monetary(string="Subtotal", related='order_line.price_subtotal')
    margin_percentage = fields.Float(string='Margin(%)', related='order_line.margin_percent')
    qty_delivery = fields.Float(string="Entregado", related='order_line.qty_delivered')
    qty_invoiced = fields.Float(string="Facturado", related='order_line.qty_invoiced')
    
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, store=True)
    
    