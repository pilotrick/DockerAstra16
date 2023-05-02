# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class payrolltype(models.Model):

    _name = 'hr.contract.payrolltype'
    _description = 'Payroll Type'
    _order = 'sequence, id'

    name = fields.Char(string='Payroll Type', required=True, translate=True)
    sequence = fields.Char(help="Create a New Payroll Type With '002'.", max=3)

    _sql_constraints = [
        ("unique_payrolltype_sequence", "UNIQUE(sequence)", _("This Payroll Type is already registered!"))
    ]

class HrContract(models.Model):
    """This Will add some information needed on the contract"""

    _inherit = "hr.contract"
    schedule_form_pay = fields.Selection(
        string='Schedule Pay',
        selection=[('monthly', 'Monthly'),
                   ('bi-monthly', 'Bi-monthly'),
                   ('weekly', 'Weekly')],
        required=True, readonly=False )
    

    deduction_plan = fields.Boolean(string="Monthly Deduction?")
    scheduled_retentions = fields.Selection([
        ("both_month", "Distribuidas"),
        ("start_month", "A inicio de Mes"),
        ("end_month", "Al Fin de Mes")],
        string="Retenciones De Ley",
    )
    is_foreign = fields.Boolean(string="Es Extranjero", default=False)
    identification_id = fields.Char(string='Identification No.', related="employee_id.identification_id")
    allow_accumulation = fields.Boolean(string="Permitir Acomulacion TSS, DGII?", default=True)
    retencion_unico = fields.Boolean(string="Labora en Otra Empresa?")
    rnc_retencion_unico = fields.Many2one("res.partner", string="RNC Agente De Retención Único")
    remuneracion = fields.Float(string="Remuneraciones En Otra Empresa")
    payment_day = fields.Float(string="Pagos por Dias", default=23.83)
    hourly_payment = fields.Boolean(string='Pago por hora')
    comission_rate = fields.Integer(string="% de comisión", help="Este porcentaje se calculará en base a todas las facturas pagadas en las que el empleado es vendedor.")
    wage_extra_hour = fields.Monetary(string="Pago horas extras")
    dieta_amount = fields.Monetary('Dieta', digits=(16, 2), help="Dieta de Empleado.")
    wage_extra_labol = fields.Monetary('Pago Horas Operario', digits=(16, 2))
    wage_holidays_hour = fields.Monetary(string="Pago horas Dias Feriados")
    fixed_loan = fields.Monetary(string="Cuota fija quincenal de préstamo")
    amount_saved = fields.Monetary(string="Cuota de ahorro quincenal")
    

    income_type = fields.Selection([
        ("0001", "Normal"),
        ("0002", "Trabajador Ocasional (No Fijo)"),
        ("0003", "Asalariado Por Hora o Labora Tiempo Parcial"),
        ("0004", "No laboró Mes Completo Por Razones Varias"),
        ("0005", "Salario Prorrateado Semanal/Bisemanal"),
        ("0006", "Pensionado Antes De La Ley 87-01"),
        ("0007", "Exento por Ley de pago al SDSS"),
        ("0008", "Trabajador con salario sectorizado")],
        string='Income Type', default='0001',
        help="Defines The Income Type as TSS",required=True)

    payrolltype_id = fields.Many2one('hr.contract.payrolltype', string="Payroll Type", required=True,
                              default=lambda self: self.env['hr.contract.payrolltype'].search([], limit=1))

    @api.constrains("rnc_retencion_unico", "remuneracion", "retencion_unico")
    def validate_external_partner(self):
        if self.retencion_unico:
            if self.remuneracion <= 0:
                raise ValidationError(_(
                    u"Remuneración Menor 0.00\n\n"
                    u"Favor Colocar el Monto De La Remuneracion de la "
                    u"Otra Empresa para la planilla de TSS"))

            if not self.rnc_retencion_unico.vat:
                raise ValidationError(_(
                    u"RNC Agente de Retención Único sin RNC/Céd\n\n"
                    u"*{}* no tiene RNC o Cédula y es requerido "
                    u"para la planilla de TSS")
                    .format(self.rnc_retencion_unico.name))








