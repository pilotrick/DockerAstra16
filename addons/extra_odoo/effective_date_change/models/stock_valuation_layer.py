from datetime import datetime
from psycopg2.extensions import AsIs

from odoo import models, api, fields, _

from odoo.exceptions import UserError


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    org_create_date = fields.Datetime(string='Origin Create Date', readonly=True, help="A technical field to store original create date."
                                      " When backdate is applied, we changed the value of create_date so this field is important to store"
                                      " its original value.")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockValuationLayer, self).create(vals_list)
        if self._context.get('force_period_date'):
            for each_rec in res:
                self.env.cr.execute("update stock_valuation_layer set create_date = %s where id = %s", (self._context.get('force_period_date'), each_rec.id))
        
        manual_validate_date_time = self._context.get('manual_validate_date_time', False)
        manual_validate_date_time_mrp = self._context.get('manual_validate_date_time_mrp', False)
        if manual_validate_date_time:
            now = fields.Datetime.now()
            for vals in vals_list:
                vals['org_create_date'] = now
            org_price_unit = self._context.get('org_price_unit', False)
            org_value = self._context.get('org_value', False)
            
            if org_value:
                if isinstance(manual_validate_date_time, datetime):
                    manual_validate_date_time = fields.Datetime.to_string(manual_validate_date_time)
                    #         if res:
                for svl in res:
                    move_id = svl.stock_move_id.id
                    if org_value[move_id] and org_value[move_id] > 0:
                        self.env.cr.execute("""
                        UPDATE %s
                        SET create_date=%s, write_date=%s,
                        unit_cost=%s, value=%s
                        WHERE id = %s
                        """, (
                            AsIs(self._table),
                            manual_validate_date_time,
                            manual_validate_date_time,
                            org_price_unit[move_id],
                            org_value[move_id],
                            svl.id
                            )
                        )
                    else:
                        self.env.cr.execute("""
                            UPDATE %s
                            SET create_date=%s, write_date=%s
                            WHERE id = %s
                            """, (
                            AsIs(self._table),
                            manual_validate_date_time,
                            manual_validate_date_time,
                            svl.id
                            )
                        )
                        
        if manual_validate_date_time_mrp:
            now = fields.Datetime.now()
            for vals in vals_list:
                vals['org_create_date'] = now
                
            for svl in res:
                if svl.id:
                    self.env.cr.execute("""
                        UPDATE %s
                        SET create_date=%s, write_date=%s
                        WHERE id = %s
                        """, (
                        AsIs(self._table),
                        manual_validate_date_time_mrp,
                        manual_validate_date_time_mrp,
                        svl.id
                        )
                    )
        return res
