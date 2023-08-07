from odoo import models, fields

from odoo.addons.hr_hospital_odooschool import constants as const


class HrHospitalContactPerson(models.Model):
    _name = 'hr.hospital.contact.person'
    _inherit = 'hr.person.mixin'
    _description = 'Patient contact person'

    sex = fields.Selection(
        selection=const.SEX_LIST, required=True,
        default="else"
    )
