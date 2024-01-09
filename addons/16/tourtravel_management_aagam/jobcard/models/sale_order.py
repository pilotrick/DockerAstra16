# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    job_card_id = fields.Many2one(comodel_name='job.card', string='Job Card')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    task_assigned_id = fields.Many2one(
        comodel_name='task.description', string='Task Assigned Id')
