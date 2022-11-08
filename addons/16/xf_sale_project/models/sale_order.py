# -*- coding: utf-8 -*-
from odoo import api, Command, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Fields
    use_sale_project = fields.Selection(
        string='Use Sale Project',
        related='company_id.use_sale_project',
        readonly=True,
    )
    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
        ondelete='restrict',
    )

    analytic_account_id = fields.Many2one(
        related='project_id.analytic_account_id')

    @api.depends('order_line.product_id.project_id', 'order_line.project_id')
    def _compute_tasks_ids(self):
        for order in self:
            order.tasks_ids = self.env['project.task'].search(['&', ('display_project_id', '!=', 'False'), '|', (
                'sale_line_id', 'in', order.order_line.ids), ('sale_order_id', '=', order.id)])
            order.tasks_count = len(order.tasks_ids)

    @api.depends('order_line.product_id', 'order_line.project_id')
    def _compute_project_ids(self):
        for order in self:
            if order.project_id:
                projects = order.order_line.mapped('project_id')
            else:
                projects = order.order_line.mapped('product_id.project_id')
                projects |= order.order_line.mapped('project_id')
                projects |= order.project_id
            order.project_ids = projects
            order.project_count = len(projects)

    def action_apply_project(self):
        self.apply_project()

    # Business methods
    
    def apply_project(self):
        for order in self:
            if not order.project_id:
                continue
            so_vals = order.project_id._prepare_sale_order()
            order.write(so_vals)
            order.apply_project_product_lines()

    def apply_project_product_lines(self):
        for order in self:
            if not order.project_id:
                continue
            lines = self.env['sale.order.line']
            for line in order.project_id.product_line_ids:
                so_line_vals = line._prepare_sale_order_line(order)
                so_line = lines.new(so_line_vals)
                lines |= so_line
            order.order_line = lines

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.project_id:
            invoice_vals['project_id'] = self.project_id.id
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    project_id = fields.Many2one(related='order_id.project_id',  index=True)
    analytic_line_ids = fields.One2many(
        'account.analytic.line', 'so_line', string="Analytic lines")

    @api.depends('analytic_line_ids.project_id', 'project_id.pricing_type', 'order_id.project_id')
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()

        lines_by_timesheet = self.filtered(
            lambda sol: sol.qty_delivered_method == 'timesheet')

        domain = lines_by_timesheet._timesheet_compute_delivered_quantity_domain()
        mapping = lines_by_timesheet.sudo()._get_delivered_quantity_by_analytic(domain)

        for line in lines_by_timesheet:
            line.qty_delivered = mapping.get(line.id or line._origin.id, 0.0)

    def _timesheet_compute_delivered_quantity_domain(self):
        """ Hook for validated timesheet in addionnal module """
        domain = [('project_id', '!=', False)]
        if self._context.get('accrual_entry_date'):
            domain += [('date', '<=', self._context['accrual_entry_date'])]
        return domain

    def _timesheet_create_project_prepare_values(self):
        """Generate project values"""

        account = self.order_id.analytic_account_id
        if not account:
            self.order_id._create_analytic_account(
                prefix=self.product_id.default_code or None)
            account = self.order_id.analytic_account_id
        # create the project or duplicate one
        return {
            'name': '%s - %s' % (self.order_id.client_order_ref, self.order_id.name) if self.order_id.client_order_ref else self.order_id.name,
            'analytic_account_id': account.id,
            'partner_id': self.order_id.partner_id.id,
            'sale_line_id': self.id,
            'sale_order_id': self.order_id,
            'active': True,
            'company_id': self.company_id.id,
        }

    def _timesheet_create_project(self):
        """ Generate project for the given so line, and link it.
            :param project: record of project.project in which the task should be created
            :return task: record of the created task
        """
        self.ensure_one()
        values = self._timesheet_create_project_prepare_values()
        if not self.order_id.project_id:
            if self.product_id.project_template_id:
                values['name'] = "%s - %s" % (values['name'],
                                              self.product_id.project_template_id.name)
                project = self.product_id.project_template_id.copy(values)

                project.tasks.write({
                    'sale_line_id': self.id,
                    'partner_id': self.order_id.partner_id.id,
                    'email_from': self.order_id.partner_id.email,
                })
                # duplicating a project doesn't set the SO on sub-tasks
                project.tasks.filtered(lambda task: task.parent_id != False).write({
                    'sale_line_id': self.id,
                    'sale_order_id': self.order_id,
                })
        else:
            project = self.env['project.project'].create(values)

        # Avoid new tasks to go to 'Undefined Stage'
        if not project.type_ids:
            project.type_ids = self.env['project.task.type'].create(
                {'name': _('New')})

        # link project as generated by current so line
        self.write({'project_id': project.id})
        return project

    def _timesheet_create_task_prepare_values(self, project):
        self.ensure_one()
        planned_hours = self._convert_qty_company_hours(self.company_id)
        sale_line_name_parts = self.name.split('\n')
        title = sale_line_name_parts[0] or self.product_id.name
        description = '<br/>'.join(sale_line_name_parts[1:])

        return {
            'name': title if project.sale_line_id else '%s: %s' % (self.order_id.name or '', title),
            'planned_hours': planned_hours,
            'partner_id': self.order_id.partner_id.id,
            'email_from': self.order_id.partner_id.email,
            'description': description,
            'project_id': project.id,
            'sale_line_id': self.id,
            'sale_order_id': self.order_id.id,
            'company_id': project.company_id.id,
            'user_ids': False,  # force non assigned task, as created as sudo()
        }

    def _timesheet_create_task(self, project):
        """ Generate task for the given so line, and link it.
            :param project: record of project.project in which the task should be created
            :return task: record of the created task
        """
        values = self._timesheet_create_task_prepare_values(project)
        task = self.env['project.task'].sudo().create(values)

        self.write({'task_id': task.id})
        # post message on task
        task_msg = _("This task has been created from: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a> (%s)") % (
            self.order_id.id, self.order_id.name, self.product_id.name)
        task.message_post(body=task_msg)
        return task

    def _timesheet_service_generation(self):

        so_line_task_global_project = self.filtered(
            lambda sol: sol.is_service and sol.product_id.service_tracking == 'task_global_project')
        so_line_new_project = self.filtered(lambda sol: sol.is_service and sol.product_id.service_tracking in [
                                            'project_only', 'task_in_project'])

        # search so lines from SO of current so lines having their project generated, in order to check if the current one can
        # create its own project, or reuse the one of its order.
        map_so_project = {}
        if so_line_new_project:
            order_ids = self.mapped('order_id').ids
            so_lines_with_project = self.search([('order_id', 'in', order_ids), ('project_id', '!=', False), ('product_id.service_tracking', 'in', [
                                                'project_only', 'task_in_project']), ('product_id.project_template_id', '=', False)])
            map_so_project = {
                sol.order_id.id: sol.project_id for sol in so_lines_with_project}
            so_lines_with_project_templates = self.search([('order_id', 'in', order_ids), ('project_id', '!=', False), (
                'product_id.service_tracking', 'in', ['project_only', 'task_in_project']), ('product_id.project_template_id', '!=', False)])
            map_so_project_templates = {(sol.order_id.id, sol.product_id.project_template_id.id)
                                         : sol.project_id for sol in so_lines_with_project_templates}

        # search the global project of current SO lines, in which create their task

        map_sol_project = {}
        if so_line_task_global_project:
            map_sol_project = {sol.id: sol.product_id.with_company(
                sol.company_id).project_id for sol in so_line_task_global_project}

        def _can_create_project(sol):

            if not sol.project_id:
                if sol.product_id.project_template_id:
                    return (sol.order_id.id, sol.product_id.project_template_id.id) not in map_so_project_templates
                elif sol.order_id.id not in map_so_project:
                    return True
            return False

        def _determine_project(so_line):
            """Determine the project for this sale order line.
            Rules are different based on the service_tracking:

            - 'project_only': the project_id can only come from the sale order line itself
            - 'task_in_project': the project_id comes from the sale order line only if no project_id was configured
              on the parent sale order"""

            if so_line.order_id.project_id:
                return so_line.order_id.project_id

            if so_line.product_id.service_tracking == 'project_only':
                return so_line.project_id
            elif so_line.product_id.service_tracking == 'task_in_project':
                return so_line.order_id.project_id or so_line.project_id

            return False

        # task_global_project: create task in global project
        for so_line in so_line_task_global_project:

            if not so_line.task_id:
                if so_line.order_id.project_id:
                    project = so_line.order_id.project_id
                else:
                    project = map_sol_project[so_line.id]

                if map_sol_project.get(so_line.id) and so_line.product_uom_qty > 0:
                    so_line._timesheet_create_task(project=project)

        # project_only, task_in_project: create a new project, based or not on a template (1 per SO). May be create a task too.
        # if 'task_in_project' and project_id configured on SO, use that one instead
        for so_line in so_line_new_project:
            project = _determine_project(so_line)
            if not project and _can_create_project(so_line):
                project = so_line._timesheet_create_project()
                if so_line.product_id.project_template_id:
                    map_so_project_templates[(
                        so_line.order_id.id, so_line.product_id.project_template_id.id)] = project
                else:
                    map_so_project[so_line.order_id.id] = project
            elif not project:
                # Attach subsequent SO lines to the created project
                so_line.project_id = (
                    map_so_project_templates.get(
                        (so_line.order_id.id, so_line.product_id.project_template_id.id))
                    or map_so_project.get(so_line.order_id.id)
                )
            if so_line.product_id.service_tracking == 'task_in_project':
                if not project:
                    if so_line.product_id.project_template_id:
                        project = map_so_project_templates[(
                            so_line.order_id.id, so_line.product_id.project_template_id.id)]
                    else:
                        project = map_so_project[so_line.order_id.id]
                if not so_line.task_id:
                    so_line._timesheet_create_task(project=project)
