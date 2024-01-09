# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    service_product = fields.Many2one(
        string="product for Service", required=True,
        comodel_name="product.product",
        domain="[('type', '=', 'service')]")
    extra_service_product = fields.Many2one(
        string="Default product for Extra service", required=True,
        comodel_name="product.product",
        domain="[('type', '=', 'service')]")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameter = self.env['ir.config_parameter'].sudo()

        get_default_service_product = config_parameter.get_param(
            'tourtravel_management_aagam.service_product')
        get_default_extra_service_product = config_parameter.get_param(
            'tourtravel_management_aagam.extra_service_product')
        res.update({
            'service_product': int(get_default_service_product),
            'extra_service_product': int(
                get_default_extra_service_product),
        })
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameter = self.env['ir.config_parameter'].sudo()
        config_parameter.set_param(
            'tourtravel_management_aagam.service_product',
            self.service_product.id)
        config_parameter.set_param(
            'tourtravel_management_aagam.extra_service_product',
            self.extra_service_product.id)
