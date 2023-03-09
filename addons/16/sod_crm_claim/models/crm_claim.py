# Copyright 2019-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval

AVAILABLE_STATES = [
    ("draft", "New"),
    ("open", "In Progress"),
    ("return", "Waiting for Return"),
    ("delivery", "Waiting for Delivery"),
    ("payment", "Waiting for Payment"),
    ("cancel", "Rejected"),
    ("done", "Settled"),
]


class CrmClaimStage(models.Model):
    _name = "crm.claim.stage"
    _description = "Claim stages"
    _order = "sequence"

    def _get_default_team_ids(self):
        team_id = self.env.context.get("default_team_id")
        if team_id:
            return [(4, team_id, 0)]

    name = fields.Char(
        string="Stage Name",
        required=True,
    )
    sequence = fields.Integer(
        help="Used to order stages. Lower is better.",
        default=1,
    )
    state = fields.Selection(
        selection=AVAILABLE_STATES,
        string="Status",
        required=True,
        default="open",
        help="The related status for the stage. The status of your document "
        "will automatically change regarding the selected stage. For example, "
        "if a stage is related to the status 'Close', when your document "
        "reaches this stage, it will be automatically have the 'closed'"
        "status.",
    )
    fold = fields.Boolean(
        string="Folded in Kanban view",
        help="This stage is folded in the kanban view.",
    )
    team_ids = fields.Many2many(
        "crm.claim.team",
        relation="claim_team_stage_rel",
        string="Return Team",
        default=_get_default_team_ids,
    )


class CrmClaim(models.Model):
    """Crm claim"""

    _name = "crm.claim"
    _description = "Claim"
    _order = "priority,date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_default_warehouse(self):
        company_id = self.env.company.id
        wh_obj = self.env["stock.warehouse"]
        wh = wh_obj.search([("company_id", "=", company_id)], limit=1)
        if not wh:
            raise Warning(_("There is no warehouse for the current user's company."))
        return wh

    def name_get(self):
        result = []
        for record in self:
            result.append(
                (
                    record.id,
                    record.number
                    + " - "
                    + (record.name or "")
                    + (record.stage_id and " - " + record.stage_id.name or ""),
                )
            )
        return result

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [("team_ids", "in", [self._context.get("default_team_id")])]
        return stages.search(search_domain, order=order)

    def _get_default_stage_id(self):
        stage_ids = self.env["crm.claim.stage"].search(
            [("team_ids", "in", self.team_id.id)]
        )
        if stage_ids:
            return stage_ids[0]
        return False

    @api.onchange("team_id")
    def _onchange_team_get_values(self):
        self.stage_id = (
            self.env["crm.claim.stage"]
            .search([("team_ids", "in", self.team_id.id)], order="sequence", limit=1)
            .id
        )
        self.claim_type = self.team_id.claim_type
        self.warehouse_id = self.team_id.warehouse_id

    def _default_team_id(self):
        team_id = (
            self._context.get("active_id")
            if self._context.get("active_model") == "crm.claim.team"
            else None
        )
        if not team_id:
            team_id = (
                self.env["crm.claim.team"]
                .search([("member_ids", "in", self.env.uid)], limit=1)
                .id
            )
        if not team_id:
            team_id = self.env["crm.claim.team"].search([], limit=1).id
        return team_id

    name = fields.Char(
        string="Return Subject",
    )
    active = fields.Boolean(
        default=True, help="Set active to false to hide the claim without removing it."
    )
    #     action_next = fields.Char(
    #         string='Next Action',
    #     )
    #     date_action_next = fields.Datetime(
    #         string='Next Action Date',
    #     )
    description = fields.Text()

    # TODO chech me that am I needed or not
    # create_date = fields.Datetime('Creation Date', readonly=True)
    # write_date = fields.Datetime('Update Date', readonly=True)

    date_deadline = fields.Date(
        string="Deadline",
    )
    date_closed = fields.Datetime(
        string="Closed Date",
        readonly=True,
    )
    date = fields.Datetime(
        string="Return Date",
        index=True,
        default=lambda self: fields.datetime.now(),
    )
    priority = fields.Selection(
        selection=[
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        default="1",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        tracking=True,
        default=lambda self: self.env.user,
    )
    team_id = fields.Many2one(
        comodel_name="crm.claim.team",
        string="Sales Team",
        index=True,
        help="Responsible sales team.",
        default=_default_team_id,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env["res.company"]._company_default_get(),
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
    )
    email_from = fields.Char(string="Email", size=128, help="Partner Email")
    partner_phone = fields.Char(
        string="Phone",
    )
    number = fields.Char(
        default=lambda self: _("New"),
    )
    claim_type = fields.Selection(
        selection=[("customer", "Customer"), ("supplier", "Supplier")],
        string="Return Type",
        required=True,
        default="customer",
        help="customer = from customer to company ; supplier = from company "
        "to supplier",
    )
    reason_code = fields.Many2many(
        comodel_name="crm.claim.reason",
        relation="crm_claim_reason_rel",
        column1="claim_id",
        column2="reason_id",
    )
    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        help="Related Sale Order",
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase Order",
        help="Related Purchase Order",
    )
    stage_id = fields.Many2one(
        comodel_name="crm.claim.stage",
        string="Stage",
        tracking=True,
        domain="[('team_ids', 'in', team_id)]",
        group_expand="_read_group_stage_ids",
        default=_get_default_stage_id,
    )
    state = fields.Selection(
        related="stage_id.state",
        store=True,
        # selection=AVAILABLE_STATES, # TODO check me
        string="Status",
        readonly=True,
    )
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        help="Related original Customer invoice",
    )
    claim_line_ids = fields.One2many(
        comodel_name="claim.line",
        inverse_name="claim_id",
        string="Return lines",
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
        default=_get_default_warehouse,
        required=True,
    )
    sale_count = fields.Integer(
        string="Sale Orders",
        compute="_compute_claims_count",
    )
    purchase_count = fields.Integer(
        string="Purchase Orders",
        compute="_compute_claims_count",
    )
    invoice_count = fields.Integer(
        string="Invoices",
        compute="_compute_invoice_count",
    )
    refund_count = fields.Integer(
        compute="_compute_invoice_count",
    )
    delivery_count = fields.Integer(
        string="Delivery Orders",
        compute="_compute_claims_count",
    )
    stock_inventory_count = fields.Integer(
        string="Inventory Adjustment",
        compute="_compute_quant_claim_count",
    )
    return_count = fields.Integer(
        string="Returns(s)",
        compute="_compute_claims_count",
    )
    vendor_refund_count = fields.Integer(
        compute="_compute_invoice_count",
    )
    vendor_bill_count = fields.Integer(
        compute="_compute_invoice_count",
    )
    tag_ids = fields.Many2many("crm.claim.tags", string="Tags")

    def _compute_claims_count(self):
        """This common compute method counts the number of Sale's,
        Purchase's, Picking's, Return's associated with this claim
        param: self --> crm.claim"""
        # Fix me
        # stock.inventory model deprecated in V15
        # model_list = ['stock.inventory', 'sale.order','purchase.order','stock.picking']
        # field_list = ['stock_inventory_count', 'sale_count','purchase_count',
        # ('delivery_count','return_count')]
        model_list = ["sale.order", "purchase.order", "stock.picking"]
        field_list = [
            "sale_count",
            "purchase_count",
            ("delivery_count", "return_count"),
        ]
        return self._set_claim_fields_count(model_list, field_list)

    def _set_claim_fields_count(self, model_list, field_list):
        for claim in self:
            for model, field in zip(model_list, field_list):
                search_count = self.env[model].search_count
                claim_domain = ("claim_id", "=", claim.id)
                if isinstance(field, tuple) and model == "stock.picking":
                    location_dest_id = (
                        claim.partner_id.property_stock_customer.id
                        if claim.claim_type == "customer"
                        else claim.partner_id.property_stock_supplier.id
                    )
                    location_id = (
                        claim.partner_id.property_stock_customer.id
                        if claim.claim_type == "customer"
                        else claim.partner_id.property_stock_supplier.id
                    )
                    claim[field[0]] = search_count(
                        [claim_domain, ("location_dest_id", "=", location_dest_id)]
                    )
                    claim[field[1]] = search_count(
                        [claim_domain, ("location_id", "=", location_id)]
                    )
                else:
                    claim[field] = search_count([claim_domain])

    def _compute_quant_claim_count(self):
        for claim in self:
            claim.stock_inventory_count = self.env["stock.quant"].search_count(
                [
                    ("claim_id", "=", claim.id),
                    ("location_id.usage", "in", ["internal", "transit"]),
                ]
            )

    def _compute_invoice_count(self):
        search_count = self.env["account.move"].search_count
        for claim in self:
            claim_domain = ("claim_id", "=", claim.id)
            claim.refund_count = search_count(
                [claim_domain, ("move_type", "=", "out_refund")]
            )
            claim.vendor_refund_count = search_count(
                [
                    claim_domain,
                    ("move_type", "=", "in_refund"),
                ]
            )
            claim.invoice_count = search_count(
                [
                    claim_domain,
                    ("move_type", "=", "out_invoice"),
                ]
            )
            claim.vendor_bill_count = search_count(
                [
                    claim_domain,
                    ("move_type", "=", "in_invoice"),
                ]
            )

    @api.onchange("claim_type")
    def onchange_claim_type(self):
        if not self._context.get("from_defaults"):
            for claim in self:
                claim.partner_id = False
                claim.sale_id = False

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        self.email_from = self.partner_id.email
        self.partner_phone = self.partner_id.phone
        if not self._context.get("from_defaults"):
            self.sale_id = False

    #         if self.partner_id.team_id:
    #             self.team_id = self.partner_id.team_id.id
    #         else:
    #             self.team_id = self.env['crm.team']._get_default_team_id(self.env.uid)

    @api.model
    def create(self, vals):
        if vals.get("team_id") and not self._context.get("default_team_id"):
            self = self.with_context(default_team_id=vals.get("team_id"))
        if vals.get("number", _("New")) == _("New"):
            vals["number"] = self.env["ir.sequence"].next_by_code("crm.claim") or _(
                "New"
            )
        res = super(CrmClaim, self).create(vals)
        #         if vals.get('sale_id'):
        #             self.env['sale.order'].browse(
        #                 vals.get('sale_id')).write({
        #                     'so_claim_id': res.id,
        #                 })
        return res

    def write(self, vals):
        if "stage_id" in vals:
            stage = self.env["crm.claim.stage"].browse(vals.get("stage_id"))
            if stage.state == "done":
                vals.update(
                    {
                        "date_closed": fields.datetime.now(),
                    }
                )
        #         if 'sale_id' in vals:
        #             if vals.get('sale_id'):
        #                 self.env['sale.order'].browse(vals.get('sale_id')).write({
        #                     'so_claim_id': self.id,
        #                 })
        #             else:
        #                 self.sale_id.write({
        #                     'so_claim_id': False,
        #                 })
        return super(CrmClaim, self).write(vals)

    def copy(self, default=None):
        default = dict(default or {}, name=_("%s (copy)") % self.name)
        default["number"] = self.env["ir.sequence"].next_by_code("crm.claim") or _(
            "New"
        )
        return super(CrmClaim, self).copy(default)

    def action_view_sale(self):
        self.ensure_one()
        action = self.env.ref("sale.action_orders").sudo().read()[0]
        sale_orders = self.env["sale.order"].search([("claim_id", "=", self.id)])
        context = {
            "default_partner_id": self.partner_id.id,
            "default_claim_id": self.id,
        }
        if len(sale_orders) >= 1:
            action["domain"] = [("id", "in", sale_orders.ids)]
        else:
            action["views"] = [(self.env.ref("sale.view_order_form").id, "form")]
        action["context"] = context
        return action

    def action_view_purchase(self):
        action = self.env.ref("purchase.purchase_rfq")
        result = action.sudo().read()[0]
        claim_ids = sum([claim.ids for claim in self], [])
        purchase_ids = self.env["purchase.order"].search(
            [("claim_id", "in", claim_ids)]
        )
        context = {
            "default_partner_id": self.partner_id.id,
            "default_claim_id": self.id,
        }
        if len(purchase_ids) == 1:
            form = self.env.ref("purchase.purchase_order_form", False)
            form_id = form.id if form else False
            result["views"] = [(form_id, "form")]
            result["res_id"] = purchase_ids[0].id
        else:
            result["domain"] = (
                "[('claim_id','in',[" + ",".join(map(str, claim_ids)) + "])]"
            )
        result["context"] = context
        return result

    def action_view_invoice(self):
        if self.claim_type == "customer":
            invoice_type = "out_invoice"
            action = self.env.ref("account.action_move_out_invoice_type")
            form_view = "account.view_move_form"
        else:
            invoice_type = "in_invoice"
            action = self.env.ref("account.action_move_in_invoice_type")
            form_view = "account.view_move_form"
        context = safe_eval(action.context)
        context.update(
            {
                "default_move_type": invoice_type,
                "default_partner_id": self.partner_id.id,
                "default_claim_id": self.id,
            }
        )
        result = action.sudo().read()[0]
        result.update({"context": context})
        claim_ids = sum([claim.ids for claim in self], [])
        invoice_ids = self.env["account.move"].search(
            [("claim_id", "in", claim_ids), ("move_type", "=", invoice_type)]
        )
        if len(invoice_ids) == 1:
            form = self.env.ref(form_view, False)
            form_id = form.id if form else False
            result["views"] = [(form_id, "form")]
            result["res_id"] = invoice_ids[0].id
        else:
            result["domain"] = (
                "[('claim_id','in',["
                + ",".join(map(str, claim_ids))
                + "]),('move_type','=','"
                + str(invoice_type)
                + "')]"
            )
        return result

    def action_view_refund(self):
        if self.claim_type == "customer":
            invoice_type = "out_refund"
            action = self.env.ref("account.action_move_out_invoice_type")
            form_view = "account.view_move_form"
        else:
            invoice_type = "in_refund"
            action = self.env.ref("account.action_move_in_invoice_type")
            form_view = "account.view_move_form"
        context = safe_eval(action.context)
        context.update(
            {
                "default_move_type": invoice_type,
                "default_partner_id": self.partner_id.id,
                "default_claim_id": self.id,
                "default_date_invoice": fields.Datetime.now(),
            }
        )
        result = action.sudo().read()[0]
        result.update({"context": context})
        claim_ids = sum([claim.ids for claim in self], [])
        invoice_ids = self.env["account.move"].search(
            [("claim_id", "in", claim_ids), ("move_type", "=", invoice_type)]
        )

        if len(invoice_ids) == 1:
            form = self.env.ref(form_view, False)
            form_id = form.id if form else False
            result["views"] = [(form_id, "form")]
            result["res_id"] = invoice_ids[0].id
        else:
            result["domain"] = (
                "[('claim_id','in',["
                + ",".join(map(str, claim_ids))
                + "]),('move_type','=','"
                + str(invoice_type)
                + "')]"
            )
        return result

    def action_view_picking(self):
        action = self.env.ref("stock.action_picking_tree_all")
        # override the context to get rid of the default filtering on operation type
        #         context = safe_eval(action.context)
        context = {
            "contact_display": "partner_address",
        }
        picking_type_id = None
        claim_ids = sum([claim.ids for claim in self], [])
        domain = [("claim_id", "in", claim_ids)]
        if self.claim_type == "customer":
            location_id = self.partner_id.property_stock_customer.id
        else:
            location_id = self.partner_id.property_stock_supplier.id
        context.update(
            {"default_warehouse_id": self.warehouse_id.id, "planned_picking": True}
        )
        if "picking_type_code" in self._context:
            if self._context.get("picking_type_code") == "outgoing":
                picking_type_id = self.warehouse_id.out_type_id.id
                domain += [("location_dest_id", "=", location_id)]
            elif self._context.get("picking_type_code") == "incoming":
                picking_type_id = (
                    self.warehouse_id.rma_type_id.id
                    or self.warehouse_id.out_type_id.return_picking_type_id.id
                    or self.warehouse_id.in_type_id.id
                )
                domain += [("location_id", "=", location_id)]
            context.update({"default_picking_type_id": picking_type_id})
        context.update(
            {
                "default_partner_id": self.partner_id.id,
                "default_claim_id": self.id,
            }
        )
        result = action.sudo().read()[0]
        result.update({"context": context})
        picking_ids = self.env["stock.picking"].search(domain)
        if len(picking_ids) == 1:
            form = self.env.ref("stock.view_picking_form", False)
            form_id = form.id if form else False
            result["views"] = [(form_id, "form")]
            result["res_id"] = picking_ids[0].id
        else:
            result["domain"] = (
                "[('claim_id','in',["
                + ",".join(map(str, claim_ids))
                + "]),('id','in',["
                + ",".join(map(str, picking_ids.ids))
                + "])]"
            )
        return result

    def action_view_inventory_adjustment(self):
        claim_ids = sum([claim.ids for claim in self], [])
        action = {
            "name": _("Inventory Adjustment"),
            "view_mode": "list",
            "view_id": self.env.ref(
                "stock.view_stock_quant_tree_inventory_editable"
            ).id,
            "res_model": "stock.quant",
            "type": "ir.actions.act_window",
            "context": {"default_claim_id": self.id, "from_claim": False},
            "domain": [
                ("claim_id", "in", claim_ids),
                ("location_id.usage", "in", ["internal", "transit"]),
            ],
        }
        return action


class ClaimLine(models.Model):
    _name = "claim.line"
    _description = "List of product to return"

    name = fields.Char(string="Description", required=True, default=None)
    claim_id = fields.Many2one(
        "crm.claim",
        readonly=True,
        string="Related Return",
        help="To link to the Return object",
    )
    claim_origine = fields.Selection(
        [
            ("none", "Not specified"),
            ("legal", "Legal retractation"),
            ("cancellation", "Order cancellation"),
            ("damaged", "Damaged delivered product"),
            ("error", "Shipping error"),
            ("exchange", "Exchange request"),
            ("lost", "Lost during transport"),
            ("other", "Other"),
            ("warranty", "Warranty"),
        ],
        string="Return Subject",
        required=True,
        help="To describe the line product problem",
        default="none",
    )
    refund_line_id = fields.Many2one(
        "account.move.line",
        string="Refund Line",
        help="The refund line related to the returned product",
    )
    invoice_line_id = fields.Many2one(
        "account.move.line",
        string="Invoice Line",
        help="The invoice line related to the returned product",
    )
    product_id = fields.Many2one(
        "product.product", string="Product", help="Returned product"
    )
    product_returned_quantity = fields.Float(
        string="Quantity", digits=(12, 2), help="Quantity of product returned"
    )
    unit_sale_price = fields.Float(
        digits=(12, 2),
        help="""Unit sale price of the product.
        Auto filed if retrun done by invoice selection. BE CAREFUL AND CHECK the automatic value
        as don't take into account previous refounds, invoice discount, can be for 0
        if product for free,...""",
    )
    product_uom_id = fields.Many2one("uom.uom", string="UoM", required=True)
    state = fields.Selection(
        [
            ("draft", "No Refund"),
            ("refund", "Refund"),
            ("refund_restock", "Refund with restocking fee"),
        ],
        default="draft",
    )
    prodlot_id = fields.Many2one(
        "stock.production.lot",
        string="Serial/Lot n",
        help="The serial/lot of the returned product",
    )
    warning = fields.Char(
        string="Warranty", readonly=True, help="If warranty has expired"
    )
    on_invoice = fields.Boolean(readonly=True, help="Product form Invoice")


class CrmClaimReason(models.Model):
    _name = "crm.claim.reason"
    _description = "Claim Reason"

    name = fields.Char(size=64)
    color = fields.Integer("Color Index")


class CrmClaimTags(models.Model):
    _name = "crm.claim.tags"
    _description = "Claim Tags"

    name = fields.Char(required=True)
    color = fields.Integer("Color Index")

    _sql_constraints = [
        ("name_uniq", "CHECK(1=1)", "Tag name already exists !"),
    ]
