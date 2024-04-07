# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrEmployeeEmergencyContact(models.Model):
    """adding emergency contact table"""

    _name = "hr.employee.emergency_contact"
    _description = "HR Emergency Contact"

    name = fields.Char(string="Name", required=True)
    number = fields.Char(string="Number", required=True)
    employee_id = fields.Many2one('hr.employee', invisible=1)


class HrEmployeeFamily(models.Model):
    """Employee family information"""

    _name = "hr.employee.family"
    _description = "HR Employee Family"

    family_name = fields.Char(string="Name", required=True)
    birthdate = fields.Date(string="Fecha de Nacimiento", required=False, )
    cedula = fields.Char(string="Cedula", required=False, )
    relation = fields.Selection(
        [
            ("father", "Father"),
            ("mother", "Mother"),
            ("daughter", "Daughter"),
            ("son", "Son"),
            ("wife", "Wife"),
            ("husband", "Husband"),
        ],
        string="Relation",
        required=True,
    )
    is_capita = fields.Boolean(string="Retenter Per Cápita?")
    amount_capita = fields.Float(string="Monto")
    family_contact = fields.Char(string="Contact No")
    employee_id = fields.Many2one(
        string="Employee",
        help="Select corresponding Employee",
        comodel_name="hr.employee",
        invisible=False,
    )



class HrEmployee(models.Model):
    _inherit = "hr.employee"

    emergency_contacts = fields.One2many(
        "hr.employee.emergency_contact", "employee_id", string="Emergency Contact",
        invisible=False,
    )
    family_ids = fields.One2many(
        "hr.employee.family", "employee_id", string="Family")
    social_security_number = fields.Char(string="Nº Seguro Social")

    identification_id = fields.Char(string='Identification No',copy=False, required=True)

    is_dominica = fields.Boolean(string="Dominican", compute="_compute_is_dominica_person")
    _sql_constraints = [
        ('identification_id_uniq', 'unique(identification_id)',
         'The employee identification number must be unique across the company(s).'),
    ]

    #TSS INFO
    tss_names = fields.Char(string='Nombres',copy=False, required=True)
    tss_first_lastname = fields.Char(string='Primer Apellido',copy=False, required=True)
    tss_second_lastname = fields.Char(string='Segundo Apellido',copy=False)

    loan_ids = fields.One2many(comodel_name='hr.employee.loan', inverse_name='employee_id',
                               string=u"Préstamos")

    @api.model
    def create(self, vals):
        if not vals.get('identification_id'):
            vals['identification_id'] = self.generate_identification_id()
        return super(HrEmployee, self).create(vals)


    @api.depends('country_id')
    def _compute_is_dominica_person(self):
        do = self.env.ref('base.do').id
        self.is_dominica =  self.country_id.id == do
        
    def get_approved_loans(self):
        return self.loan_ids.filtered(lambda loan: loan.state == 'approved')
