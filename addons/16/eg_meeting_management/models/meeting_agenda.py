from odoo import fields, models, api


class MeetingAgenda(models.Model):
    _name = "meeting.agenda"
    _description = "Agenda"

    minute_id = fields.Many2one(comodel_name="minute.meeting", string="Minute")
    topic = fields.Char(string="Topics")
    note = fields.Char(string="Description / Notes")
    discuss = fields.Boolean(string="Discussed")

