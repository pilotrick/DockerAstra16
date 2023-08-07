import logging
from odoo import models, fields, api
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    hidden_menu_ids = fields.Many2many('ir.ui.menu', relation='hidden_menu_user_rel')

    @api.model_create_multi
    def create(self, vals_list):
        user_ids = super(ResUsers, self).create(vals_list)
        request.env['ir.ui.menu'].load_menus(debug=1)
        return user_ids

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        request.env['ir.ui.menu'].load_menus(debug=1)
        return res
