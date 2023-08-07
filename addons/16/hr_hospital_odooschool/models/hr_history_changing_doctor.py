from odoo import fields, models


class HrHospitalHistoryChangingDoctor(models.Model):
    _name = 'hr.hospital.history.changing.doctor'
    _description = 'History of changing the doctor'

    change_date = fields.Datetime()
    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        string="Patient", required=True,
        ondelete="cascade"
    )
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Attending doctor",
        required=True
    )

    def name_get(self) -> list:
        """ Build display name """
        return [
            (change.change_date, change.patient_id.name) for change in self
        ]
