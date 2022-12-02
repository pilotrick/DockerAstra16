# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    log_fuel = fields.One2many('fleet.vehicle.log.fuel', 'vehicle_id', 'Fuel Logs')
    fuel_logs_count = fields.Integer(compute="_compute_count_all", string='Fuel Log Count')
    cost_count = fields.Integer(compute="_compute_count_all", string="Costs")

    def _compute_count_all(self):
        Odometer = self.env['fleet.vehicle.odometer']
        LogFuel = self.env['fleet.vehicle.log.fuel']
        LogService = self.env['fleet.vehicle.log.services']
        LogContract = self.env['fleet.vehicle.log.contract']
        Cost = self.env['fleet.vehicle.cost']
        for record in self:
            record.odometer_count = Odometer.search_count([('vehicle_id', '=', record.id)])
            record.fuel_logs_count = LogFuel.search_count([('vehicle_id', '=', record.id)])
            record.service_count = LogService.search_count([('vehicle_id', '=', record.id)])
            record.contract_count = LogContract.search_count([('vehicle_id', '=', record.id), ('state', '!=', 'closed')])
            record.cost_count = Cost.search_count([('vehicle_id', '=', record.id), ('parent_id', '=', False)])
            record.history_count = self.env['fleet.vehicle.assignation.log'].search_count([('vehicle_id', '=', record.id)])

    def return_action_to_open(self):
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        price = False
        price_date = False
        if self.fuel_id:
            FuelDetail = self.fuel_id.price_ids.mapped('id')[-1]
            price = self.env['fuel.detail'].browse(FuelDetail).price
            price_date = self.env['fuel.detail'].browse(FuelDetail).date
        if xml_id:
            try:
                res = self.env['ir.actions.act_window']._for_xml_id('fleet.%s' % xml_id)
            except:
                res = self.env['ir.actions.act_window']._for_xml_id('fleet_vehicle_log_fuel.%s' % xml_id)
            
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, default_price_per_liter=price, default_price_date=price_date, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
            )
            return res
        return False


class FleetVehicleCost(models.Model):
    _name = 'fleet.vehicle.cost'
    _description = 'Cost related to a vehicle'
    _order = 'date desc, vehicle_id asc'

    name = fields.Char(related='vehicle_id.name', string='Name', store=True, readonly=False)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True, help='Vehicle concerned by this log')
    cost_subtype_id = fields.Many2one('fleet.service.type', 'Type', help='Cost type purchased with this cost')
    amount = fields.Float('Total Price')
    cost_type = fields.Selection([
        ('contract', 'Contract'),
        ('services', 'Services'),
        ('fuel', 'Fuel'),
        ('other', 'Other')
        ], 'Category of the cost', default="other", help='For internal purpose only', required=True)
    parent_id = fields.Many2one('fleet.vehicle.cost', 'Parent', help='Parent cost to this current cost')
    cost_ids = fields.One2many('fleet.vehicle.cost', 'parent_id', 'Included Services', copy=True)
    odometer_id = fields.Many2one('fleet.vehicle.odometer', 'Odometer', help='Odometer measure of the vehicle at the moment of this log')
    odometer = fields.Float(compute="_get_odometer", inverse='_set_odometer', string='Odometer Value',
        help='Odometer measure of the vehicle at the moment of this log')
    odometer_unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True)
    date = fields.Date(help='Date when the cost has been executed')
    contract_id = fields.Many2one('fleet.vehicle.log.contract', 'Contract', help='Contract attached to this cost')
    auto_generated = fields.Boolean('Automatically Generated', readonly=True)
    description = fields.Char("Cost Description")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    def _get_odometer(self):
        self.odometer = 0.0
        for record in self:
            record.odometer = False
            if record.odometer_id:
                record.odometer = record.odometer_id.value

    def _set_odometer(self):
        for record in self:
            if not record.odometer:
                raise UserError(_('Emptying the odometer value of a vehicle is not allowed.'))
            odometer = self.env['fleet.vehicle.odometer'].create({
                'value': record.odometer,
                'date': record.date or fields.Date.context_today(record),
                'vehicle_id': record.vehicle_id.id
            })
            self.odometer_id = odometer

    @api.model_create_multi
    def create(self, vals_list):
        for data in vals_list:
            # make sure that the data are consistent with values of parent and contract records given
            if 'parent_id' in data and data['parent_id']:
                parent = self.browse(data['parent_id'])
                data['vehicle_id'] = parent.vehicle_id.id
                data['date'] = parent.date
                data['cost_type'] = parent.cost_type
            if 'contract_id' in data and data['contract_id']:
                contract = self.env['fleet.vehicle.log.contract'].browse(data['contract_id'])
                data['vehicle_id'] = contract.vehicle_id.id
                data['cost_subtype_id'] = contract.cost_subtype_id.id
                data['cost_type'] = contract.cost_type
            if 'odometer' in data and not data['odometer']:
                # if received value for odometer is 0, then remove it from the
                # data as it would result to the creation of a
                # odometer log with 0, which is to be avoided
                del data['odometer']
        return super(FleetVehicleCost, self).create(vals_list)

class FleetVehicleLogFuel(models.Model):
    _name = 'fleet.vehicle.log.fuel'
    _description = 'Fuel log for vehicles'
    _inherits = {'fleet.vehicle.cost': 'cost_id'}

    @api.model
    def default_get(self, default_fields):
        res = super(FleetVehicleLogFuel, self).default_get(default_fields)
        service = self.env.ref('fleet.type_service_refueling', raise_if_not_found=False)
        res.update({
            'date': fields.Date.context_today(self),
            'cost_subtype_id': service and service.id or False,
            'cost_type': 'fuel'
        })
        return res

    name_seq = fields.Char('fuel log', copy=False, required=True, index=True, readonly=True, default= lambda self: _('New') )
    price_date = fields.Date()
    liter = fields.Float()
    price_per_liter = fields.Float()
    purchaser_id = fields.Many2one('res.partner', 'Purchaser')
    inv_ref = fields.Char('Invoice Reference', size=64)
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    notes = fields.Text()
    cost_id = fields.Many2one('fleet.vehicle.cost', 'Cost', required=True, ondelete='cascade')
    # we need to keep this field as a related with store=True because the graph view doesn't support
    # (1) to address fields from inherited table
    # (2) fields that aren't stored in database
    cost_amount = fields.Float(related='cost_id.amount', string='Amount', store=True, readonly=False) 
   
    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.odometer_unit = self.vehicle_id.odometer_unit
            self.purchaser_id = self.vehicle_id.driver_id.id
            FuelType = self.vehicle_id.fuel_id 

            self.price_per_liter = False
            if FuelType:
                FuelDetail = FuelType.price_ids.mapped('id')[-1]
                price = self.env['fuel.detail'].browse(FuelDetail).price
                price_date = self.env['fuel.detail'].browse(FuelDetail).date
                self.price_per_liter = price


    @api.onchange('liter', 'price_per_liter', 'amount')
    def _onchange_liter_price_amount(self):
        # need to cast in float because the value receveid from web client maybe an integer (Javascript and JSON do not
        # make any difference between 3.0 and 3). This cause a problem if you encode, for example, 2 liters at 1.5 per
        # liter => total is computed as 3.0, then trigger an onchange that recomputes price_per_liter as 3/2=1 (instead
        # of 3.0/2=1.5)
        # If there is no change in the result, we return an empty dict to prevent an infinite loop due to the 3 intertwine
        # onchange. And in order to verify that there is no change in the result, we have to limit the precision of the
        # computation to 2 decimal
        liter = float(self.liter)
        price_per_liter = float(self.price_per_liter)
        amount = float(self.amount)
        if liter > 0 and price_per_liter > 0 and round(liter * price_per_liter, 2) != amount:
            self.amount = round(liter * price_per_liter, 2)
        elif amount > 0 and liter > 0 and round(amount / liter, 2) != price_per_liter:
            self.price_per_liter = round(amount / liter, 2)
        elif amount > 0 and price_per_liter > 0 and round(amount / price_per_liter, 2) != liter:
            self.liter = round(amount / price_per_liter, 2)

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('fleet.vehicle.log.fuel.sequence') or _('New')
        result = super(FleetVehicleLogFuel, self).create(vals)
        return result