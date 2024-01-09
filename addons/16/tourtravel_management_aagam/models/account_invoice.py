# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.move"

    agent_id = fields.Many2one(
        comodel_name='res.partner', string='Tour agent',
        domain="[('s_agent', '=', 'parent')]", tracking=True)
    client_name = fields.Char(
        string='Client name', tracking=True)
    agent_reference = fields.Char(
        string='Agent reference', tracking=True)
    addition_info = fields.Text(
        string='Additional Information', tracking=True)
    tour_reservation_id = fields.Many2one(
        comodel_name='tour.reservation', string='Tour Reservation',
        help='Tour reservation for the created invoice',
        tracking=True)
    payment_method = fields.Char(string='Payment Method')
    bank_detail = fields.Char(string='Bank Detail')


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    service_datetime = fields.Datetime(
        string='Service datetime', help='Service Datetime',
        tracking=True)
    person_cost_id = fields.Many2one(
        comodel_name='persontype.cost', string='Person Cost',
        tracking=True)
