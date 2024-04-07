from odoo import fields, models


class HrHospitalChangeVisitTimeWizard(models.TransientModel):
    _name = 'hr.hospital.change.visit.time.wizard'
    _description = 'Change Visit Time'

    visit_date = fields.Datetime(help="Choose date and time")
    old_time = fields.Datetime()

    def change_visit_time(self):
        self.ensure_one()
        new_visit_time = self.visit_date
        self.env["hr.hospital.patient.visit"].browse(self.id).write({
            'visit_date': new_visit_time,
            'active': True
        })
