# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp
from itertools import groupby
from odoo.osv.expression import AND



_logger = logging.getLogger(__name__)

class pos_config(models.Model):
    _inherit = 'pos.config' 

    allow_multi_uom = fields.Boolean('Product multi uom', default=True)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_multi_uom = fields.Boolean(related='pos_config_id.allow_multi_uom', readonly=False)

class product_multi_uom(models.Model):
    _name = 'product.multi.uom'
    _order = "sequence desc"

    multi_uom_id = fields.Many2one('uom.uom','Unit of measure')
    product_id = fields.Many2one('product.product','Product')
    price = fields.Float("Sale Price",default=0)
    sequence = fields.Integer("Sequence",default=1)

    @api.onchange('multi_uom_id')
    def unit_id_change(self):
        domain = {'multi_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        return {'domain': domain}

class product_product(models.Model):
    _inherit = 'product.product'
    
    has_multi_uom = fields.Boolean('Has multi UOM')
    multi_uom_ids = fields.One2many('product.multi.uom','product_id')

class PosOrder(models.Model):
    _inherit = "pos.order"

    def _prepare_invoice_line(self, order_line):
        result = super()._prepare_invoice_line(order_line)
        result['product_uom_id'] = order_line.product_uom.id or order_line.product_uom_id.id
        return result
        
class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    product_uom = fields.Many2one('uom.uom','Unit of measure')

    def _export_for_ui(self, orderline):
        res = super(PosOrderLine, self)._export_for_ui(orderline)
        if orderline.product_uom:
            res['product_uom'] = orderline.product_uom.id;
        else:
            res['product_uom'] = orderline.product_uom_id.id;
        return res

class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if self.config_id.allow_multi_uom:
            new_model = 'product.multi.uom'
            if new_model not in result:
                result.append(new_model)
        return result

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['has_multi_uom','multi_uom_ids'])
        return result

    def _loader_params_product_multi_uom(self):
        return {'search_params': {'domain': [], 'fields': ['multi_uom_id','price'], 'load': False}}

    def _get_pos_ui_product_multi_uom(self, params):
        result = self.env['product.multi.uom'].search_read(**params['search_params'])
        for res in result:
            uom_id = self.env['uom.uom'].browse(res['multi_uom_id'])
            res['multi_uom_id'] = [uom_id.id,uom_id.name] 
        return result

class StockPicking(models.Model):
    _inherit='stock.picking'

    def _prepare_stock_move_vals(self, first_line, order_lines):
        res = super(StockPicking, self)._prepare_stock_move_vals(first_line, order_lines)
        res['product_uom'] = first_line.product_uom.id or first_line.product_id.uom_id.id,
        return res

    def _create_move_from_pos_order_lines(self, lines):
        self.ensure_one()
        # lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: l.product_id.id)
        lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: (l.product_id.id,l.product_uom.id))

        move_vals = []
        for dummy, olines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*olines)
            move_vals.append(self._prepare_stock_move_vals(order_lines[0], order_lines))
        moves = self.env['stock.move'].create(move_vals)
        confirmed_moves = moves._action_confirm()
        confirmed_moves._add_mls_related_to_order(lines, are_qties_done=True)

class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):

        """ Serialise the orders of the day information

        params: date_start, date_stop string representing the datetime of order
        """
        domain = [('state', 'in', ['paid','invoiced','done'])]

        if (session_ids):
            domain = AND([domain, [('session_id', 'in', session_ids)]])
        else:
            if date_start:
                date_start = fields.Datetime.from_string(date_start)
            else:
                # start by default today 00:00:00
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
                date_start = today.astimezone(pytz.timezone('UTC'))

            if date_stop:
                date_stop = fields.Datetime.from_string(date_stop)
                # avoid a date_stop smaller than date_start
                if (date_stop < date_start):
                    date_stop = date_start + timedelta(days=1, seconds=-1)
            else:
                # stop by default today 23:59:59
                date_stop = date_start + timedelta(days=1, seconds=-1)

            domain = AND([domain,
                [('date_order', '>=', fields.Datetime.to_string(date_start)),
                ('date_order', '<=', fields.Datetime.to_string(date_stop))]
            ])

            if config_ids:
                domain = AND([domain, [('config_id', 'in', config_ids)]])

        orders = self.env['pos.order'].search(domain)

        user_currency = self.env.company.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id._convert(
                    order.amount_total, user_currency, order.company_id, order.date_order or fields.Date.today())
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                product_uom = line.product_uom if line.product_uom else line.product_id.uom_id
                key = (line.product_id, line.price_unit, line.discount, product_uom)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount':0.0, 'base_amount':0.0})
                        taxes[tax['id']]['tax_amount'] += tax['amount']
                        taxes[tax['id']]['base_amount'] += tax['base']
                else:
                    taxes.setdefault(0, {'name': _('No Taxes'), 'tax_amount':0.0, 'base_amount':0.0})
                    taxes[0]['base_amount'] += line.price_subtotal_incl

        payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', orders.ids)]).ids
        if payment_ids:
            self.env.cr.execute("""
                SELECT method.name, sum(amount) total
                FROM pos_payment AS payment,
                     pos_payment_method AS method
                WHERE payment.payment_method_id = method.id
                    AND payment.id IN %s
                GROUP BY method.name
            """, (tuple(payment_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        return {
            'currency_precision': user_currency.decimal_places,
            'total_paid': user_currency.round(total),
            'payments': payments,
            'company_name': self.env.company.name,
            'taxes': list(taxes.values()),
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'discount': discount,
                'uom': product_uom.name
            } for (product, price_unit, discount,product_uom), qty in products_sold.items()], key=lambda l: l['product_name'])
        }
