# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, api, _

class UpdateVendor(models.TransientModel):
	_name = 'update.vendor' 
	_description = "Update Vendor"


	partner_id = fields.Many2one('res.partner' , string="Existing Vendor")
	new_partner_id = fields.Many2one('res.partner' , string="New Vendor")

	@api.model
	def default_get(self , fields):
		res = super(UpdateVendor, self).default_get(fields)
		purchase_order = self.env['purchase.order'].browse(self._context.get('active_ids'))
		res['partner_id'] = purchase_order.partner_id.id
		return res


	def update_vendor(self):
		purchase_order_id = self.env['purchase.order'].browse(self._context.get('active_ids'))
		if purchase_order_id:
			purchase_order_id.update({
					'partner_id' :self.new_partner_id,
				})

			if purchase_order_id.picking_ids:
				for picking in purchase_order_id.picking_ids:
					picking.partner_id = self.new_partner_id

			if purchase_order_id.invoice_ids:
				for invoice in purchase_order_id.invoice_ids:
					invoice.partner_id = self.new_partner_id
					payment_ids = self.env['account.payment'].search([('ref' , 'ilike' , invoice.name)])
					if payment_ids:
						payment_ids.update({
							'partner_id' :self.new_partner_id,
						})

					move_ids = self.env['account.move'].search([('ref' , 'ilike' , invoice.name)])
					if move_ids:
						move_ids.update({
							'partner_id' : self.new_partner_id,
						})


			if purchase_order_id.invoice_ids: 
				line_ids = self.env['account.move.line'].search([('payment_id' , 'in' , payment_ids.ids)])	
				if line_ids:
					line_ids.update({
						'partner_id' : self.new_partner_id,
					})

				move_line_ids = self.env['account.move.line'].search([('move_id' , 'in' , purchase_order_id.invoice_ids.ids)])
				if move_line_ids:
					move_line_ids.update({
						'partner_id' : self.new_partner_id,
					})
	
				