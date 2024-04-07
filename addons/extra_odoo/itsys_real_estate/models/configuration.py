# -*- coding: utf-8 -*-
from odoo import api, fields, models

class real_estate_setings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    reservation_hours= fields.Integer(string='Hours to release units reservation',
                                              config_parameter='itsys_real_estate.reservation_hours')

    penalty_percent= fields.Integer ('Penalty Percentage')
    penalty_account= fields.Many2one('account.account',
                                             'Late Payments Penalty Account',
                                             config_parameter='itsys_real_estate.penalty_account')
    discount_account= fields.Many2one('account.account',
                                              'Discount Account',
                                              config_parameter='itsys_real_estate.discount_account')
    income_account= fields.Many2one('account.account',
                                            'Income Account',
                                            config_parameter='itsys_real_estate.income_account')
    me_account= fields.Many2one('account.account',
                                        'Managerial Expenses Account',
                                        config_parameter='itsys_real_estate.me_account')
    analytic_account= fields.Many2one('account.analytic.account',
                                              'Analytic Account',
                                              config_parameter='itsys_real_estate.analytic_account')
    security_deposit_account= fields.Many2one('account.account',
                                                      'Security Deposit Account',
                                                      config_parameter='itsys_real_estate.security_deposit_account')

    revenue_account= fields.Many2one('account.account',
                                                      'Revenue Account',
                                                      config_parameter='itsys_real_estate.revenue_account')

    income_journal = fields.Many2one('account.journal','Income Journal',config_parameter='itsys_real_estate.income_journal')
    maintenance_journal = fields.Many2one('account.journal','وديعة صيانة',config_parameter='itsys_real_estate.maintenance_journal')
    club_journal = fields.Many2one('account.journal','تصرفات عقارية',config_parameter='itsys_real_estate.club_journal')
    garage_journal = fields.Many2one('account.journal','تشطبات',config_parameter='itsys_real_estate.garage_journal')
    elevator_journal = fields.Many2one('account.journal','تآمين آعمال',config_parameter='itsys_real_estate.elevator_journal')
    other_journal = fields.Many2one('account.journal','مرافق',config_parameter='itsys_real_estate.other_journal')
    brokers_account_id = fields.Many2one(comodel_name='account.account',string=' وسطاء',config_parameter='itsys_real_estate.brokers_account_id')
    relations_account_id = fields.Many2one(comodel_name='account.account',string=' علاقات',config_parameter='itsys_real_estate.relations_account_id')
    comp_account_id = fields.Many2one(comodel_name='account.account',string=' شركة',config_parameter='itsys_real_estate.comp_account_id')

    

class Config(models.TransientModel):
    _name = 'gmap.config'

    @api.model
    def get_key_api(self):
        return self.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')