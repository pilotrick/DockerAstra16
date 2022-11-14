# Copyright 2018, 2021 Heliconia Solutions Pvt Ltd (https://heliconia.io)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderHistoryWizard(models.TransientModel):
    _name = "sale.order.history.wizard"
    _description = "sale order history wizard"

    def get_order_id(self):
        active_id = self.env.context.get("active_id", False)
        active_model = self.env.context.get("active_model", False)
        if active_id and active_model == "sale.order":
            return self.env[active_model].browse(active_id).id

    order_id = fields.Many2one(
        "sale.order", readonly=True, string="Order ID", default=get_order_id
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer", related="order_id.partner_id", readonly=True
    )

    order_line_ids = fields.One2many("sale.order.line.wiz", "wizard_id", "Order Lines")

    def prepare_order_history_vals(self, line):
        order_history_vals = {
            "order_line_id": line.id,
            "order_id": line.order_id.id,
            "product_id": line.product_id.id,
            "name": line.name,
            "qty": line.product_uom_qty,
            "price": line.price_unit,
            "subtotal": line.price_subtotal,
            "date_order": line.order_id.date_order,
            "product_uom": line.product_uom.id,
            "display_type": line.display_type,
        }
        return order_history_vals

    @api.onchange("partner_id")
    def get_sale_order_history(self):
        orders = self.env["sale.order"].search(
            [("partner_id", "=", self.order_id.partner_id.id), ("state", "=", "sale")],
            order="date_order desc",
            limit=5,
        )
        order_lines = [
            (0, 0, self.prepare_order_history_vals(line))
            for line in orders.mapped("order_line")
        ]
        self.write({"order_line_ids": order_lines})

    def add_lines(self):
        if not any([rec.select_bool for rec in self.order_line_ids]):
            raise ValidationError(
                _(
                    "Sorry !!! Please Select Any Of Record(s) For Add Into The Sale Order Line"
                )
            )
        order_lines = [
            (0, 0, line.get_selected_line_vals())
            for line in self.order_line_ids
            if line.select_bool
        ]
        self.order_id.sudo().write({"order_line": order_lines})


class SaleOrderHistoryWizardLine(models.TransientModel):
    _name = "sale.order.line.wiz"
    _description = "sale order history wizard line"

    select_bool = fields.Boolean("Select")
    wizard_id = fields.Many2one("sale.order.history.wizard")
    order_line_id = fields.Many2one("sale.order.line", "Order Lines")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Currency",
        readonly=True,
    )
    name = fields.Char("Description")
    order_id = fields.Many2one("sale.order", "Orders ")
    product_id = fields.Many2one("product.product", string="Product")
    price = fields.Float(string="Price")
    qty = fields.Float("Quantity")
    uom_id = fields.Many2one("uom.uom", string="Units")
    subtotal = fields.Float("Sub Total")
    date_order = fields.Date("Date")
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure")
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    def get_selected_line_vals(self):
        return {
            "product_id": self.product_id.id,
            "product_uom_qty": self.qty,
            "price_unit": self.price,
            "name": self.name,
            "product_uom": self.product_uom.id,
            "display_type": self.display_type,
        }
