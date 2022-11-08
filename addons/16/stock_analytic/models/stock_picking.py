from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.picking"

    project_id = fields.Many2one(
        compute="_compute_project_id",
        inverse="_inverse_project_id",
        comodel_name="account.analytic.account",
        string="Analytic Account",
        readonly=True,
        states={"draft": [("readonly", False)]},
        store=True,
        help="The analytic account related to a purchase order.",
    )

    @api.depends("move_ids_without_package.analytic_account_id")
    def _compute_project_id(self):
        """If all order line have same analytic account set project_id.
        If no lines, respect value given by the user.
        """
        for st in self:
            if st.move_ids_without_package:
                al = st.move_ids_without_package[0].analytic_account_id or False
                for ol in st.move_ids_without_package:
                    if ol.analytic_account_id != al:
                        al = False
                        break
                st.project_id = al

    def _inverse_project_id(self):
        """When set project_id set analytic account on all order lines"""
        for st in self:
            if st.project_id:
                st.move_ids_without_package.write({"analytic_account_id": st.project_id.id})

    @api.onchange("project_id")
    def _onchange_project_id(self):
        """When change project_id set analytic account on all order lines"""
        if self.project_id:
            self.move_ids_without_package.update({"analytic_account_id": self.project_id.id})