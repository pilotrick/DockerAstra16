# Copyright 2015 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - vicent.cubells@tecnativa.com
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if not self.product_id:  # pragma: no cover
            return res
        if self.product_id.description_purchase:
            product = self.product_id
            if self.order_id.partner_id:
                product = product.with_context(
                    lang=self.order_id.partner_id.lang,
                )
            self.name = product.description_purchase
        return res
