# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class StockProductQuantity(models.TransientModel):
    _name = 'stock.product.quantity.overview'
    _description = 'Stock Product Quantity Overview'


    product_id = fields.Many2one("product.product", string="Product", required=True, domain=[('type', '=', 'product')])


    def stock_product_overview(self):
        self.ensure_one()
        product_id = self.product_id.id
        self.env['stock.quant']._merge_quants()
        self.env['stock.quant']._unlink_zero_quants()
        return {
            'domain': "[('product_id', '=', %s)]" %product_id,
            'name': _("Stock Product Quantity Overview"),
            #'view_mode': 'tree,form,pivot',
            #'auto_search': True,
            'res_model': 'stock.quant',
            'views': [(self.env.ref('stock_product_quantity_overview.view_stock_product_quantity_overview_tree').id, "tree"),(self.env.ref('stock.view_stock_quant_pivot').id, "pivot")],
            'context' : {'search_default_internal_loc': 1, 'search_default_transit_loc': 1},
            'type': 'ir.actions.act_window',
            }
