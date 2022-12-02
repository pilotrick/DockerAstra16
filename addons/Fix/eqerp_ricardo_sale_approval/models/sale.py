# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import models, api, fields, _
from odoo.tools.misc import format_date
import time
from odoo.exceptions import ValidationError,Warning
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class sale_order(models.Model):
    _inherit = "sale.order"

    is_minimum_sale_margin = fields.Boolean(string="Minimum Sales Margin",default=False,compute='cal_sales_order_margin',store=True)

    state = fields.Selection(selection_add=[('waiting_sale_approval', 'Waiting for Sale Approval'),
                                            ('sale_approval', 'Sale Approval'),
                                            ('decline_approval','Decline Approval')])

    sale_approverl_id = fields.Many2one('res.users', 'Sale Order Approver', readonly=True, copy=False, tracking=True)
    is_sale_approval = fields.Boolean(string="Sale Approval",copy=False)
    is_sale_confirm = fields.Boolean(string="Sale Confirm",copy=False)
    need_sale_approval = fields.Boolean(string="Need Sale Approval",copy=False)

    @api.model
    def create(self,vals):
        res = super(sale_order,self).create(vals)
        for order in res:
            order.check_users_sale_approval()
        return res

    def write(self,vals):
        res = super(sale_order,self).write(vals)
        for order in self:
            order.check_users_sale_approval()
        return res

    def check_users_sale_approval(self):
        order = self
        if order.state in ['draft','sent']:
            user = self.env.user
            date_order = order.date_order
            today_date = datetime.today()
            if order.is_minimum_sale_margin:
                order.state = 'waiting_sale_approval'
                order.action_create_sale_approval_activity()
                if user.next_date_so_permission and user.next_date_so_permission >= today_date.date():
                    order.action_approve_sale()

    def action_cancel(self):
        res = super(sale_order,self).action_cancel()
        for order in self:
            order.sale_approverl_id = False
            order.is_sale_approval = False
        return res

    def action_confirm(self):
        for order in self:
            if order.is_minimum_sale_margin and order.state in ['draft','sent','waiting_sale_approval']:
                continue
            else:
                order.is_sale_confirm = True
                super(sale_order,self).action_confirm()
        return True

    def action_approve_sale(self):
        for order in self:
            user = self.env.user
            if not user.next_date_so_permission or user.next_date_so_permission < datetime.today().date():
                return {
                    'name': 'Sales Approval',
                    'type': 'ir.actions.act_window',
                    'res_model': 'wizard.sales.approval',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context':{'sale_order_id':order.id,'user':user.id}
                }
            else:
                order.write({'state':'sale_approval','sale_approverl_id':user.id,'is_sale_approval':True,'is_sale_confirm':False})

    @api.depends('order_line.margin', 'amount_untaxed')
    def cal_sales_order_margin(self):
        for order in self:
            user = self.env.user
            is_minimum_sale_margin = False
            user_sales_margin = user.minimum_sales_margin
            if order.currency_id.id != order.company_id.currency_id.id:
                user_sales_margin = order.currency_id._convert(user_sales_margin, order.company_id.currency_id, order.company_id, order.date_order or fields.Date.today())
            if order.order_line and user.minimum_sales_margin and order.state in ['draft','sent','waiting_sale_approval']:
                if order.margin < user_sales_margin or order.margin < 0:
                    is_minimum_sale_margin = True
            order.is_minimum_sale_margin = is_minimum_sale_margin

    def action_create_sale_approval_activity(self):
        for record in self:
            if self.env.user.sale_user_representative_id:
                order_id = self.env['sale.order'].browse(self._context.get('active_id'))
                model_id = self.env.ref('sale.model_sale_order')
                type_id = self.env.ref('mail.mail_activity_data_todo')
                summary = 'órdenes de venta - %s está por debajo del margen permitido de %s' % (self.name,self.env.user.minimum_sales_margin)
                activity_data = {
                    'res_id': self.id,
                    'res_model_id': model_id.id,
                    'activity_type_id': type_id.id,
                    'summary': summary,
                    'user_id': self.env.user.sale_user_representative_id.id,
                }
                self.env['mail.activity'].create(activity_data)
        return True
    
    def btn_decline_approval(self):
        self.write({'state': 'decline_approval'})


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('margin')
    def onchange_product_id_field(self):
        title = False
        message = False
        result = {}
        warning = {}
        user = self.env.user
        if not self.product_id:
            return result
        if user.minimum_sales_margin and self.margin:
            if self.margin < user.minimum_sales_margin:
                title = _("Warning for sale margin limit!")
                message = (_('Product %s sale below margin limit.') % (self.product_id.display_name))
                warning['title'] = title
                warning['message'] = message
                result = {'warning': warning}
        return result


class res_user(models.Model):
    _inherit = 'res.users'

    @api.constrains('minimum_sales_margin')
    def check_minimum_sales_margin(self):
        for user in self:
            if user.minimum_sales_margin < 0:
                raise ValidationError(_("please enter proper margin amount."))

    minimum_sales_margin = fields.Float(string="Minimum Sales Margin",copy=False)
    next_date_so_permission = fields.Date(string="Till Date sales Approval",copy=False)
    sale_user_representative_id = fields.Many2one('res.users',string="Users")


class wizard_sales_approval(models.TransientModel):
    _name = 'wizard.sales.approval'
    _description = "Sale Approval Wizard"

    @api.constrains('next_date_so_permission')
    def check_next_date_so_permission(self):
        for each in self:
            today_date = datetime.today().date()
            if each.next_date_so_permission < today_date:
                raise ValidationError(_("please enter proper date.")) 

    next_date_so_permission = fields.Date(string="Next sales approval",copy=False,
                    help="it allows user to automatically sales approval till next date.")

    def do_confirm(self):
        order_id = self.env['sale.order'].browse(self._context.get('sale_order_id'))
        user_id = self.env['res.users'].browse(self._context.get('user'))
        if user_id:
            user_id.sudo().next_date_so_permission = self.next_date_so_permission
        if order_id:
            order_id.write({'state':'sale_approval','sale_approverl_id':user_id.id,'is_sale_approval':True,'is_sale_confirm':False})
