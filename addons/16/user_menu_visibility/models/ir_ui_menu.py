import logging
from odoo import models, fields, api, _, tools

_logger = logging.getLogger(__name__)

class IrActionReport(models.Model):
    _inherit = "ir.actions.report"
    _description = 'Ir Action Report'

    group_ids = fields.Many2many('res.groups', string='Groups Menu Visibility')
    users_ids = fields.Many2many('res.users', string='Users')
    protected = fields.Boolean("Protected", help="Make rule editable only for superuser")

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        res = super(IrUiMenu, self)._visible_menu_ids(debug)
        return res - set(self.env.user.hidden_menu_ids.ids)

    @api.model
    @api.returns('self')
    def get_user_roots(self):
        menu_ids = super(IrUiMenu, self).get_user_roots()
        return menu_ids - self.env.user.hidden_menu_ids

    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if self.env.user.hidden_menu_ids:
            res += self.env.user.hidden_menu_ids.ids
        return res

    @api.model
    @tools.ormcache_context('self._uid', 'debug', keys=('lang',))
    def load_menus(self, debug):
        ir_act_report = self.env['ir.actions.report'].sudo().with_user(self.env.user).search(
            [('users_ids', '=', self.env.user.id), ('protected', '=', False)])
        ir_act_report1 = self.env['ir.actions.report'].sudo().with_user(self.env.user).search(
            [('users_ids', '!=', self.env.user.id), ('protected', '=', False)])
        if ir_act_report:
            ir_act_report.sudo().unlink_action()
        if ir_act_report1:
            ir_act_report1.sudo().create_action()
        return super(IrUiMenu, self).load_menus(debug)
