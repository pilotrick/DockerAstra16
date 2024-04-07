from odoo import fields, models


class HrHospitalDiagnosis(models.Model):
    _name = 'hr.hospital.diagnosis'
    _description = 'HrHospitalDiagnosis'
    _order = "diagnosis_date"

    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        required=True
    )
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
    )
    disease_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Disease"
    )
    analysis_id = fields.Many2one(
        comodel_name="hr.hospital.analysis.card"
    )
    diagnosis_date = fields.Date()
    treatment = fields.Text()
    mentor_comment = fields.Text()
    is_intern = fields.Boolean(compute="_compute_is_intern")

    def _compute_is_intern(self) -> None:
        """ Compute is doctor intern or not """
        for rec in self:
            rec.is_intern = rec.doctor_id.is_intern

    def name_get(self) -> list:
        """ Build display name """
        return [
            (diagnosis.id, diagnosis.diagnosis_date) for diagnosis in self
        ]
