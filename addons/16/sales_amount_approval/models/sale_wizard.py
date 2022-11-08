# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools,_
from odoo.exceptions import UserError


class WizardInvoiceSaleCommission(models.TransientModel):
    _name = 'wizard.sales.confirm'
    _description = 'Sales Confirmation'

    name = fields.Char("Order")

    def confirm(self):
        mail_activity = self.env['mail.activity']
        sale_order = self.env['sale.order'].search([('id','=',self._context.get('active_id'))])
        body = ('Your Sales Order %s has been confirmed by %s. Total amount is %s which is less than %s') % (sale_order.name,self.env.user.name,sale_order.amount_total,self._context.get('amount_range'))
        if self.user_has_groups('sales_amount_approval.group_saa_manager'):
            # sale_order.with_context(confirm='yes').action_confirm()
            sale_order.group_button = '1'
            return sale_order.with_context(confirm='yes').action_sale_ok()
            #activity
            # model_id = self.env.ref('sale.model_sale_order')
            # type_id = self.env.ref('mail.mail_activity_data_todo')
            # activity_data = {
            #     'res_id': sale_order.id,
            #     'res_model_id': model_id.id,
            #     'activity_type_id': type_id.id,
            #     'summary': body,
            #     'user_id': self.env.user.sale_user_approver.id,
            # }
            # mail_activity.create(activity_data)
        else:
            sale_order.group_button = '0'
            # raise UserError(_("Non Manager user cannot confirm the sales"))
        pass


class SaleOrderGroup(models.Model):
    _inherit = "sale.order"

    group_button = fields.Char("Group",copy=False)
    group_button_logic = fields.Char("Group",compute="compute_group")

    def compute_group(self):
        if self.user_has_groups('sales_amount_approval.group_saa_manager') or self.env.is_admin():
            self.group_button = '1'
        else:
             self.group_button = '0'
        self.group_button_logic = self.group_button

    def action_sale_ok(self):
        amount_range = self.env['ir.config_parameter'].sudo().get_param('sales_amount_approval.amount_range')
        print('amount range',amount_range)
        if not (self._context.get('confirm') == 'yes') and self.amount_total < float(amount_range):
            view = self.env.ref('sales_amount_approval.view_wizard_sales_confirm')
            return {
                    'name': _('Allow Permission to Confirm?'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'wizard.sales.confirm',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'context':{'amount_range':amount_range,'default_name':"Your Your Amount is under %s. Do you want to confirm? Contact your adminstrator" % amount_range} ,
                }
        else:
            res = super(SaleOrderGroup, self).action_sale_ok()
            res['context'] = {'so': self.id}
            return res
    # def action_confirm(self):
    #     amount_range = self.env['ir.config_parameter'].sudo().get_param('sales_amount_approval.amount_range')
    #     print('amount range',amount_range)
    #     if not (self._context.get('confirm') == 'yes') and self.amount_total < float(amount_range):
    #         view = self.env.ref('sales_amount_approval.view_wizard_sales_confirm')
    #         return {
    #                 'name': _('Allow Permission to Confirm?'),
    #                 'type': 'ir.actions.act_window',
    #                 'view_mode': 'form',
    #                 'res_model': 'wizard.sales.confirm',
    #                 'views': [(view.id, 'form')],
    #                 'view_id': view.id,
    #                 'target': 'new',
    #                 'context':{'amount_range':amount_range} ,
    #             }
    #     else:
    #         res = super(SaleOrderGroup, self).action_confirm()
    #         return res