from odoo import fields, models, _
from odoo.addons.hr_hospital_odooschool import constants as const


class HrPerson(models.AbstractModel):
    _name = 'hr.person.mixin'
    _description = _('HrPerson mixin')

    name = fields.Char(required=True)
    phone = fields.Char()
    email = fields.Char()
    img = fields.Image(max_width=128, max_height=128)
    sex = fields.Selection(
        selection=const.SEX_LIST, required=True
    )
