# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class TaskDescription(models.Model):
    _name = 'task.description'
    _inherit = 'mail.thread'
    _description = 'task assigned details'

    @api.depends('order_line_ids', 'order_line_ids.order_id.state')
    def _compute_ordered(self):
        for rec in self:
            if rec.order_line_ids and any(
                    s != 'cancel' for s in rec.order_line_ids.mapped(
                        'order_id.state')):
                rec.ordered = True

    name = fields.Char(
        string='Task assigned description', required="1",
        tracking=True)
    cost = fields.Float(
        string='Cost', digits=(16, 2), tracking=True)
    ordered = fields.Boolean(
        string='Ordered', compute='_compute_ordered', store=True)
    order_line_ids = fields.One2many(
        comodel_name='sale.order.line', inverse_name='task_assigned_id',
        string='Order Line')


class JobEquipment(models.Model):
    _name = 'job.equipment'
    _inherit = 'mail.thread'
    _description = 'Job equipment details'

    name = fields.Char(
        string='Equipment', required="1", tracking=True)
    sequence = fields.Integer(string='S. No', tracking=True)
    qty = fields.Float(
        string='Qty', digits=(16, 2), tracking=True)


class JobCard(models.Model):
    _name = 'job.card'
    _inherit = 'mail.thread'
    _description = 'Job Card'
    _rec_name = 'jobcard_number'

    def _get_ordered(self):
        for jc in self:
            orders = self.env['sale.order'].search([
                ('job_card_id', '=', jc.id), ])
            qty_ordered = len(jc.task_description_ids.filtered(
                lambda j: j.ordered))
            total_qty = len(jc.task_description_ids)
            qty_to_order = total_qty - qty_ordered
            jc.update({'order_count': len(orders),
                       'order_ids': orders.ids,
                       'qty_to_order': qty_to_order})

    customer_id = fields.Many2one(
        comodel_name='res.partner', string='Customer',
        tracking=True, required="True")
    customer_email = fields.Char(
        string='Customer Email', tracking=True)
    customer_phone = fields.Char(
        string='Customer Phone', tracking=True)
    assign_to_id = fields.Many2one(
        comodel_name='res.partner', string='Assign To',
        tracking=True)
    jobcard_number = fields.Char(
        string='Jobcard Number', default='/', tracking=True)
    jobcard_subject = fields.Char(
        string='Jobcard Subject', tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'), ('in_progress', 'In Progress'),
            ('done', 'Done'), ('cancel', 'Cancel')
        ], string='Jobcard Status', help='Status of the job card',
        default='draft', tracking=True)
    start_date = fields.Date(
        string='Start Date', help='Start date of job card',
        tracking=True)
    end_date = fields.Date(
        string='End Date', help='End date of job card',
        tracking=True)
    notes = fields.Text(
        string='Notes/Comments', help='Notes and comments for the job card',
        tracking=True)
    # Task Assigned Description
    task_description_ids = fields.Many2many(
        comodel_name='task.description', string='Task Assigned Description',
        tracking=True)
    task_done_description = fields.Text(
        string='Task Done Description', tracking=True)
    # Equipment Installed
    equipment_installed_ids = fields.Many2many(
        'job.equipment', 'job_equipment_installed', 'job_id',
        'equip_id', string='Equipment Installed',
        tracking=True)
    # Equipment Returned
    equipment_returned_ids = fields.Many2many(
        'job.equipment', 'job_equipment_returned', 'job_id',
        'equip_id', string='Equipment Returned',
        tracking=True)
    technician_name = fields.Char(string='Name', tracking=True)
    technician_sign_date = fields.Date(
        string='Date', help='Date when technician added signature',
        tracking=True)
    customer_representative_name = fields.Char(
        string='Name', tracking=True)
    c_sign_date = fields.Date(
        string='Date', help='Date when technician added signature',
        tracking=True)
    order_ids = fields.Many2many(
        "sale.order", string='Orders', compute="_get_ordered",
        readonly=True, copy=False)
    order_count = fields.Integer(
        string='# of Orders', compute='_get_ordered', readonly=True)
    qty_to_order = fields.Float(
        string='Qty to Order', compute='_get_ordered', readonly=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        tracking=True, required=True,
        default=lambda self: self.env.user.company_id.currency_id)

    @api.model
    def create(self, values):
        values['jobcard_number'] = self.env['ir.sequence'].next_by_code(
            'job.card.seq') or '/'
        return super(JobCard, self).create(values)

    def action_approve(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_order(self):
        order_obj = self.env['sale.order']
        order_line_obj = self.env['sale.order.line']

        if not self.task_description_ids:
            raise UserError(_("There is no Task included.\
                Please include at least one task to create sale order."))

        order_values = {
            'name': self.jobcard_number,
            'origin': self.jobcard_number,
            'partner_id': self.assign_to_id.id,
            'date_order': fields.Date.today(),
            'job_card_id': self.id,
            'currency_id': self.currency_id.id,
        }
        config_parameter = self.env['ir.config_parameter'].sudo()
        default_task_assigned_product = config_parameter.get_param(
            'jobcard.default_task_assigned_product')
        order_ids = []
        new_order = False
        if self.task_description_ids and len(
                self.task_description_ids) > len(
                    self.task_description_ids.filtered(lambda t: t.ordered)):
            new_order = order_obj.with_context(
                mail_create_nosubscribe=True).create(order_values)
            order_ids.append(new_order.id)
            for task in self.task_description_ids.filtered(
                    lambda t: not t.ordered):
                new_line_values = {
                    'name': task.name,
                    'order_id': new_order.id,
                    'product_id': int(default_task_assigned_product),
                    'price_unit': task.cost,
                    'product_uom_qty': 1.0,
                    'task_assigned_id': task.id
                }
                order_line_obj.create(new_line_values)
            action = self.env.ref('sale.action_quotations').read()[0]
            action['domain'] = [('id', 'in', order_ids)]
            return action
        else:
            raise UserError(
                _("Nothing to order:\nAll Task are already ordered."))

    def action_view_order(self):
        orders = self.mapped('order_ids')
        action = self.env.ref('sale.action_quotations').read()[0]
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            action['views'] = [
                (self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
