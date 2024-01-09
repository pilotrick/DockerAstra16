# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TransferExcursion(models.Model):
    _name = 'transfer.excursion'
    _inherit = 'mail.thread'
    _description = 'Transfer and excursion details'
    _rec_name = 'tour_consultant_id'

    def _compute_balance(self):
        for rec in self:
            rec.balance_amount = rec.invoice_amount - rec.entrance_fee_used

    tour_consultant_id = fields.Many2one(
        comodel_name='res.partner', string='Tour Consultant',
        domain="[('tour_consultant', '=', True)]", tracking=True)
    driver_id = fields.Many2one(
        comodel_name='res.partner', string='Driver',
        help="Driver person for the service", domain="[('driver', '=', True)]",
        tracking=True)
    guide_id = fields.Many2one(
        comodel_name='res.partner', string='Guide',
        help='Guide person for the service', domain="[('guide', '=', True)]",
        tracking=True)
    service_id = fields.Many2one(
        comodel_name='booking.service', string='Service',
        help='Service for the transfer and excursion',
        tracking=True)
    invoice_number = fields.Char(
        string='Invoice Number', default='/', tracking=True)
    invoice_amount = fields.Float(
        string='Invoice Amount', digits=(16, 2), default=0.0,
        tracking=True)
    entrance_fee_given = fields.Float(
        string='Entrance Fee Given', digits=(16, 2), default=0.0,
        tracking=True)
    entrance_fee_used = fields.Float(
        string='Entrance Fee Used', digits=(16, 2), default=0.0,
        tracking=True)
    entrance_fee_to_return = fields.Float(
        string='Entrance Fee to be Return', digits=(16, 2), default=0.0,
        tracking=True)
    extra_paid = fields.Float(
        string='Extra Paid', digits=(16, 2), default=0.0,
        tracking=True)
    balance_amount = fields.Float(
        string='Balance Amount', digits=(16, 2), compute='_compute_balance')
    transfer_tour_payment = fields.Float(
        string='Transfer Tour Payment', digits=(16, 2), default=0.0,
        tracking=True)
