# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models,fields
from odoo.tools import config


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_unit = fields.Float(
        string="Unit Price",
        
        digits='Product Price',
        store=True, readonly=False, required=True)

    def _compute_price_unit(self):
        pass

    def _depends_eval(self, field_name, depends, result):
        """Remove the trigger for the undesired onchange method with this field.

        We have to act at this place, as `_onchange_methods` is defined as a
        property, and thus it can't be inherited due to the conflict of
        inheritance between Python and Odoo ORM, so we can consider this as a HACK.
        """
        ctx = self.env.context
        if field_name in {"product_uom_qty", "product_uom"}:
        
            cls = type(self)
            for method in self._depends_methods.get(field_name, ()):
                if method == cls._compute_price_unit:
                    self._depends_methods[field_name].remove(method)
                    break
                #if method == cls._get_pricelist_price:
                 #   self._onchange_methods[field_name].remove(method)
                  #  break
        return super()._depends_eval(field_name, depends, result)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _onchange_eval(self, field_name, onchange, result):
        """Remove the trigger for the undesired onchange method with this field.

        We have to act at this place, as `_onchange_methods` is defined as a
        property, and thus it can't be inherited due to the conflict of
        inheritance between Python and Odoo ORM, so we can consider this as a HACK.
        """
        ctx = self.env.context
        if field_name in {"pricelist_id"} and (
            not config["test_enable"]
            or (config["test_enable"] and ctx.get("prevent_onchange_quantity", False))
        ):
            cls = type(self)
            for method in self._onchange_methods.get(field_name, ()):
                if method == cls._onchange_pricelist_id_show_update_prices:
                    self._onchange_methods[field_name].remove(method)
                    break
        return super()._onchange_eval(field_name, onchange, result)