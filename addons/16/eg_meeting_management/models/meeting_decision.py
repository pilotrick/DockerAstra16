from odoo import fields, models, api


class MeetingDecision(models.Model):
    _name = "meeting.decision"
    _description = "Decisions"

    minute_id = fields.Many2one(comodel_name="minute.meeting", string="Minute")
    decision = fields.Char(string="Decision")
    note = fields.Char(string="Description / Notes")
    responsible_person_id = fields.Many2one(comodel_name="res.partner", string="Responsible")
    assigned_person_id = fields.Many2one(comodel_name="res.partner", string="Assigned To")
    deadline_date = fields.Date(string="Deadline")

