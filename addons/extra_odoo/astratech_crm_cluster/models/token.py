# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import os
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import hashlib
from datetime import datetime as dt
import uuid
import random


class DGIIFile(models.Model):
    _name = 'token.register'
    _description = 'Token Registres'

    name = fields.Char(String="Nombre", required=True)
    bot = fields.Char(String="Bot", required=True)
    token = fields.Char(String="Token", readonly=True)

    def generate_token(self):
        random_data = os.urandom(100)
        hash_gen = hashlib.new('sha512')
        hash_gen.update(random_data)
        self.token = hash_gen.hexdigest()[:45]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pregnancy = fields.Boolean(
        string='Embarazada?',
    )

    height = fields.Float(
        string='Altura',
    )

    weight = fields.Float(
        string='Pesos',
    )

    bariatric = fields.Boolean(
        string='Bariatica ?',
    )

    diseases = fields.Html(
        string='Enfermedades',
    )
    
    birthday = fields.Char(
        string='Fecha de Nacimiemto',
    )
    
    IMC = fields.Char(
        string='IMC',
    )
    
    appliesTo = fields.Char(
        string='appliesTo',
    )

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    pregnancy = fields.Boolean(
        related='partner_id.pregnancy', readonly=True
    )

    height = fields.Float(
        related='partner_id.height', readonly=True
    )

    weight = fields.Float(
        related='partner_id.weight', readonly=True
    )

    bariatric = fields.Boolean(
        related='partner_id.bariatric', readonly=True
    )

    diseases = fields.Html(
        related='partner_id.diseases', readonly=True
    )
    
    birthday = fields.Char(
        related='partner_id.birthday', readonly=True
    )
    
    IMC = fields.Char(
        related='partner_id.IMC', readonly=True
    )
    
    appliesTo = fields.Char(
        related='partner_id.appliesTo', readonly=True
    )
