from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approval_system_for_reorder = fields.Boolean('Approval System for Reorder',
                                                 help="Set true for Approved System to use Advance "
                                                      "Reorder Process")
    reorder_rounding_method = fields.Selection([('round_up', 'Rounding up'), ('round_down', 'Rounding down')],
                                                string="Rounding Method",
                                                help="Rounding Method will be set rounding according "
                                                     "to selected value")
    reorder_round_quantity = fields.Integer('Round Quantity')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        approval_system_for_reorder = self.env['ir.config_parameter'].sudo().\
            get_param('setu_advance_reordering.approval_system_for_reorder', False)
        reorder_rounding_method = self.env['ir.config_parameter'].sudo(). \
            get_param('setu_advance_reordering.reorder_rounding_method', False)
        reorder_round_quantity = self.env['ir.config_parameter'].sudo(). \
            get_param('setu_advance_reordering.reorder_round_quantity', False)
        res.update(approval_system_for_reorder=approval_system_for_reorder,
                   reorder_rounding_method=reorder_rounding_method,
                   reorder_round_quantity=reorder_round_quantity)
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].set_param('setu_advance_reordering.approval_system_for_reorder',
                                                  self.approval_system_for_reorder or False)
        self.env['ir.config_parameter'].set_param('setu_advance_reordering.reorder_rounding_method',
                                                  self.reorder_rounding_method or False)
        self.env['ir.config_parameter'].set_param('setu_advance_reordering.reorder_round_quantity',
                                                  self.reorder_round_quantity or False)
        super(ResConfigSettings, self).set_values()
