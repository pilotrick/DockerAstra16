from odoo import  fields, models, Command

class AccountMove(models.Model):

    _inherit = 'real.estate'

    def action_do_sold(self):
        res = super(AccountMove, self).action_do_sold()
        print('buyer : ' ,self.buyer)
        print('++++res+++',res)

        val = self.env["account.move"].create({
            'name': self.env['ir.sequence'].next_by_code(
                'property.invoice'),
            'partner_id': self.buyer.id,
            'move_type': 'out_invoice',
            'invoice_date':fields.datetime.now(),
            'invoice_line_ids': [
                Command.create({
                    'name': 'Property Price',
                    'quantity': 1,
                    'price_unit': self.selling_price,
                    'tax_ids': None,
                }),
                Command.create({
                    'name': 'Property Tax',
                    'price_unit': ((self.selling_price*6)/100),
                    'tax_ids': None,
                }),
                Command.create({
                    'name': 'Administrative Fees',
                    'price_unit': 100,
                    'tax_ids': None,
                }),
            ],
        })

        return res