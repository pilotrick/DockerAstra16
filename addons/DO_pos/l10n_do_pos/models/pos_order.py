# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = "pos.order"

    ncf = fields.Char("NCF")
    ncf_invoice_related = fields.Char(related="account_move.l10n_latam_document_number", string="NCF Factura")
    origin_ncf = fields.Char(related="account_move.l10n_do_origin_ncf", string="Modifies")
    sale_fiscal_type = fields.Many2one(related="account_move.l10n_latam_document_type_id",
                                       string="Tipo", readonly=True)

    def _create_invoice(self, move_vals):
        inv = super(PosOrder, self)._create_invoice(move_vals)
        if move_vals['move_type'] == 'out_refund':
            inv.l10n_do_origin_ncf = self.ncf

        return inv

    @api.model
    def get_from_ui(self, order):
        pos_order = self.sudo().search([('pos_reference', '=', order)])
        return {
            'ncf_invoice_related': pos_order.ncf_invoice_related,
        }

    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super(PosOrder, self).create_from_ui(orders, draft)
        self = self.browse(res)

        for record in res:
            record['ncf'] = self.browse(record.get('id')).ncf_invoice_related
            record['sale_fiscal_type'] = self.browse(record.get('id')).sale_fiscal_type.name
            record['origin_ncf'] = self.browse(record.get('id')).origin_ncf

        return res

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        res['ncf'] = ui_order.get('ncf', False)
        return res

    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result.update({
            'sale_fiscal_type': order.sale_fiscal_type.name,
            'origin_ncf': order.origin_ncf,
            'ncf': order.ncf_invoice_related,
        })
        return result
