# -*- coding: utf-8 -*-

from odoo import fields, models,tools,api
import json

class pos_config(models.Model):
    _inherit = 'pos.config' 

    wv_session_id = fields.Many2one("pos.sync.session","Sync Session")
    allow_incoming_orders = fields.Boolean('Allow Incoming order', default=True)
    session_short_name = fields.Char("Session Nickname",default="POS")
    allow_auto_sync = fields.Boolean("Allow Auto Sync",default=True, help="If you don't allow auto Sync The Sync button will display to sync the order.")

class pos_sync_session(models.Model):
    _name = "pos.sync.session"

    name = fields.Char("Session Name")
    pos_config_id = fields.One2many("pos.config","wv_session_id")
    order_ids = fields.One2many('pos.sync.order', 'sync_session_id')

    @api.model
    def multi_session_update(self, *args):
        if args:
            session_id = args[0] if len(args) > 0 else 0
            order = args[1] if len(args) > 1 else {}
            res = self.env["pos.sync.session"].browse(int(session_id)).order_operations(order)
            return res
        else:
            return False


    def order_operations(self, order):
        self.ensure_one()
        if order['action'] == 'update_order':
            order_data = order['order']
            pos_order = self.env['pos.sync.order'].search([('order_ref', '=',order_data['uid'])])
            if pos_order:
                pos_order.write({'pos_order': json.dumps(order)})
            else:
                pos_order.create({'pos_order': json.dumps(order),'sync_session_id': self.id,'order_ref': order_data['uid']})
            self.sync_order(order)
            return True
        elif order['action'] == 'remove_order':
            if 'order' in order:
                order_uid = order['order']
                wv_order = self.order_ids.search([('order_ref', '=', order_uid)])
                wv_order.unlink()
                self.sync_order(order)
            return True
        elif order['action'] == 'sync_all_orders':
            # pos_config_id = order['order']
            # pos = self.env['pos.config'].search([('wv_session_id', '=', self.id), ("id", "=", pos_config_id)])
            messages = []
            for order in self.order_ids:
                orderval = json.loads(order.pos_order)
                orderval['action'] = 'sync_all_orders'
                messages.append(orderval)
            return {'action':'sync_all_orders','order':messages}

    def sync_order(self, order):
        self.ensure_one()
        notifications = []
        for pos_session in self.env['pos.session'].search([('state', '!=', 'closed'), ('config_id.wv_session_id', '=', self.id)]):
            if pos_session.user_id.id != self.env.user.id:
                notifications.append([pos_session.user_id.partner_id, "pos_sync_session",{'type':'product','data':order}])
        self.env['bus.bus']._sendmany(notifications)
        return 1

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create_from_ui(self, partner):
        partner_id = super(ResPartner, self).create_from_ui(partner)
        notifications = []
        for pos_session in self.env['pos.session'].search([('state', '!=', 'closed'), ('config_id.allow_incoming_orders', '=', True)]):
            params = pos_session._loader_params_res_partner()
            if self.env.uid != pos_session.user_id.id:
                allo_data = self.search_read([('id','=',partner_id)],params['search_params']['fields'])
                notifications.append([pos_session.user_id.partner_id, "pos_sync_session",{'type':'res_partner','data':allo_data}])
        if notifications:
            self.env['bus.bus']._sendmany(notifications)
        return partner_id

class pos_sync_order(models.Model):
    _name = "pos.sync.order"

    pos_order = fields.Text('Order')
    order_ref = fields.Char()
    sync_session_id = fields.Many2one('pos.sync.session', 'Sync session')


class PosSession(models.Model):
    _inherit = 'pos.session'

    def action_pos_session_close(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        res = super(PosSession, self).action_pos_session_close(balancing_account, amount_to_balance, bank_payment_method_diffs)
        for session in self:
            session.config_id.wv_session_id.order_ids.unlink()
        return res