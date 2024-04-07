# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, fields, models , _


class customer_limit_wizard(models.TransientModel):
    _name = "customer.limit.wizard"
    _description = 'Customer Credit Limit Wizard'

    message = fields.Char()
    users_ids = fields.Many2many('res.users','users_sale_wizard_rel','sale_id','user_id','Users')

    def action_create_activity(self):
        for record in self:
            order_id = self.env['sale.order']
            if self._context.get('so'):
                order_id = order_id.browse(self._context.get('so'))
            else:
                order_id = order_id.browse(self._context.get('active_id'))
            model_id = self.env.ref('sale.model_sale_order')
            type_id = self.env.ref('mail.mail_activity_data_todo')
            summary = 'El pedido ha sido bloqueado por superar el limite de credito, por favor revisar'
            users = record.users_ids
            for user in users:
                activity_data = {
                    'res_id': order_id.id,
                    'res_model_id': model_id.id,
                    'activity_type_id': type_id.id,
                    'summary': summary,
                    'user_id': user.id,
                }
                self.env['mail.activity'].create(activity_data)
        return True
    
    def set_credit_limit_state(self):
        # order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        order_id = self.env['sale.order']
        if self._context.get('so'):
            order_id = order_id.browse(self._context.get('so'))
        else:
            order_id = order_id.browse(self._context.get('active_id'))
        order_id.state = 'credit_limit'
        self.action_create_activity()
        partner_id = self.partner_id
        if partner_id.parent_id:
            partner_id= partner_id.parent_id
        partner_id.credit_limit_on_hold = self.credit_limit_on_hold
        return True
    
    current_sale = fields.Float('Current Quotation')
    credit = fields.Float('Total Receivable')
    partner_id = fields.Many2one('res.partner',string="Customer")
    credit_limit = fields.Float(related='partner_id.credit_limit',string="Credit Limit")
    due_invoice = fields.Char("Due Invoice")
    total_invoices = fields.Float("Total Invoices")
    credit_limit_on_hold = fields.Boolean('Credit Limit on Hold')

    def action_view_invoice(self):
        return {
            'name': _("Invoices"),
            'domain': [('partner_id','=', self.partner_id.id)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
    def action_view_quotation(self):
        return {
            'name': _("Quotations"),
            'domain': [('partner_id','=', self.partner_id.id),('state','=','draft')],
            'view_type': 'form',
            'res_model': 'sale.order',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
