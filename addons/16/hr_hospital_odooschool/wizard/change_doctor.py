from odoo import fields, models


class HrHospitalChangeDoctorWizard(models.TransientModel):
    _name = 'hr.hospital.change.doctor.wizard'
    _description = 'Change Doctor'

    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
    )
    patient_ids = fields.Many2many(
        comodel_name="hr.hospital.patient",
        required=True
    )

    def change_doctor(self):
        """
        Method for changing doctor for patient
        """
        self.ensure_one()
        doctor_id = self.doctor_id.id
        self.env["hr.hospital.patient"].search([('id', '=', self.id)]).write({
            'doctor_id': doctor_id
        })
