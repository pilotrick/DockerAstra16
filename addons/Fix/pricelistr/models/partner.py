# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import Warning


class wizard_customer_pricelist(models.TransientModel):
    _name = 'wizard.customer.pricelist'

    date_from = fields.Date(string="Date From")
    partner_ids = fields.Many2many('res.partner', string="Customer(s)")

    def action_create_pricelist(self):
        if not self.partner_ids:
            raise Warning(_("Please select Customer."))
        pricelist_obj = self.env['product.pricelist']
        today_date = datetime.today().date()
        for partner in self.partner_ids:
            child_partner = self.env['res.partner'].search([('id', 'child_of', partner.ids)])
            self._cr.execute("""SELECT sol.product_id, max(sol.price_unit) as higher_price
                                    FROM sale_order_line sol
                                    LEFT JOIN sale_order so on so.id = sol.order_id
                                    WHERE order_partner_id in %s
                                        AND so.date_order::date >= %s
                                        AND so.date_order::date <= %s
                                        AND so.state != 'cancel'
                                    GROUP BY sol.product_id""", (tuple(child_partner.ids), self.date_from, today_date))
            result = self._cr.dictfetchall()
            if result:
                vals = {'name': partner.name + " - " + today_date.strftime('%Y-%m-%d'),
                        'customer_id': partner.id}
                items_list = []
                for each in result:
                    items_list.append((0, 0, {'applied_on': '0_product_variant',
                                              'product_id': each['product_id'],
                                              'compute_price': 'fixed',
                                              'fixed_price': each['higher_price']}))
                vals.update({'item_ids': items_list})
                pricelist_id = pricelist_obj.create(vals)
                if pricelist_id:
                    pricelist_obj.search([('customer_id', '=', partner.id),
                                          ('id', '!=', pricelist_id.id)]).write({'active': False})
                    partner.write({'property_product_pricelist': pricelist_id.id})


class product_pricelist(models.Model):
    _inherit = 'product.pricelist'

    customer_id = fields.Many2one('res.partner', string="Customer")
