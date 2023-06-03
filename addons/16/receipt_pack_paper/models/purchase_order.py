from odoo import models, api, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_number = fields.Char(compute='_compute_order_number', store=True)

    @api.depends('name')
    def _compute_order_number(self):
        for order in self:
            number = self._get_order_number(order.name)
            order.order_number = number

    def _get_order_number(self, name):
        number = name.split('-')[-1].strip()
        return number

