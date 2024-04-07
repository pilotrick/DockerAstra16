from odoo import api, fields, models, _


class stock_quant(models.Model):
    _inherit = 'stock.quant'

    inv_backdated = fields.Datetime(string="Fecha Real", copy=False)
    backdated_remark = fields.Char(string="Notas", copy=False)

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super(stock_quant, self)._get_inventory_move_values(qty=qty, location_id=location_id, location_dest_id=location_dest_id, out=out)
        if self.inv_backdated:
            res.update({'inv_backdated': self.inv_backdated,
                        'date_deadline': self.inv_backdated,
                        'origin': self.backdated_remark})
        return res

    def _apply_inventory(self):
        for inventories in self.filtered(lambda l:l.inv_backdated):
            inventories.accounting_date = inventories.inv_backdated
        res = super(stock_quant, self)._apply_inventory()
        for inventories in self.filtered(lambda l:l.inv_backdated):
            inventories.write({'inv_backdated': False, 'backdated_remark': False})
        return res

    @api.model
    def _get_inventory_fields_create(self):
        res = super(stock_quant, self)._get_inventory_fields_create()
        res += ['inv_backdated', 'backdated_remark']
        return res

    @api.model
    def _get_inventory_fields_write(self):
        res = super(stock_quant, self)._get_inventory_fields_write()
        res += ['inv_backdated', 'backdated_remark']
        return res
