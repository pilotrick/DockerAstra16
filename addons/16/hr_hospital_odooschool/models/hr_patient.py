from datetime import datetime

from odoo import fields, models, api, _


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _inherit = 'hr.person.mixin'
    _description = _('Patient')

    birthday = fields.Date()
    age = fields.Integer(compute='_compute_age')
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Attending doctor", required=True
    )
    doctor_channing_ids = fields.One2many(
        comodel_name="hr.hospital.history.changing.doctor",
        inverse_name="patient_id",
        string="Changed doctors"
    )
    diagnosis_ids = fields.One2many(
        comodel_name="hr.hospital.diagnosis",
        inverse_name="patient_id",
        string="Diagnosis"
    )
    analysis_history = fields.One2many(
        comodel_name="hr.hospital.analysis.card",
        inverse_name="patient_id",
        string="Analysis history"
    )
    passport = fields.Char()
    contact_person = fields.Many2one(
        comodel_name="hr.hospital.contact.person",
    )
    active = fields.Boolean(default=True)

    @api.depends('birthday')
    def _compute_age(self) -> None:
        """ Compute patient age base on birthday field """
        for rec in self:
            today = datetime.today().date()
            birthday = rec.birthday or today
            diff = ((today.month, today.day) < (birthday.month, birthday.day))
            rec.age = today.year - birthday.year - diff

    @api.model
    def create(self, vals_list: dict) -> dict:
        """ Creates new records for the model """
        result = super(HrHospitalPatient, self).create(vals_list)
        if result:
            self._history_change(result)
        return result

    def write(self, vals: dict) -> bool:
        """ Updates all records in ``self`` with the provided values. """
        result = super().write(vals)
        if result:
            self._history_change()
        return result

    @api.model
    def _history_change(self, val=None) -> None:
        """
        Create new record in 'hr.hospital.history.changing.doctor' model
        when patient change attending doctor
        """
        patients = val or self
        for patient in patients:
            self.env["hr.hospital.history.changing.doctor"].create({
                'change_date': datetime.now(),
                'patient_id': patient.id,
                'doctor_id': patient.doctor_id.id,
            })

    def change_patient_doctor(self) -> dict:
        """
        Method change attending doctor for patient
        """
        patients_ids = []
        for rec in self:
            patients_ids.append(rec.id)
        return {"type": "ir.actions.act_window",
                "name": _("Change Doctor"),
                "res_model": "hr.hospital.change.doctor.wizard",
                "target": "new",
                "views": [[False, "form"]],
                "view_mode": "form",
                'context': {
                    'default_patient_ids': patients_ids,
                }}
