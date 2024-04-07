# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import config


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    
    def _compute_price_unit_and_date_planned_and_name(self):
        pass