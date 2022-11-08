# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models
from odoo.tools.translate import html_translate

class Website(models.Model):
    _inherit = 'website'

    sh_pwa_frontend_is_disabled = fields.Boolean(string="Disable PWA for Website")

class WebisteConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_pwa_frontend_is_disabled = fields.Boolean(
        related='website_id.sh_pwa_frontend_is_disabled',
        string="Disable PWA for Website",
        readonly=False
    )

