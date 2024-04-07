from odoo import models, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        for rec in res:
            if rec.order_id.partner_id.max_discount:
                if rec.discount > rec.order_id.partner_id.max_discount:
                    raise UserError(
                        _("El descuento maximo permitido a este cliente es de '{}%' discount for '{}'.".format(
                            rec.order_id.partner_id.max_discount, rec.order_id.partner_id.name)))
        return res

    def write(self, vals):
        for rec in self:
            res = super(SaleOrderLine, self).write(vals)
            if rec.order_id.partner_id.max_discount:
                if rec.discount > rec.order_id.partner_id.max_discount:
                    raise UserError(
                        _("El descuento maximo permitido a este cliente es de '{}%' discount for '{}'".format(
                            rec.order_id.partner_id.max_discount, rec.order_id.partner_id.name)))
            return res
