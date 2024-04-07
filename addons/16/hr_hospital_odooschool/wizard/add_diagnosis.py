from odoo import fields, models, api


class HrHospitalAddDiagnosisWizard(models.TransientModel):
    _name = 'hr.hospital.add.diagnosis.wizard'
    _description = 'Add Diagnosis'

    diagnosis_date = fields.Date()
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
    )
    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        required=True
    )
    disease_id = fields.Many2one(
        comodel_name="hr.hospital.disease.category",
        string="Disease",
        index=True,
    )
    analysis_id = fields.Many2one(
        comodel_name="hr.hospital.analysis.card"
    )
    treatment = fields.Text(required=True)
    mentor_comment = fields.Text()
    is_intern = fields.Boolean()
    visit_id = fields.Integer()

    def add_diagnosis(self):
        """
        Create diagnosis record
        """
        for rec in self:
            result = self.env["hr.hospital.diagnosis"].create({
                'disease_id': rec.disease_id.id,
                'analysis_id': rec.analysis_id.id,
                'patient_id': rec.patient_id.id,
                'doctor_id': rec.doctor_id.id,
                'diagnosis_date': rec.diagnosis_date,
                'treatment': rec.treatment,
                'mentor_comment': rec.mentor_comment,
            })
            if result:
                vals = {
                    "diagnosis_id": result.id,
                    # If True, visit state become -> 'done' automatically
                    'is_done': True  # optional
                }
                visit = self.env[
                    "hr.hospital.patient.visit"
                ].search([('id', '=', rec.visit_id)])
                visit.write(vals)

    @api.onchange('diagnosis_date')
    def _onchange_date(self):
        """
        Onchange method to change diagnosis date
        """
        for rec in self:
            date_now = fields.Datetime.now().date()
            if rec.diagnosis_date:
                if rec.diagnosis_date < date_now:
                    rec.diagnosis_date = False
