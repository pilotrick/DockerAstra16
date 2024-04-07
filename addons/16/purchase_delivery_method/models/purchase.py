# Copyright 2018-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        self.carrier_id = self.partner_id.purchase_delivery_carrier_id.id
        return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super(StockRule, self)._prepare_purchase_order(company_id, origins, values)
        values = values[0]
        partner = values["supplier"].partner_id
        if partner.purchase_delivery_carrier_id:
            res.update({
                'carrier_id': partner.purchase_delivery_carrier_id.id
            })
        return res

