from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        compute='_compute_warehouse_id',
        store=True,
    )

    @api.depends('invoice_line_ids', 'invoice_line_ids.sale_line_ids',
                 'invoice_line_ids.sale_line_ids.order_id',
                 'invoice_line_ids.sale_line_ids.order_id.warehouse_id')
    def _compute_warehouse_id(self):
        for record in self:
            for line in record.invoice_line_ids:
                if line.sale_line_ids:
                    record.warehouse_id = \
                        line.sale_line_ids[0].order_id.warehouse_id