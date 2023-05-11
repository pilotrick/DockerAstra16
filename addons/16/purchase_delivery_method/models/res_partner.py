# Copyright 2018-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_delivery_carrier_id = fields.Many2one(
        'delivery.carrier', company_dependent=True, string="Purchase Delivery Method", help="This delivery method will be used in Purchase Order.")
