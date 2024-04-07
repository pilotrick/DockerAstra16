# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields, api, tools, _
import pytz
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

LINE_STATE = {'Waiting': 1, 'Preparing': 2, 'Delivering': 3, 'Done': 4}


class PosOrder(models.Model):
    _inherit = "pos.order"

    order_state = fields.Selection(
        [("Start", "Start"), ("Done", "Done"), ("Deliver", "Deliver"), ("Complete", "Complete")], default="Start")
    line_cancel_reason_ids = fields.One2many('order.line.cancel.reason', 'pos_order_id', string="Line Cancel Reason")
    waiter_id = fields.Many2one('res.users', string="Waiter", readonly=True)
    cancel_order_reason = fields.Text('Cancel Reason', readonly=True)
    send_to_kitchen = fields.Boolean('Send To Kitchen', readonly=True)
    order_type = fields.Selection(
        [('take_away', 'Take Away'), ('dine_in', 'Dine In'), ('delivery', 'Delivery')], string="Order Type",
        readonly=True)
    delivery_service = fields.Many2one('delivery.type', string="Delivery Service", readonly=True)
    deliver_by = fields.Many2one('res.users', string="Delivery By", readonly=True)
    delivery_status = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'), ('done', 'Done')],
                                       default="draft")
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    delivery_time = fields.Char(string="Delivery Time")
    mobile = fields.Char(related="partner_id.mobile")
    city = fields.Char(related="partner_id.city")
    street = fields.Char(related="partner_id.street")
    street2 = fields.Char(related="partner_id.street2")
    zip = fields.Char(related="partner_id.zip")
    state_id = fields.Many2one(related="partner_id.state_id")
    country_id = fields.Many2one(related="partner_id.country_id")
    country_code = fields.Char(related="partner_id.country_code")

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['send_to_kitchen'] = ui_order.get('send_to_kitchen', False)
        order_fields['order_state'] = ui_order.get('order_state', False)
        order_fields['waiter_id'] = ui_order.get('waiter_id')
        order_fields['order_type'] = ui_order.get('orderType')
        order_fields['delivery_service'] = ui_order.get('deliveryService')
        order_fields['deliver_by'] = ui_order.get('deliveryBy')
        if ui_order.get('is_from_sync_screen') and ui_order.get('server_id'):
            order = self.browse(ui_order.get('server_id'))
            if order and order.table_id:
                order_fields.update({'table_id': order.table_id.id})
        return order_fields

    def action_pos_order_paid(self):
        res = super(PosOrder, self).action_pos_order_paid()
        if res:
            self.cancel_or_delete_pos_order(self.id, '', 'paid')
        return res

    def write(self, vals):
        res = super().write(vals)
        if self.order_state == 'Complete' and not self.env.context.get('reload_kanban'):
            user_obj = self.env['res.users'].search([('kitchen_screen_user', 'in', ['manager', 'waiter', 'delivery'])])
            user_list = [[user.partner_id, 'reload.kanban', {'render': True}] for user in user_obj]
            self.env['bus.bus']._sendmany(user_list)
        return res

    @api.model
    def cancel_or_delete_pos_order(self, order_id, cancel_reason, string):
        order_obj = self.browse(order_id)
        pos_reference = order_obj.pos_reference
        if string == 'cancel':
            order_obj.write({'state': 'cancel', 'cancel_order_reason': cancel_reason or ''})
        elif string == 'delete':
            order_obj.unlink()
        else:
            pass
        kitchen_user_ids = self.env['res.users'].search([('kitchen_screen_user', 'in', ['manager', 'waiter'])])
        notifications = []
        if kitchen_user_ids:
            for kitchen_user_id in kitchen_user_ids:
                notify_data = {'order_id': order_obj.id,
                               'remove_or_cancel': True,
                               'message': f"{pos_reference} [{string.upper()}]".format(pos_reference, string),
                               'is_remove': string}
                notifications.append([kitchen_user_id.partner_id, 'kitchen.order.remove', notify_data])
        if notifications:
            self.env['bus.bus']._sendmany(notifications)
        self.broadcast_order_data(False)
        return True

    def _get_fields_for_draft_order(self):
        res = super(PosOrder, self)._get_fields_for_draft_order()
        res.extend(['order_type', 'delivery_service', 'deliver_by', 'order_state', 'waiter_id', 'send_to_kitchen'])
        return res

    def _get_fields_for_order_line(self):
        res = super(PosOrder, self)._get_fields_for_order_line()
        if isinstance(res, list):
            res.append('state')
            res.append('line_cid')
        return res

    @api.model
    def _process_order(self, order, draft, existing_order):
        res = super(PosOrder, self)._process_order(order, draft, existing_order)
        if order['data']['send_to_kitchen'] or not order['data'].get('table_id'):
            self.broadcast_order_data(True)
        return res

    @api.model
    def cancel_pos_order(self, order_id, cancel_reason):
        order_obj = self.browse(order_id)
        order_obj.write({'state': 'cancel', 'cancel_order_reason': cancel_reason or ''})
        self.broadcast_order_data(False)
        return True

    @api.model
    def get_broadcast_data(self):
        pos_order = self.search([('amount_total', '>=', 0.00),
                                 ('send_to_kitchen', '=', True),
                                 ('state', '!=', 'cancel')])
        screen_table_data = []
        for order in pos_order:
            order_line_list = []
            flag = False
            for line in order.lines:
                if not flag and line.state == 'Waiting':
                    order.order_state = 'Start'
                    flag = True
                order_line = {
                    'id': line.id,
                    'order_id': order.id,
                    'line_cid': line.line_cid,
                    'name': line.product_id.display_name,
                    'full_product_name': line.full_product_name,
                    'note': line.note,
                    'qty': line.qty,
                    'state': line.state,
                    'categ_id': line.product_id.pos_categ_id.id,
                    'user': line.create_uid.id
                }
                order_line_list.append(order_line)
            order_dict = {
                'order_id': order.id,
                'order_name': order.name,
                'order_reference': order.pos_reference,
                'order_time': pytz.utc.localize(order.date_order).isoformat(),
                'table': order.table_id and order.table_id.name or False,
                'floor': order.table_id and order.table_id.floor_id.name or False,
                'customer': order.partner_id.name,
                'order_lines': order_line_list,
                'total': order.amount_total,
                'note': order.note,
                'state': order.state,
                'order_type': order.order_type,
                'user_id': order.user_id.id,
                'user_name': order.user_id.name,
                'guests': order.customer_count,
                'order_state': order.order_state
            }
            screen_table_data.append(order_dict)
        broadcast_data = screen_table_data
        return broadcast_data

    # def _is_pos_order_paid(self):
    #     return float_is_zero(self._get_rounded_amount(self.amount_total) - self.amount_paid, precision_rounding=self.currency_id.rounding)

    @api.model
    def broadcast_order_data(self, new_order):
        screen_table_data = self.get_broadcast_data()
        if not self.env.context.get('from_backend'):
            kitchen_user_ids = self.env['res.users'].search(
                [('kitchen_screen_user', 'in', ['cook', 'manager', 'waiter'])])
            notifications = []
            if kitchen_user_ids:
                for kitchen_user_id in kitchen_user_ids:
                    notify_data = {
                        'order_data': screen_table_data,
                        'new_order': new_order,
                        'manager': False if kitchen_user_id.kitchen_screen_user == 'cook' else True
                    }
                    notifications.append([kitchen_user_id.partner_id, 'kitchen.order', notify_data])
            if notifications:
                self.env['bus.bus']._sendmany(notifications)

    def change_state(self, state):
        if state == 'in_progress':
            self.sudo().with_context({'reload_kanban': True}).write(
                {'delivery_status': state, 'start_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            self.sudo()._create_order_picking()
        elif state == 'done':
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            difference = (current_time - self.start_date).total_seconds()
            self.sudo().with_context({'reload_kanban': True}).write(
                {'delivery_status': state,
                 'end_date': end_time,
                 'delivery_time': f"{int(difference / 60)} Minutes."})
            self.picking_ids.sudo().picking_done()
            self.picking_ids.sudo().write({'origin': self.name})
        user_ids = self.env['res.users'].search([])
        notifications = []
        if user_ids:
            for kitchen_user_id in user_ids:
                notify_data = {'order_id': self.id,
                               'state': self.delivery_status,
                               }
                notifications.append([kitchen_user_id.partner_id, 'state.update', notify_data])
        if notifications:
            self.env['bus.bus']._sendmany(notifications)
        return True

    def _create_order_picking(self):
        self.ensure_one()
        if self.order_type == 'delivery':
            if self.delivery_status == 'in_progress':
                if self.to_ship:
                    self.lines._launch_stock_rule_from_pos_order_lines()
                if self._should_create_picking_real_time():
                    picking_type = self.config_id.picking_type_id
                    if self.partner_id.property_stock_customer:
                        destination_id = self.partner_id.property_stock_customer.id
                    elif not picking_type or not picking_type.default_location_dest_id:
                        destination_id = self.env['stock.warehouse']._get_partner_locations()[0].id
                    else:
                        destination_id = picking_type.default_location_dest_id.id

                    pickings = self.env['stock.picking']._create_custom_picking_from_pos_order_lines(destination_id,
                                                                                                     self.lines,
                                                                                                     picking_type,
                                                                                                     self.partner_id,
                                                                                                     self)
                    if pickings:
                        pickings.sudo().write(
                            {'pos_session_id': self.session_id.id, 'pos_order_id': self.id, 'origin': self.name})
            else:
                pass
        else:
            return super(PosOrder, self)._create_order_picking()


class PosOrderLines(models.Model):
    _inherit = "pos.order.line"

    state = fields.Selection(
        selection=[("Waiting", "Waiting"), ("Preparing", "Preparing"), ("Delivering", "Delivering"),
                   ("Done", "Done")], default="Waiting")
    line_cid = fields.Char('Line cid')

    def remove_order_line(self, vals):
        if self:
            self.order_id.write({'line_cancel_reason_ids': [(0, 0, {
                                   'pos_order_id': self.order_id.id,
                                   'product_id': vals.get('product_id'),
                                   'reason': vals.get('reason_id'),
                                   'description': vals.get('description'),
                               })],
                           })
            self.unlink()
            self.env['pos.order'].broadcast_order_data(False)
        return True

    def _export_for_ui(self, orderline):
        res = super(PosOrderLines, self)._export_for_ui(orderline)
        res.update({'state': orderline.state,
                    'line_cid': orderline.line_cid})
        return res

    @api.model
    def update_orderline_state(self, vals):
        order_line = self.browse(vals['order_line_id'])
        order = self.env['pos.order'].browse(vals['order_id'])
        if LINE_STATE[vals['state']] >= LINE_STATE[order_line.state]:
            order_line.sudo().write({'state': vals['state']})
            state_list = [line.state for line in order.lines]
            if 'Waiting' in state_list:
                order_state = 'Start'
            elif 'Preparing' in state_list:
                order_state = 'Done'
            else:
                order_state = 'Deliver'
            order.sudo().write({'order_state': order_state})
            if order.order_state == 'Deliver':
                order.sudo().write({'order_state': 'Complete'})
            self.env['pos.order'].broadcast_order_data(False)
        return True

    @api.model
    def update_all_orderline_state(self, vals):
        order = self.env['pos.order'].browse(vals['order_id'])
        order.sudo().write({'order_state': vals['order_state']})
        if not vals.get('line_state'):
            vals['line_state'] = 'Done'
        for line in order.lines:
            if line.state and LINE_STATE[vals['line_state']] >= LINE_STATE[line.state]:
                line.sudo().write({'state': vals['line_state']})
        self.env['pos.order'].broadcast_order_data(False)
        return True


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _create_custom_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False,
                                                    order=False):
        """We'll create some picking based on order_lines"""
        pickings = self.env['stock.picking']
        stockable_lines = lines.filtered(
            lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty,
                                                                                      precision_rounding=l.product_id.uom_id.rounding))
        if not stockable_lines:
            return pickings
        positive_lines = stockable_lines.filtered(lambda l: l.qty > 0)
        negative_lines = stockable_lines - positive_lines

        if positive_lines:
            location_id = picking_type.default_location_src_id.id
            if not order.picking_ids:
                positive_picking = self.env['stock.picking'].create(
                    self._prepare_picking_vals(partner, picking_type, location_id, location_dest_id)
                )
                positive_picking._create_move_from_pos_order_lines(positive_lines)
                return positive_picking
        return pickings

    def picking_done(self):
        try:
            with self.env.cr.savepoint():
                self._action_done()
        except (UserError, ValidationError):
            pass


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(IrUiMenu, self)._visible_menu_ids(debug)
        user_role = self.env.user and self.env.user.kitchen_screen_user
        if user_role == 'delivery':
            root = self.env.ref('point_of_sale.menu_point_root')
            parent = self.env.ref('point_of_sale.menu_point_of_sale')
            delivery_menu = self.env.ref('aspl_pos_kitchen_screen.delivery_orders_menu_id')
            return {root.id, parent.id, delivery_menu.id}
        elif user_role == 'cook':
            return {}
        return menus


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    def check(self):
        res = super().check()
        user_obj = self.env['res.users'].search([('kitchen_screen_user', 'in', ['manager', 'waiter'])])
        user_list = [[user.partner_id, 'remove.pos.order', {'server_id': self.env.context.get('active_id', False)}] for user in user_obj]
        self.env['bus.bus']._sendmany(user_list)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
