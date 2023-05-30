from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = "pos.config"

    allow_salesperson = fields.Boolean("Allow Salesperson")
    action_type = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], default='manual')
    group_change_salesperson_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_group_change_salesperson",
        string="Point of Sale - Change Salesperson",
        help="This field is there to pass the id of the 'PoS - Change salesperson' Group to the Point of Sale Frontend."
    )

    def _compute_group_change_salesperson(self):
        self.update(
            {
                "group_change_salesperson_id": self.env.ref(
                    "an_pos_sales_person.group_change_salesperson"
                ).id,
            }
        )

    @api.onchange("allow_salesperson")
    def onchange_allow_salesperson(self):
        if self.allow_salesperson:
            self.module_pos_hr = True
