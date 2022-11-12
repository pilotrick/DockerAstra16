# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# Part of AktivSoftware License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# for licensing details.


from odoo import models, fields

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResFact(models.Model):
    _inherit = 'sale.order.line'

    resfactname  = fields.Char(string='Numero Factura',  compute='rickyfactnombre')
    
    
    @api.depends('invoice_lines')
    def rickyfactnombre(self):
        for ResFact in self:
            Facturas = []
            for il in ResFact.invoice_lines:
                Facturas.append(il.move_id.name)
            ResFact.resfactname = " ".join(Facturas)

class ResPartner(models.Model):
    _inherit = "res.partner"
    sale_product_count = fields.Integer(compute='_compute_sale_product_count')
    sale_product_ids = fields.One2many('sale.order.line', 'order_partner_id', string='Shopped Products', copy=False)
    def _compute_sale_product_count(self):
        """
        This method is compute the Total no of order line for main partner and their child contact and count it
        Assign to the: sale_product_count field
        :return: Integer
        """
        sale_product_data = self.env['sale.order.line'].read_group(domain=[(
            'order_partner_id', 'child_of', self.ids), (
            'is_downpayment', '=', False)], fields=['order_partner_id'],
            groupby=['order_partner_id'])
        # read to keep the child/parent relation
        # while aggregating the read_group result in the loop
        partner_child_ids = self.read(['child_ids'])
        mapped_data = dict([(sale_data['order_partner_id'][0], sale_data[
            'order_partner_id_count']) for sale_data in sale_product_data])
        for partner in self:
            # let's obtain the partner id and
            # all its child ids from the read up there
            item = next(
                partner_child_id for partner_child_id in partner_child_ids
                if partner_child_id['id'] == partner.id)
            partner_ids = [partner.id] + item.get('child_ids')
            # then we can sum for all the partner's child
            partner.sale_product_count = sum(
                mapped_data.get(child, 0) for child in partner_ids)
