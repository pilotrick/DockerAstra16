# -*- coding: utf-8 -*-

import json
from collections import OrderedDict
from functools import reduce
from statistics import mean, median

from odoo import api, fields, models


class IrActionsActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(
        selection_add=[('list', 'List')],
        ondelete={'list': 'cascade'},
    )


class StockMove(models.Model):
    _inherit = "stock.move"

    item = fields.Integer(
        string="Item",
        compute="_compute_totals",
        readonly=True,
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Orden de compra',
        related='purchase_line_id.order_id',
        store=True,
        readonly=True,
        help='Orden de compra asociada a la transferencia incluida en la liquidación',
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        related='picking_id.partner_id',
        store=True,
        readonly=True,
        help='Suplidor de la orden de compra',
    )
    invoice_ids = fields.Many2many(
        'account.move',
        string='Facturas',
        compute="_compute_info_purchase",
        store=True,
        readonly=True,
        domain=[('move_type', '=', 'in_invoice')],
        help='Facturas a proveedores asociadas a la orden de compra',
    )
    currency_date_rate = fields.Date(
        string="Fecha Tasa USD (LC)",
        compute="_compute_rate_usd",
        readonly=True,
        help='Fecha de vigencia de la tasa de cambio considerada para la liquidación',
    )
    currency_rate_usd = fields.Float(
        string="Tasa USD (LC)",
        compute="_compute_rate_usd",
        readonly=True,
        help='Tasa de cambio a la fecha de la liquidación (o de fecha más cercana)',
    )
    price_unit_usd = fields.Float(
        string="C/U US$",
        related='purchase_line_id.price_unit',
        readonly=True,
        help='Costo unitario del producto según la orden de compra. Para la conversión de monedas emplea la Tasa USD (OC)',
    )
    amount_total_usd = fields.Float(
        string="Total US$",
        compute="_compute_totals",
        readonly=True,
        help='Total de costo, según la cantidad comprada: "Qty" * "C/U US$"',
    )
    price_unit_rd = fields.Float(
        string="C/U RD",
        compute="_compute_totals",
        readonly=True,
        help='Costo unitario del producto según la orden de compra, en moneda de la empresa. Para la conversión de monedas emplea la Tasa USD (OC)',
    )
    amount_total_rd = fields.Float(
        string="Total RD",
        compute="_compute_totals",
        readonly=True,
        help='Total de costo, según la cantidad comprada: "Qty" * "C/U RD"',
    )
    factor = fields.Float(
        string="Factor",
        digits=(12, 3),
        compute="_compute_factor",
        readonly=True,
        help='Factor de costes en destino. Dado por el cálculo: ( “Total de costos adicionales” + “Total RD” ) / “Total USD”',
    )
    current_price_unit_rd = fields.Float(
        string="C/U Actual RD",
        compute="_compute_current_totals",
        readonly=True,
        help='Costo del producto luego de aplicar el factor de costos en destino. Dado por el cálculo: “C/U US$” * “Factor”',
    )
    current_total_rd = fields.Float(
        string="C/T Actual RD",
        compute="_compute_current_totals",
        readonly=True,
        help='Total de costo, según la cantidad comprada, luego de aplicar el factor de costos en destino',
    )
    current_price_unit_usd = fields.Float(
        string="C/U Actual US$",
        compute="_compute_current_totals",
        readonly=True,
        help='Costo del producto luego de aplicar el factor de costos en destino. Para la conversión de monedas emplea la Tasa USD (LC)',
    )
    current_total_usd = fields.Float(
        string="C/T Actual US$",
        compute="_compute_current_totals",
        readonly=True,
        help='Total de costo, según la cantidad comprada, luego de aplicar el factor de costos en destino. Para la conversión de monedas emplea la Tasa USD (LC)',
    )
    pvp_usd = fields.Float(
        string="PVP US$",
        default=lambda self: self.product_id.list_price *
        self.env.ref('base.USD').rate,
        help='Precio de venta del producto según su registro. Para la conversión de monedas emplea la Tasa USD (OC). Este valor puede modificarse.',
    )
    pvp_rd = fields.Float(
        string="PVP RD",
        compute="_compute_pvp_rd",
        readonly=True,
        help='Precio de venta del producto según su registro. Para la conversión de monedas emplea la Tasa USD (OC).',
    )
    margin = fields.Float(
        string="Margen %",
        compute="_compute_extra_indicators",
        readonly=True,
        help='Margen de ganancia expresado en valor porcentual. Dado por el cálculo: ( “PVP US$” – “C/U Actual US$” ) / “PVP US$”',
    )
    profit_usd = fields.Float(
        string="Ganancias en US$",
        compute="_compute_extra_indicators",
        readonly=True,
        help='Ganancia total obtenida por los productos según ajuste de costo y PVP. Dado por el cálculo: ( “PVP US$” – “C/U Actual US$” ) * “Qty”',
    )
    profit_rd = fields.Float(
        string="Ganancias en RD",
        compute="_compute_extra_indicators",
        readonly=True,
        help='Ganancia total obtenida por los productos según ajuste de costo y PVP. Dado por el cálculo: ( “PVP RD” – “C/U Actual RD” ) * “Qty”',
    )

    @api.depends('pvp_usd', 'currency_rate_usd', 'purchase_order_id')
    def _compute_pvp_rd(self):
        for record in self:
            record.pvp_rd = record.pvp_usd * (
                (record.purchase_order_id and (1/record.purchase_order_id.currency_rate))
                or record.currency_rate_usd
            )

    @api.depends_context('landed_cost_date', 'date')
    def _compute_rate_usd(self):
        self.currency_date_rate = self.get_date_from_landed_cost()
        self.currency_rate_usd = self.env["res.currency"].with_context({
            'date': self.get_date_from_landed_cost(),
        }).search([("name", "=", "USD")]).inverse_rate

    @api.depends('picking_id.purchase_id.invoice_ids')
    def _compute_info_purchase(self):
        for record in self:
            record.invoice_ids = record.picking_id.purchase_id.invoice_ids

    @api.depends('currency_rate_usd', 'price_unit_usd', 'product_uom_qty', 'purchase_order_id')
    def _compute_totals(self):
        for item, record in enumerate(self, start=1):
            record.item = item

            if record.purchase_order_id and record.purchase_order_id.currency_rate:
                record.price_unit_rd = record.price_unit_usd / record.purchase_order_id.currency_rate
            else:
                record.price_unit_rd = record.price_unit_usd * record.currency_rate_usd

            record.amount_total_usd = record.price_unit_usd * record.product_uom_qty
            record.amount_total_rd = record.price_unit_rd * record.product_uom_qty

    @api.depends('amount_total_usd', 'amount_total_rd')
    @api.depends_context('landed_cost_id', 'active_id')
    def _compute_factor(self):
        landed_cost = self.env['stock.landed.cost'].browse(
            self._context.get('landed_cost_id') or self._context.get('active_id')
        )

        if landed_cost:
            stock_move_ids = landed_cost._get_move_ids_without_package()
            total_usd = sum(stock_move_ids.mapped('amount_total_usd'))
            total_rd = sum(stock_move_ids.mapped('amount_total_rd'))
            if total_usd:
                self.factor = (landed_cost.amount_total + total_rd) / total_usd
            else:
                self.factor = 1.0
        else:
            self.factor = 1.0

    @api.depends('price_unit_usd', 'currency_rate_usd', 'factor')
    def _compute_current_totals(self):
        for record in self:
            record.current_price_unit_rd = record.price_unit_usd * record.factor
            record.current_total_rd = record.current_price_unit_rd * record.product_uom_qty
            record.current_price_unit_usd = (
                record.current_price_unit_rd / record.currency_rate_usd
                if record.currency_rate_usd else 0.0
            )
            record.current_total_usd = record.current_price_unit_usd * record.product_uom_qty

    @api.depends('pvp_usd', 'pvp_rd', 'current_price_unit_usd', 'current_price_unit_rd', 'product_uom_qty')
    def _compute_extra_indicators(self):
        for record in self:
            if record.pvp_usd:
                record.margin = (record.pvp_usd - record.current_price_unit_usd) * 100 / record.pvp_usd
            else:
                record.margin = 0.0
            record.profit_usd = (record.pvp_usd - record.current_price_unit_usd) * record.product_uom_qty
            record.profit_rd = (record.pvp_rd - record.current_price_unit_rd) * record.product_uom_qty

    def get_date_from_landed_cost(self):
        return (
            self._context.get('landed_cost_date')
            or self._context.get('date')
            or fields.Date.today()
        )

    def get_lst_price_from_product(self, vals, date=None):
        picking_id = vals.get('picking_id')
        purchase_line_id = vals.get('purchase_line_id')

        purchase_order_id = (
            picking_id and self.env['stock.picking'].browse(picking_id).purchase_id
        ) or (
            purchase_line_id and self.env['purchase.order.line'].browse(purchase_line_id).order_id
        )

        if purchase_order_id:
            currency_rate = purchase_order_id.currency_rate
        else:
            currency_rate = self.env["res.currency"].with_context({
                'date': date or self.get_date_from_landed_cost(),
            }).search([("name", "=", "USD")]).rate

        product = self.env['product.product'].browse(vals.get('product_id'))
        return product.list_price * currency_rate

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list['pvp_usd'] = self.get_lst_price_from_product(vals_list)
        elif isinstance(vals_list, list):
            for vals in vals_list:
                vals['pvp_usd'] = self.get_lst_price_from_product(vals)
        return super().create(vals_list)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    landed_costs_ids = fields.Many2many(
        'stock.landed.cost',
        string='Costes de destino',
        copy=False
    )


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    currency_rate_date_pos_usd = fields.Date(
        string="Fecha Tasa USD (OC)",
        compute="_compute_currency_rate_date_pos_usd",
        readonly=True,
    )
    currency_rate_pos_usd = fields.Float(
        string="Tasa USD (OC)",
        compute="_compute_currency_rate_pos_usd",
        readonly=True,
    )

    @api.depends('currency_rate')
    def _compute_currency_rate_pos_usd(self):
        for record in self:
            record.currency_rate_pos_usd = 1/record.currency_rate

    @api.depends('date_order')
    def _compute_currency_rate_date_pos_usd(self):
        for record in self:
            if record.currency_id.name == 'USD':
                record.currency_rate_date_pos_usd = record.currency_id.rate_ids.filtered(
                    lambda x: x.name <= record.date_order.date()
                ).sorted(key=lambda x: x.name, reverse=True)[0].name
            else:
                record.currency_rate_date_pos_usd = False


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    total_closeouts = fields.Integer(
        string="Total de liquidaciones",
        compute="_compute_total_closeouts",
        readonly=True,
    )
    currency_rate_date_usd = fields.Date(
        string="Fecha Tasa USD (LC)",
        compute="_compute_currency_rate_usd",
        readonly=True,
    )
    currency_rate_usd = fields.Float(
        string="Tasa USD (LC)",
        compute="_compute_currency_rate_usd",
        readonly=True,
    )
    purchase_ids = fields.Many2many(
        'purchase.order',
        compute="_compute_get_purchase_order",
        readonly=True,
    )
    factor = fields.Float(
        string="Factor",
        compute="_compute_detail_metrics",
        readonly=True,
        help='Factor de costes en destino. Dado por el cálculo: ( "Total de costos adicionales" + "TotalFOB (RD)" ) / "Total FOB (USD)"',
    )
    avg_margin = fields.Float(
        string=u"Margen promedio %",
        compute="_compute_detail_metrics",
        readonly=True,
        help='Margen promedio de la ganancia, expresado en valor porcentual',
    )
    median_margin = fields.Float(
        string=u"Margen medio %",
        compute="_compute_detail_metrics",
        readonly=True,
        help='Calculo de mediana del margen de ganancia, expresado en valor porcentual',
    )
    metrics = fields.Text(
        string="Métricas",
        compute="_compute_detail_metrics",
        readonly=True,
        help=(
            'Total FOB: Total del costo de acuerdo a los precios unitarios en la orden de compra. Para conversión entre monedas emplea la Tasa USD (OC) \n'
            'Costo total actual: Costo total de los productos luego de aplicar el factor de costos en destino. Para la conversión entre monedas emplea la Tasa USD (LC) \n'
            'PVP Promedio: Precio unitario de venta promedio de los productos. Para la conversión entre monedas emplea la Tasa USD (OC) \n'
            'PVP Media: Calculo de mediana de precios unitarios de venta de los productos. Para la conversión entre monedas emplea la Tasa USD (OC) \n'
            'Total ganancia: Suma de las ganancias. Para la conversión entre monedas emplea la Tasa USD (LC)'
        )
    )

    @api.depends('picking_ids')
    def _compute_total_closeouts(self):
        for record in self:
            record.total_closeouts = len(record._get_move_ids_without_package().ids)

    @api.depends('date')
    def _compute_currency_rate_usd(self):
        for record in self:
            currency = self.env["res.currency"].with_context({
                'date': record.date,
            }).search([('name', '=', 'USD')], limit=1)
            record.currency_rate_usd = currency.inverse_rate
            record.currency_rate_date_usd = currency.rate_ids.filtered(
                lambda x: x.name <= record.date
            ).sorted(key=lambda x: x.name, reverse=True)[0].name

    @api.depends('picking_ids')
    def _compute_get_purchase_order(self):
        for record in self:
            record.purchase_ids = record.picking_ids.purchase_id

    def _get_stock_moves(self) -> 'StockMove':
        self.ensure_one()
        return self.env['stock.move'].with_context({
            "landed_cost_id": self.id,
            "landed_cost_date": self.date
        }).browse(self._get_move_ids_without_package().ids)

    @api.depends('picking_ids')
    def _compute_detail_metrics(self):
        for record in self:
            stock_moves = record._get_stock_moves()

            if stock_moves:
                record.factor = stock_moves[0].factor

                margin_values = stock_moves.mapped('margin')
                record.avg_margin = mean(margin_values)
                record.median_margin = median(margin_values)

                metrics = record._get_metrics(stock_moves)
                record.metrics = json.dumps(
                    list(metrics.values()),
                )

            else:
                record.factor = 1.0
                record.avg_margin = 0.0
                record.median_margin = 0.0
                record.metrics = json.dumps([])

    def _get_metrics(self, stock_moves=None) -> OrderedDict:
        self.ensure_one()
        stock_moves = stock_moves or self._get_stock_moves()

        amount_total_usd = stock_moves.mapped('amount_total_usd')
        amount_total_rd = stock_moves.mapped('amount_total_rd')

        current_total_usd = stock_moves.mapped('current_total_usd')
        current_total_rd = stock_moves.mapped('current_total_rd')

        pvp_usd = stock_moves.mapped('pvp_usd')
        pvp_rd = stock_moves.mapped('pvp_rd')

        profit_usd = stock_moves.mapped('profit_usd')
        profit_rd = stock_moves.mapped('profit_rd')

        return OrderedDict([
            ("total_fob", {
                "string": "Total FOB",
                "usd": sum(amount_total_usd),
                "rd": sum(amount_total_rd)
            }),
            ("current_total_cost", {
                "string": "Costo Total Actual",
                "usd": sum(current_total_usd),
                "rd": sum(current_total_rd)
            }),
            ("avg_pvp", {
                "string": "PVP Promedio",
                "usd": mean(pvp_usd),
                "rd": mean(pvp_rd)
            }),
            ("median_pvp", {
                "string": "PVP Media",
                "usd": median(pvp_usd),
                "rd": median(pvp_rd)
            }),
            ("total_profit", {
                "string": "Total Ganancia",
                "usd": sum(profit_usd),
                "rd": sum(profit_rd)
            })
        ])

    def _get_move_ids_without_package(self):
        self.ensure_one()
        return reduce(
            lambda p1, p2: p1 | p2.move_ids_without_package,
            self.picking_ids,
            self.env["stock.move"]
        )

    def action_view_closeouts_detail(self):
        move_ids = self._get_move_ids_without_package().ids
        action = self.env["ir.actions.actions"]._for_xml_id(
            "lc_detail_and_indicators.closeouts_detail_action_window"
        )
        return dict(
            action,
            view_type='list',
            domain=[('id', 'in', move_ids)],
            context=dict(
                self.env.context,
                landed_cost_id=self.id,
                landed_cost_date=self.date
            )
        )

    @property
    def dict_metrics(self):
        self.ensure_one()
        return json.loads(self.metrics)
