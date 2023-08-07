from datetime import timedelta, datetime, time

from odoo import fields, models, api
from odoo.addons.hr_hospital_odooschool import constants as const


class HrHospitalWeekScheduleWizard(models.TransientModel):
    _name = 'hr.hospital.week.schedule.wizard'
    _description = 'Create Week Schedule'

    week_start_date = fields.Date(required=True)
    work_day_start = fields.Datetime(required=True)
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        required=True,
        ondelete="cascade"
    )
    shift_duration = fields.Selection(
        selection=const.WORK_SHIFT_DURATION,
        required=True,
        default="8"
    )
    is_even_or_odd = fields.Selection(
        selection=[("even", "Even"), ("odd", "Odd")],
        string="Even or Odd",
        help="For even or odd days"
    )

    def add_schedule(self):
        """
        Create one week schedule for specified doctor
        """
        self.ensure_one()
        week_start_date = fields.Date.to_date(self.week_start_date)
        delta = timedelta(days=1)
        params = {
            "doctor_id": self.doctor_id.id,
            "shift_duration": self.shift_duration
        }
        if self.is_even_or_odd == 'even':
            for _ in range(0, 7):
                if week_start_date.day % 2 == 0:
                    params["visit_date"] = week_start_date
                    params["start_time"] = week_start_date
                    params["day_week"] = week_start_date.strftime('%A')
                    self._create_schedule(params)
                week_start_date += delta
        elif self.is_even_or_odd == 'odd':
            for _ in range(0, 7):
                if week_start_date.day % 2 != 0:
                    params["visit_date"] = week_start_date
                    params["start_time"] = week_start_date
                    params["day_week"] = week_start_date.strftime('%A')
                    self._create_schedule(params)
                week_start_date += delta
        else:
            for _ in range(0, 7):
                params["visit_date"] = week_start_date
                params["start_time"] = week_start_date
                params["day_week"] = week_start_date.strftime('%A')
                self._create_schedule(params)
                week_start_date += delta

    def _create_schedule(self, params: dict):
        """
        Create one week schedule for specified doctor
        """
        self.env['hr.hospital.doctor.schedule'].create({
            "visit_date": params["visit_date"],
            "day_week": params["day_week"],
            "start_time": params['start_time'],
            "doctor_id": params['doctor_id'],
        })

    @api.onchange('week_start_date', 'work_day_start')
    @api.depends('week_start_date', 'work_day_start')
    def _work_day_start(self):
        """
        Set work day start depends on week_start_date
        and work_day_start fields
        """
        if not self.work_day_start and self.week_start_date:
            start_time = datetime.combine(
                self.week_start_date, time(0, 0, 0)
            )
            self.work_day_start = start_time
        elif self.work_day_start and self.week_start_date:
            self.work_day_start = datetime.combine(
                self.week_start_date, self.work_day_start.time()
            )
        else:
            self.work_day_start = None

    # TODO Add doctor schedule checking
