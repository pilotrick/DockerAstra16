# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
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

from odoo import api, fields, models
from datetime import datetime, timedelta, date



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rfq_count = fields.Integer('RFQ', compute='_compute_rfq_count')

    def action_create_rfq(self):
        order_lines = []
        for line in self.order_line:
            vals = {'name': line.name,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'date_planned': date.today(),
                    'date_order': date.today(),
                    'taxes_id': [(6, 0, line.tax_id.ids)]
                    }
            order_lines.append((0, 0, vals))
        action = self.env["ir.actions.actions"]._for_xml_id("iwesabe_rfq_from_sale.action_create_rfq_from_sale")
        action['context'] = {
            'default_related_so_id': self.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_order_line': order_lines,
        }
        if self.user_id:
            action['context']['default_user_id'] = self.user_id.id
        return action

    def _compute_rfq_count(self):
        for so in self:
            rfq = self.env['purchase.order'].search([('related_so_id', '=', so.id)])
            so.rfq_count = len(rfq)

    def action_get_rfq_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
        action['domain'] = [('related_so_id', '=', self.id)]
        action['view_mode'] = 'tree,form'
        action['views'] = [(k, v) for k, v in action['views'] if v in ['tree', 'form']]
        return action
    

    