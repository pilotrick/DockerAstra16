# -*- coding: utf-8 -*-

from odoo import models, fields, _

class Website(models.Model):
    _inherit = "website"

    is_hide_price = fields.Boolean('Hide Price ? ')
    price_support_email = fields.Char('Email')



