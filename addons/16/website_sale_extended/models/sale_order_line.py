# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_sale_order_line_multiline_description_sale(self, product):
        description = product.display_name
        if self.linked_line_id:
            description += "\n" + _("Option for: %s", self.linked_line_id.product_id.display_name)
        if self.option_line_ids:
            description += "\n" + '\n'.join(
                [_("Option: %s", option_line.product_id.display_name) for option_line in self.option_line_ids])
        return description