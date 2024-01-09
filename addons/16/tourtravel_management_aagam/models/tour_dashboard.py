# from odoo import models, fields, api
# from odoo.http import request
# from datetime import datetime
#
# class tour_group(models.Model):
#     _name = 'tour.group'

    # name = fields.Char(string='Group Name')
    # appointment_charge = fields.Float(string='Appointment Charge', required=True)
    # product_template_id = fields.Many2one('product.template', string='Group Product')
    # appointment_group_ids = fields.Many2many('res.partner')
    # country_id = fields.Many2one('res.country', string='Country',required=True)
    # state_id = fields.Many2one('res.country.state', string='State',required=True)

    # @api.model
    # def get_count_list(self):
    #     print(">>>>>>>>")
    #     total_service = self.env['appointment.group'].sudo().search_count([])
    #     total_appointment = request.env['calendar.event'].sudo().search_count([])
    #     pending_appointment = request.env['calendar.event'].sudo().search_count([('attendee_ids.state','=','needsAction')])
    #     approved_appointment = request.env['calendar.event'].sudo().search_count([('attendee_ids.state','=','accepted')])
    #     rejected_appointment = request.env['calendar.event'].sudo().search_count([('attendee_ids.state','=','declined')])
    #     today_appointment = request.env['calendar.event'].sudo().search_count([('start_at','=', fields.Date.today())])
    #     return {
    #         'total_service':total_service,
    #         'total_appointment':total_appointment,
    #         'pending_appointment':pending_appointment,
    #         'approved_appointment':approved_appointment,
    #         'rejected_appointment':rejected_appointment,
    #         'today_appointment':today_appointment,
    #     }
