from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrDiseaseCategory(models.Model):
    _name = 'hr.hospital.disease.category'
    _description = 'Disease Category'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(required=True, translate=True)
    complete_name = fields.Char(
        compute='_compute_complete_name',
        recursive=True, store=True, translate=True
    )
    parent_id = fields.Many2one(
        comodel_name='hr.hospital.disease.category',
        string='Category name', index=True,
        ondelete='cascade'
    )
    parent_path = fields.Char(index=True, unaccent=False)
    desc = fields.Text(string="Description")

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        """ Compute complete name """
        for category in self:
            if category.parent_id:
                name = f"{category.parent_id.complete_name}/{category.name}"
                category.complete_name = name
            else:
                category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        """ Check recursion for disease category"""
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))

    @api.model
    def name_create(self, name: str) -> dict:
        """ Create name """
        return self.create({'name': name}).name_get()[0]

    def name_get(self):
        """ Build display name """
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super().name_get()


class HrHospitalDisease(models.Model):
    _name = 'hr.hospital.disease'
    _description = _('Diseases')

    disease_id = fields.Many2one(
        comodel_name="hr.hospital.disease.category",
        string="Disease",
        index=True,
    )
    diagnosis_ids = fields.One2many(
        comodel_name="hr.hospital.diagnosis",
        inverse_name="disease_id"
    )
    active = fields.Boolean(default=True)

    def name_get(self):
        """ Build display name """
        return [(record.id, record.disease_id.name) for record in self]
