from odoo import models, api, _
from datetime import date

from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _set_scheduled_date(self):
        for picking in self:
            picking.move_ids.write({'date': picking.scheduled_date})
        
    def _action_done(self):
        for rec in self:
            if rec.scheduled_date:
                rec.env.context = dict(rec.env.context)
                scheduled_date = rec.scheduled_date
                accounting_date = scheduled_date.date()
                rec.env.context.update({
                    'manual_validate_date_time': scheduled_date,
                    'picking_type_code': rec.picking_type_id.code,
                    'force_period_date': accounting_date
                })
                res = super(StockPicking, self)._action_done()

                manual_validate_date_time = rec._context.get('manual_validate_date_time', False)
                if manual_validate_date_time:
                    rec.filtered(lambda x: x.state == 'done').write({'date_done': manual_validate_date_time})
                return False