from odoo import fields, models
from odoo.exceptions import UserError


class HrHospitalCreateAppointmentWizard(models.TransientModel):
    _name = 'hr.hospital.create.appointment.wizard'
    _description = 'Create New Appointment'

    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        required=True
    )
    doctor_id = fields.Many2one(
        related='patient_id.doctor_id',
        readonly=True, required=True
    )
    visit_date = fields.Datetime(
        required=True,
        string="Visit date and time"
    )

    def create_appointment(self):
        """
        Quick create visit
        :raise UserError: If appointment created in the past
        """
        self.ensure_one()
        for rec in self:
            if rec.visit_date.date() >= fields.Datetime.now().date():
                self.env["hr.hospital.patient.visit"].create({
                    'patient_id': rec.patient_id.id,
                    'doctor_id': rec.doctor_id.id,
                    'visit_date': rec.visit_date,
                })
            else:
                raise UserError(
                    f"You can't create appointment in the past!!!"
                    f"You choose - {rec.visit_date.date()}"
                    f"Choose another date!!!"
                )
