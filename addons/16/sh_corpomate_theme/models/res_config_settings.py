# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sh_is_enable_bottom_nav_bar = fields.Boolean(
        related="website_id.sh_is_enable_bottom_nav_bar",
        string="Bottom Navigation Bar",
        readonly=False)

    sh_is_enable_toggle_zoom  = fields.Boolean(
        string='Is enable toggle zoom',
        related="website_id.sh_is_enable_toggle_zoom",
        readonly=False
        )

class Website(models.Model):
    _inherit = "website"

    sh_is_enable_bottom_nav_bar = fields.Boolean(
        "Bottom Navigation Bar",default=True)
    
    sh_is_enable_toggle_zoom  = fields.Boolean(
        string='Is enable toggle zoom',
        )
