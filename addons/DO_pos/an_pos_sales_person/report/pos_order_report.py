# -*- coding: utf-8 -*-
from odoo import models, fields


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"
    
    it_salesperson = fields.Many2one('hr.employee', string='Salesperson', readonly=True)

    def _select(self):
        return super(PosOrderReport, self)._select() + ',l.it_salesperson AS it_salesperson'

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ',l.it_salesperson'
