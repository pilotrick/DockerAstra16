# -*- coding: utf-8 -*-
from odoo import models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_hr_employee(self, params):
        employees = super(PosSession, self)._get_pos_ui_hr_employee(params)
        user_ids = [employee['user_id'] for employee in employees if employee['user_id']]
        for employee in employees:
            employee['groups_id'] = self.env["res.users"].browse(user_ids[0]).groups_id.ids

        return employees

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        if self.config_id.module_pos_hr:
            loaded_data['users'] = self.env["res.users"].search_read([('active', '=', True)], ['id', 'name'])
