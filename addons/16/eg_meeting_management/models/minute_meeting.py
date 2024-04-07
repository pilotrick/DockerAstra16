from odoo import fields, models, api


class MinuteMeeting(models.Model):
    _name = "minute.meeting"
    _description = "Minute Meeting"

    name = fields.Char(string="Name")
    description = fields.Html(string="description")
    meeting_members_ids = fields.Many2many("res.partner", "meeting_members_ref", "meeting_id", "partner_id", string="Meeting Members")
    responsible_person_id = fields.Many2one(comodel_name="res.partner", string="Responsible")
    note_taker_person_id = fields.Many2one(comodel_name="res.partner", string="Note Taker")
    absent_members_ids = fields.Many2many("res.partner", "absent_members_ref", "minute_id", "partner_id", string="Absent Members")
    agenda_line = fields.One2many(comodel_name="meeting.agenda", inverse_name="minute_id", string="Agenda")
    decision_line = fields.One2many(comodel_name="meeting.decision", inverse_name="minute_id", string="Decisions")
    conclusion_note = fields.Html(string="Conclusion Note")

