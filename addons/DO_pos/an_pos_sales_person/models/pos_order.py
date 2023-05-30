# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_invoice_line(self, order_line):
        res = super(PosOrder, self)._prepare_invoice_line(order_line)
        if self.session_id and self.session_id.config_id.allow_salesperson:
            res['it_salesperson'] = order_line.it_salesperson.id
        return res


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    it_salesperson = fields.Many2one("hr.employee", string="Salesperson")

    def _export_for_ui(self, orderline):
        """Este metodo se llama cuando se desea consultar los pedidos q ya fueron pagados.

        :param dict orderline: dictionary representing the orderline.
        :returns: dict order.line
        """
        result = super(PosOrderLine, self)._export_for_ui(orderline)
        result.update({
            'it_salesperson': orderline.it_salesperson.id,
        })
        return result
