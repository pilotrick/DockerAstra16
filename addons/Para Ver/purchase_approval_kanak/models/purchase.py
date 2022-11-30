# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_compare


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_order_approval_rule_ids = fields.One2many('purchase.order.approval.rules', 'purchase_order', string='Purchase Order Approval Lines', readonly=True, copy=False)
    purchase_order_approval_history = fields.One2many('purchase.order.approval.history', 'purchase_order', string='Purchase Order Approval History', readonly=True, copy=False)
    approve_button = fields.Boolean(compute='_compute_approve_button', string='Approve Button ?', search='_search_to_approve_orders', copy=False)
    ready_for_po = fields.Boolean(compute='_compute_ready_for_po', string='Ready For PO ?', copy=False)
    send_for_approval = fields.Boolean(string="Send For Approval", copy=False)
    supplier_rep_ids = fields.Many2many('res.partner', 'supplier_purchase_rel', 'supplier_id', 'partner_id', string='Supplier Representatives')
    is_rejected = fields.Boolean(string='Rejected ?', copy=False)
    user_ids = fields.Many2many('res.users', 'purchase_user_rel', 'purchase_id', 'uid', string='Approval Users')
    purchase_order_approval_rule_id = fields.Many2one('purchase.order.approval.rule', related='company_id.purchase_order_approval_rule_id', string='Purchase Order Approval Rules')
    purchase_order_approval = fields.Boolean(related='company_id.purchase_order_approval', string='Purchase Order Approval By Rule')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(PurchaseOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type in ['tree', 'form'] and (self.user_has_groups('purchase.group_purchase_user') and not self.user_has_groups('purchase.group_purchase_manager')):
            if self._context.get('purchase_approve'):
                for node in doc.xpath("//tree"):
                    node.set('create', 'false')
                    node.set('edit', 'false')
                for node_form in doc.xpath("//form"):
                    node_form.set('create', 'false')
                    node_form.set('edit', 'false')
        res['arch'] = etree.tostring(doc)
        return res

    def _search_to_approve_orders(self, operator, value):
        res = []
        for i in self.search([('purchase_order_approval_rule_ids', '!=', False)]):
            approval_lines = i.purchase_order_approval_rule_ids.filtered(lambda b: not b.is_approved).sorted(key=lambda r: r.sequence)
            if approval_lines:
                same_seq_lines = approval_lines.filtered(lambda b: b.sequence == approval_lines[0].sequence)
                if self.env.user in same_seq_lines.mapped('users') and i.send_for_approval:
                    res.append(i.id)
        return [('id', 'in', res)]

    @api.depends('purchase_order_approval_rule_ids.is_approved')
    def _compute_approve_button(self):
        for rec in self:
            if rec.company_id.purchase_order_approval and rec.company_id.purchase_order_approval_rule_id:
                approval_lines = rec.purchase_order_approval_rule_ids.filtered(lambda b: not b.is_approved).sorted(key=lambda r: r.sequence)
                if approval_lines:
                    same_seq_lines = approval_lines.filtered(lambda b: b.sequence == approval_lines[0].sequence)
                    if same_seq_lines:
                        if self.env.user in same_seq_lines.mapped('users') and rec.send_for_approval:
                            rec.approve_button = True
                        else:
                            rec.approve_button = False
                    else:
                        rec.approve_button = False
                else:
                    rec.approve_button = False
            else:
                rec.approve_button = False

    @api.depends('purchase_order_approval_rule_ids.is_approved')
    def _compute_ready_for_po(self):
        for rec in self:
            if rec.company_id.purchase_order_approval and rec.company_id.purchase_order_approval_rule_id:
                    if all([i.is_approved for i in rec.purchase_order_approval_rule_ids]) and rec.purchase_order_approval_rule_ids:
                        rec.ready_for_po = True
                    else:
                        rec.ready_for_po = False
            else:
                rec.ready_for_po = True

    def action_button_approve(self):
        for rec in self:
            template_id = self.env.ref('purchase_approval_kanak.email_template_rfq_approved')
            if rec.purchase_order_approval_rule_ids:
                rules = rec.purchase_order_approval_rule_ids.filtered(lambda b: self.env.user in b.users)
                rules.write({'is_approved': True, 'state': 'approve', 'date': fields.Datetime.now(), 'user_id': self.env.user.id})
                msg = _("RFQ has been approved by %s.") % (self.env.user.name)
                self.message_post(body=msg, subtype_xmlid='mail.mt_comment')

                self.env['purchase.order.approval.history'].create({
                    'purchase_order': rec.id,
                    'user': self.env.user.id,
                    'date': fields.Datetime.now(),
                    'state': 'approved'
                })
            if rec.state == 'sent' and not rec.purchase_order_approval_rule_ids.filtered(lambda a: a.state == 'draft'):
                rec.button_confirm()
            template_id.send_mail(rec.id, force_send=True)

    def _get_data_purchase_order_approval_rule_ids(self):
        values = []
        approval_rule = self.company_id.purchase_order_approval_rule_id
        if self.company_id.purchase_order_approval and approval_rule.approval_rule_ids:
            for rule in approval_rule.approval_rule_ids.sorted(key=lambda r: r.sequence):
                if not rule.approval_category:
                    if not(rule.purchase_lower_limit == -1 or rule.purchase_upper_limit == -1) and self.amount_total:
                        if rule.purchase_lower_limit <= self.amount_total and self.amount_total <= rule.purchase_upper_limit:
                            values.append({
                                'sequence': rule.sequence,
                                'approval_role': rule.approval_role.id,
                                'email_template': rule.email_template.id,
                                'purchase_order': self.id,
                            })
                    else:
                        if rule.purchase_upper_limit == -1 and self.amount_total >= rule.purchase_lower_limit and self.amount_total:
                            values.append({
                                'sequence': rule.sequence,
                                'approval_role': rule.approval_role.id,
                                'email_template': rule.email_template.id,
                                'purchase_order': self.id,
                            })
                        if rule.purchase_lower_limit == -1 and self.amount_total <= rule.purchase_upper_limit and self.amount_total:
                            values.append({
                                'sequence': rule.sequence,
                                'approval_role': rule.approval_role.id,
                                'email_template': rule.email_template.id,
                                'purchase_order': self.id,
                            })
                if rule.approval_category:
                    rule_approval_category_order_lines = self.order_line.filtered(lambda b: b.product_id.approval_category == rule.approval_category)
                    if rule_approval_category_order_lines:
                        subtotal = sum(rule_approval_category_order_lines.mapped('price_subtotal'))
                        if not(rule.purchase_lower_limit == -1 or rule.purchase_upper_limit == -1):
                            if rule.purchase_lower_limit <= subtotal and subtotal <= rule.purchase_upper_limit:
                                values.append({
                                    'sequence': rule.sequence,
                                    'approval_role': rule.approval_role.id,
                                    'email_template': rule.email_template.id,
                                    'purchase_order': self.id,
                                })
                        else:
                            if rule.purchase_upper_limit == -1 and subtotal >= rule.purchase_lower_limit:
                                values.append({
                                    'sequence': rule.sequence,
                                    'approval_role': rule.approval_role.id,
                                    'email_template': rule.email_template.id,
                                    'purchase_order': self.id,
                                })
                            if rule.purchase_lower_limit == -1 and subtotal <= rule.purchase_upper_limit:
                                values.append({
                                    'sequence': rule.sequence,
                                    'approval_role': rule.approval_role.id,
                                    'email_template': rule.email_template.id,
                                    'purchase_order': self.id,
                                })
        return values

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        values = res._get_data_purchase_order_approval_rule_ids()
        if values:
            for v in values:
                self.env['purchase.order.approval.rules'].create(v)
        if res.purchase_order_approval_rule_ids:
            res.user_ids = [(6, 0, res.purchase_order_approval_rule_ids.mapped('users').ids)]
        return res

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if vals.get('order_line'):
            values = self._get_data_purchase_order_approval_rule_ids()
            approval_roles = self.purchase_order_approval_rule_ids.mapped('approval_role')
            for v in values:
                if not v.get('approval_role') in approval_roles.ids:
                    self.env['purchase.order.approval.rules'].create(v)
            for a in self.purchase_order_approval_rule_ids:
                if a.approval_role.id not in map(lambda x: x['approval_role'], values):
                    a.unlink()
            self.user_ids = [(6, 0, self.purchase_order_approval_rule_ids.mapped('users').ids)]
        if self.user_ids:
            if self.env.user not in self.user_ids and not self._context.get('purchase_approve') and (self.user_has_groups('purchase.group_purchase_user') and not self.user_has_groups('purchase.group_purchase_manager')):
                raise ValidationError(_("You can only edit your assigned RFQ."))
        return res

    def reject_purchase(self):
        return {
            'name': _('Rejection Reason'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.rejection.reason',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def action_send_for_approval(self):
        for record in self:
            template_id = self.env.ref('purchase_approval_kanak.email_template_rfq_approval_request')
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            for line in record.order_line:
                if line.display_type == 'line_section':
                    continue
                if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                
                if line.price_subtotal <= 0.0:
                    context = dict(self._context or {})
                    context['purchase_order'] = True
                    return {
                        'name': _('Warning !'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'custom.warning',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': context
                    }
            if record.purchase_order_approval_rule_ids:
                record.message_subscribe(
                    partner_ids=record.purchase_order_approval_rule_ids.mapped('users.partner_id.id'))
                msg = _("PO is waiting for approval.")
                record.message_post(body=msg, subtype_xmlid='mail.mt_comment')

            self.env['purchase.order.approval.history'].create({
                'purchase_order': record.id,
                'user': self.env.user.id,
                'date': fields.Datetime.now(),
                'state': 'send_for_approval'
            })
            template_id.send_mail(record.id, force_send=True)
            record.write({'send_for_approval': True, 'is_rejected': False})

    def button_draft(self):
        res = super(PurchaseOrder, self).button_draft()
        self.purchase_order_approval_rule_ids.unlink()
        self.write({'send_for_approval': False, 'is_rejected': False})
        values = self._get_data_purchase_order_approval_rule_ids()
        approval_roles = self.purchase_order_approval_rule_ids.mapped('approval_role')
        for v in values:
            if not v.get('approval_role') in approval_roles.ids:
                self.env['purchase.order.approval.rules'].create(v)
        for a in self.purchase_order_approval_rule_ids:
            if a.approval_role.id not in map(lambda x: x['approval_role'], values):
                a.unlink()
        self.user_ids = [(6, 0, self.purchase_order_approval_rule_ids.mapped('users').ids)]
        if self.user_ids:
            if self.env.user not in self.user_ids and not self._context.get('purchase_approve') and (self.user_has_groups('purchase.group_purchase_user') and not self.user_has_groups('purchase.group_purchase_manager')):
                raise ValidationError(_("You can only edit your assigned RFQ."))
        return res

class PurchaseOrderApprovalRules(models.Model):
    _name = 'purchase.order.approval.rules'
    _description = 'Purchase Order Approval Rules'
    _order = 'sequence'

    purchase_order = fields.Many2one('purchase.order', string='Purchase Order', ondelete='cascade')
    sequence = fields.Integer(required=True)
    approval_role = fields.Many2one('approval.role', string='Approval Role', required=True)
    users = fields.Many2many('res.users', compute='_compute_users')
    email_template = fields.Many2one('mail.template', string='Mail Template')
    date = fields.Datetime()
    user_id = fields.Many2one('res.users', string='User')
    is_approved = fields.Boolean(string='Approved ?')
    state = fields.Selection([
            ('approve', 'Approved'),
            ('reject', 'Reject'),
            ('draft', 'Draft')
        ], string='Status', index=True, readonly=True, default='draft')

    @api.depends('approval_role')
    def _compute_users(self):
        for rec in self:
            if rec.approval_role:
                employees = self.env['hr.employee'].search([('approval_role', '=', rec.approval_role.id)])
                users = self.env['res.users'].search([('employee_ids', 'in', employees.ids)])
                rec.users = [(6, 0, users.ids)]


class PurchaseRejectionReason(models.TransientModel):
    _name = 'purchase.rejection.reason'
    _description = "Purchase Rejection Reason"
    _rec_name = 'reason'

    reason = fields.Text(required=True)

    def button_reject(self):
        template_id = self.env.ref('purchase_approval_kanak.email_template_rfq_rejected')
        if self.env.context.get('active_id'):
            order = self.env['purchase.order'].browse(self.env.context['active_id'])
            if order.purchase_order_approval_rule_ids:
                rules = order.purchase_order_approval_rule_ids.filtered(lambda b: self.env.user in b.users)
                rules.write({'is_approved': False, 'date': fields.Datetime.now(), 'state': 'reject', 'user_id': self.env.user.id})
                msg = _("RFQ has been rejected by %s.") % (self.env.user.name)
                order.message_post(body=msg, subtype_xmlid='mail.mt_comment')
                template_id.send_mail(order.id, force_send=True)
                order.write({'is_rejected': True, 'send_for_approval': False})
                self.env['purchase.order.approval.history'].create({
                    'purchase_order': order.id,
                    'user': self.env.user.id,
                    'date': fields.Datetime.now(),
                    'state': 'reject',
                    'rejection_reason': self.reason
                })
