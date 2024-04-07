from odoo import fields, models


class PropertyTag(models.Model):
    _name = 'property.tags'

    name = fields.Char(string='Tags')
    color = fields.Integer()

    # sql constraints
    _sql_constraints = [
        ( 'unique_tag_name', 'unique(name)', 'Tag Must Be Unique.' )
    ]

