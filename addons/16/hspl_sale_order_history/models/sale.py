# Copyright 2018, 2021 Heliconia Solutions Pvt Ltd (https://heliconia.io)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sale Order"

    show_button_bool = fields.Boolean("show History Button", default=False, copy=False)

    @api.onchange("partner_id")
    def get_sale_order_history(self):
        if self.partner_id:
            orders = self.search(
                [("partner_id", "=", self.partner_id.id), ("state", "=", "sale")],
                order="date_order desc",
                limit=100,
            )
            self.show_button_bool = True if orders else False
