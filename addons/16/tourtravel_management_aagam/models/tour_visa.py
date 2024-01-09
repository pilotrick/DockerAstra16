from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TourVisa(models.Model):
    _name = 'tour.visa'

    name = fields.Char(string='Name', default='/', tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer Name')
    Mobile_number = fields.Char(string='Mobile', related='customer_id.mobile')
    email_id = fields.Char(string='Email Id', related='customer_id.email')
    visa = fields.Char(string='visa')
    travel_start_date = fields.Datetime(string='Travel Date')
    return_date = fields.Date(string='Return Date')
    tour_id = fields.Many2one('custom.tour', string='Tour')
    start_date_tour = fields.Date(string='Tour Date',  related='tour_id.tour_details_id.start_date')
    tour_booking_ref_id = fields.Many2one('booking.information', string='Tour Booking Ref.')
    service_cost =  fields.Integer(string='Service Cost')
    visa_document_ids = fields.One2many('visa.documentation', 'name')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'), ('in_progress', 'In Progress / Approval'),
            ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancel')
        ], string='Status', help='Status of the tour reservation',
        default='draft', tracking=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        tracking=True, required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    invoice_ids = fields.Many2many(
        "account.move", string='Invoices',
        readonly=True, copy=False)
        # compute = "get_invoices",
    invoice_count = fields.Integer(
        string='# of Invoices', compute='compute_count', readonly=True)
    qty_to_invoice = fields.Float(
        string='Qty to Invoice',  readonly=True)#compute='get_invoices',
    active = fields.Boolean(string='Active', default=True, tracking=True)
    service_product = fields.Many2one('product.product', string='Service')

    def compute_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count(
                [('invoice_origin', '=', self.name)])

    def get_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'invoice',
            'view_mode': 'tree',
            'res_model': 'account.move',
            'domain': [('invoice_origin', '=', self.name)],
            'context': "{'create': False}"
        }


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code(
            'tour.visa.seq') or '/'
        return super(TourVisa, self).create(values)

    def action_approve(self):
        self.write({'state': 'in_progress'})

    def action_confirmed(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_invoice(self):
        self.ensure_one()
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        invoice_values = {
            'name': self.name,
            'invoice_origin': self.name,
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.today(),
            # 'tour_visa_id': self.id,
            'currency_id': self.currency_id.id,
        }
        invoice_ids = []
        e_service_inv = False
        service_inv = False
        if self:
            service_inv = inv_obj.with_context(
                mail_create_nosubscribe=True).create(invoice_values)
            invoice_ids.append(service_inv.id)
            for service in self:
                # qty_to_invoice = 0
                # qty_to_invoice = service.no_of_pax - service.qty_invoiced
                name = '%s From: %s To: %s' % (
                    service.name, service.tour_id.travel_info_ids.from_place.name,
                    service.tour_id.travel_info_ids.to_place.name)
                for c in service:
                    new_line_values = {
                        'name':  name,
                        'move_id': service_inv.id,
                        'product_id': int(c.service_product),
                        'price_unit': c.service_cost,
                        'service_datetime': service.travel_start_date,
                        'quantity': 1,
                        'account_id': int(service_inv),
                        'person_cost_id': c.id,
                    }
                    # inv_line_obj.create(new_line_values)
                    service_inv.write({'invoice_line_ids': [(0, 0, new_line_values)]})
                # service.qty_invoiced = service.qty_invoiced + qty_to_invoice

        if invoice_ids:
            self.write({
                'invoice_ids':  [(4, invoice_ids[0])],
                })

            action = self.env.ref('account.action_move_out_invoice_type').read()[0]
            action['domain'] = [('id', 'in', invoice_ids)]
            return action
        else:
            raise UserError(
                _("Nothing to invoice:\nAll services are already invoiced."))


class VisaDocumentation(models.Model):
    _name = 'visa.documentation'

    name = fields.Char(string='name')
    document_type_ids = fields.Many2many('visa.documentation.list', string='Documentation Name')
    # attachment_ids = fields.Many2one('ir.attachment', string='Attachments')
    attachment_ids = fields.Binary(string='Attachments')
    document_name = fields.Char(string="Document Name")
    expiry_date = fields.Date(string='Expiry Date')




class VisaDocumentationList(models.Model):
    _name = 'visa.documentation.list'

    name = fields.Char(string='Name')


# passport documentation

class PassportDocumentation(models.Model):
    _name = 'passport.documentation'

    name = fields.Char(string='Name', default='/', tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer Name')
    create_date = fields.Date(string='Create Date')
    email = fields.Char(string='Email Id')
    mobile_num = fields.Char(string='Mobile Number')
    alter_mobile_number = fields.Char(string='Alter Mobile Number')
    service = fields.Many2one('product.product', string='Service')
    service_scheme = fields.Char(string='Service Scheme')
    service_cost = fields.Integer(string='Service Cost')
    documentation_ids = fields.One2many('visa.documentation', 'name')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'), ('in_progress', 'In Progress / Approval'),
            ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancel')
        ], string='Status', help='Status of the tour reservation',
        default='draft', tracking=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        tracking=True, required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    invoice_ids = fields.Many2many(
        "account.move", string='Invoices',
        readonly=True, copy=False)
        # compute = "get_invoices",
    invoice_count = fields.Integer(
        string='# of Invoices', compute='compute_count', readonly=True)
    qty_to_invoice = fields.Float(
        string='Qty to Invoice', compute='get_invoices', readonly=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    tour_id = fields.Many2one('custom.tour', string='Tour')
    service_product = fields.Many2one('product.product', string='Service')


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code(
            'tour.passport.seq') or '/'
        return super(PassportDocumentation, self).create(values)


    def action_approve(self):
        self.write({'state': 'in_progress'})

    def action_confirmed(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def compute_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count(
                [('invoice_origin', '=', self.name)])

    def get_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'invoice',
            'view_mode': 'tree',
            'res_model': 'account.move',
            'domain': [('invoice_origin', '=', self.name)],
            'context': "{'create': False}"
        }

    def action_invoice(self):
        self.ensure_one()
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        invoice_values = {
            'name': self.name,
            'invoice_origin': self.name,
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.today(),
            # 'tour_passport_id': self.id,
            'currency_id': self.currency_id.id,
        }
        invoice_ids = []
        e_service_inv = False
        service_inv = False
        
        if self:
            service_inv = inv_obj.with_context(
                mail_create_nosubscribe=True).create(invoice_values)
            invoice_ids.append(service_inv.id)
            for service in self:
                to_place_names = []
                
                for travel_info in service.tour_id.travel_info_ids:
                    to_place_names.append(travel_info.to_place.name)
                
                to_place_name = ', '.join(to_place_names)
                
                name = '%s From: %s To: %s' % (
                    service.name,
                    service.tour_id.travel_info_ids[0].from_place.name if service.tour_id.travel_info_ids else '',
                    to_place_name)
                
                for c in service:
                    new_line_values = {
                        'name': name,
                        'move_id': service_inv.id,
                        'product_id': int(c.service),
                        'price_unit': c.service_cost,
                        'service_datetime': service.create_date,
                        'quantity': 1,
                        'account_id': int(service_inv),
                        'person_cost_id': c.id,
                    }
                    # inv_line_obj.create(new_line_values)
                    service_inv.write({'invoice_line_ids': [(0, 0, new_line_values)]})
                # service.qty_invoiced = service.qty_invoiced + qty_to_invoice

        if invoice_ids:
            self.write({
                'invoice_ids': [(4, invoice_ids[0])],
            })

            action = self.env.ref('account.action_move_out_invoice_type').read()[0]
            action['domain'] = [('id', 'in', invoice_ids)]
            return action
        else:
            raise UserError(
                _("Nothing to invoice:\nAll services are already invoiced."))
