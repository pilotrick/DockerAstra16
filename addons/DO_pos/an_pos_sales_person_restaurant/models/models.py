# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_order_line(self):
        fields = super(PosOrder, self)._get_fields_for_order_line()
        fields.extend(['it_salesperson'])
        return fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    def _order_line_fields(self, line, session_id=None):
        result = super()._order_line_fields(line, session_id)
        vals = result[2]
        if 'it_salesperson' in vals:
            it_salesperson = vals['it_salesperson']
            if type(it_salesperson) is list:
                vals['it_salesperson'] = it_salesperson[0]
        return result
