# Copyright 2019-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)

from odoo import api, fields, models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    claim_id = fields.Many2one("crm.claim", readonly=True, string="Return")
    return_reason = fields.Text()

    @api.model
    def default_get(self, fields):
        res = super(StockReturnPicking, self).default_get(fields)
        record_id = self._context.get("active_id", False)
        stock_picking = self.env["stock.picking"].browse(record_id)
        claim_id = False
        if stock_picking.claim_id:
            claim_id = stock_picking.claim_id.id
        elif stock_picking.sale_id:
            claim_id = (
                stock_picking.sale_id.so_claim_id
                and stock_picking.sale_id.so_claim_id[0].id
                or False
            )
        elif stock_picking.purchase_id:
            linked_claims = self.env["crm.claim"].search(
                [("purchase_id", "=", stock_picking.purchase_id.id)]
            )
            claim_id = linked_claims and linked_claims[0].id or False
        res["claim_id"] = claim_id
        return res

    @api.onchange("claim_id")
    def onchange_claim_id(self):
        record_id = self._context.get("active_id", False)
        stock_picking = self.env["stock.picking"].browse(record_id)
        if not stock_picking.claim_id:
            claim_ids = (
                stock_picking.sale_id.so_claim_id
                and stock_picking.sale_id.so_claim_id.ids
            )
            if claim_ids:
                return {"domain": {"claim_id": [("id", "in", claim_ids)]}}

    def _create_returns(self):
        new_picking_id, pick_type_id = super(StockReturnPicking, self)._create_returns()
        new_picking = self.env["stock.picking"].browse([new_picking_id])
        if (
            new_picking
            and new_picking.claim_id
            and new_picking.picking_type_id.code == "incoming"
            and new_picking.location_id.usage == "customer"
        ):
            res = new_picking.button_validate()
            if isinstance(res, dict):
                if (
                    "res_id" in res
                    and "res_model" in res
                    and res.get("res_model") == "stock.immediate.transfer"
                ):
                    self.env["stock.immediate.transfer"].browse(
                        res.get("res_id")
                    ).process()
        if self.claim_id:
            new_picking.write(
                {
                    "claim_id": self.claim_id.id,
                    "return_reason": self.return_reason,
                }
            )
        return new_picking_id, pick_type_id
