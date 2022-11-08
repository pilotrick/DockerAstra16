from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_vol = fields.Float(compute='_compute_vol', string='Total Volume')    
    
    @api.depends('order_line')
    def _compute_vol(self):
        for po in self:
            po.total_vol = sum(po.order_line.mapped('total_volume'))
            

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    volume = fields.Float(related='product_id.volume', string='Volumne(ft³)')
    total_volume = fields.Float(compute='_compute_volume', string='Total Volume(ft³)')

    @api.depends('volume')
    def _compute_volume(self):
        for record in self:
            record.total_volume = record.volume * record.product_qty

