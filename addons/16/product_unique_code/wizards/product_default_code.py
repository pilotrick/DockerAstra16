
from odoo import models, fields

class ProductDefaultCode(models.Model):
    _name = "product.default.code"
    _description = "Set Product Internal Reference as Unique"

    
    prefix = fields.Char(
        string='Prefix',
    )

    
    type_of_set = fields.Selection(
        string='Type of set',
        selection=[
            ('all', 'All'), 
            ('not_null', 'Not null')
        ],
        default= 'all'
    )

    def set_default_code(self):
        if self.type_of_set == 'not_null':
            self._cr.execute(
                f"""UPDATE product_product
                SET default_code = '{self.prefix}' || nextval('ir_default_id_seq')
                WHERE default_code is NULL or LENGTH(default_code) = 0"""
            )
        else:
            self._cr.execute(
                f"""UPDATE product_product
                SET default_code = '{self.prefix}' || nextval('ir_default_id_seq')"""
            )

        return True
    
    