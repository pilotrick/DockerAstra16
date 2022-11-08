# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class WareHouse(models.Model):
    _inherit = 'stock.warehouse'

    show_website = fields.Boolean("Display on Website")


class res_partner(models.Model):
    _inherit = 'res.partner'

    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")