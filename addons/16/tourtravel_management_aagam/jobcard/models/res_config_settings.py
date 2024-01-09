# -*- coding: utf-8 -*-
# from odoo import api, fields, models
#
#
# class JobCardConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     default_task_assigned_product = fields.Many2one(
#         string="Default product for Task Assigned", required=True,
#         comodel_name="product.product",
#         domain="[('type', '=', 'service')]")
#
#     @api.model
#     def get_values(self):
#         res = super(JobCardConfigSettings, self).get_values()
#         config_parameter = self.env['ir.config_parameter'].sudo()
#         get_default_task_assigned_product = config_parameter.get_param(
#             'jobcard.default_task_assigned_product')
#         res.update({
#             'default_task_assigned_product': int(
#                 get_default_task_assigned_product),
#         })
#         return res
#
#     def set_values(self):
#         super(JobCardConfigSettings, self).set_values()
#         config_parameter = self.env['ir.config_parameter'].sudo()
#         config_parameter.set_param(
#             'jobcard.default_task_assigned_product',
#             self.default_task_assigned_product.id)
