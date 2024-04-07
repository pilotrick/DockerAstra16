from datetime import datetime, time, timedelta

from odoo import fields, models, api
from odoo.addons.hr_hospital_odooschool import constants as const


class HrHospitalDoctorSchedule(models.Model):
    _name = 'hr.hospital.doctor.schedule'
    _description = 'Doctor Schedule'
    _order = "visit_date"

    visit_date = fields.Date(
        required=True,
        string="Work day"
    )
    day_week = fields.Char(
        string="Day of the week",
        compute="_compute_day_week",
    )
    shift_duration = fields.Selection(
        selection=const.WORK_SHIFT_DURATION,
        required=True,
        default="8"
    )
    start_time = fields.Datetime()
    shift_end_time = fields.Datetime(
        compute="_compute_shift_end_time",
        store=True
    )
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        ondelete="cascade",
        required=True
    )
    # TODO Add to calendar view.
    visit_ids = fields.One2many(
        comodel_name="hr.hospital.patient.visit",
        inverse_name="schedule_id"
    )

    @api.onchange('visit_date', 'start_time')
    @api.depends('visit_date', 'start_time')
    def _compute_day_week(self):
        # TODO re-write method
        """
        Compute dy of the week based on visit_date field
        """
        if self.visit_date:
            day_week = self.visit_date.strftime('%A')
            self.day_week = day_week.capitalize()
            if not self.start_time:
                start_time = datetime.combine(
                    self.visit_date, time(0, 0, 0)
                )
                self.start_time = start_time
            elif self.start_time:
                self.start_time = datetime.combine(
                    self.visit_date, self.start_time.time()
                )
        else:
            self.day_week = None

    def name_get(self) -> list:
        """ Build display name """
        return [
            (schedule.id, f"[{schedule.visit_date}, "
                          f"{schedule.doctor_id.name}]") for schedule in self
        ]

    @api.onchange('start_time', 'shift_duration')
    @api.depends('start_time', 'shift_duration')
    def _compute_shift_end_time(self):
        """
        Computing shift end time depends on
        shift duration and shift start
        """
        for rec in self:
            if rec.start_time and rec.shift_duration:
                shift_duration = int(rec.shift_duration)
                shift_end_delta = timedelta(
                    hours=shift_duration, minutes=00, seconds=00
                )
                rec.shift_end_time = rec.start_time + shift_end_delta
            else:
                rec.shift_end_time = None

    # TODO Add doctor new schedule checking method.
