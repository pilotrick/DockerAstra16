# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    cost_center_id = fields.Many2one("cost.center", string="Centro de Costo")

    @api.onchange('cost_center_id')
    def set_cost_center(self):
        print("on change cost center")
        for line in self.order_line:
            line.cost_center_id = self.cost_center_id.id

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({
            'cost_center_id': self.cost_center_id and self.cost_center_id.id or False
        })
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cost_center_id = fields.Many2one("cost.center", string="Centro de Costo",)

    @api.onchange('product_uom_qty')
    def set_default_cost_center(self):

        if self.order_id.cost_center_id:
            self.cost_center_id = self.order_id.cost_center_id.id
   
    def _prepare_invoice_line(self, **optional_values):
        invoice_line_cost = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        invoice_line_cost['cost_center_id'] = self.cost_center_id and self.cost_center_id.id or False
        return invoice_line_cost
