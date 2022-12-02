from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    usd_standard_price = fields.Float(
        string='Costo en USD'
    )

    @api.onchange('standard_price')
    def onchange_usd_cost(self):
        if self.usd_standard_price:
            rate_obj = self.env['res.currency.rate']
            currency = self.env['res.currency'].search([('name', '=', 'USD')])
            date = self.env.context.get('date') or fields.Date.today()
            currency_rate_id = rate_obj.search([
                ('name', '=', date),
                ('currency_id', '=', currency.id),
                ('company_id', '=', self.env.company.id)])
            if currency_rate_id:
                currency_cost = 1 / currency_rate_id.rate
            else:
                currency_rate_id = rate_obj.search([
                    ('currency_id', '=', currency.id),
                    ('company_id', '=', self.env.company.id),
                ], limit=1, order="name ASC")
                currency_cost = 1 / currency_rate_id.rate
            usd_standard_price = self.standard_price / currency_cost
            self.usd_standard_price = usd_standard_price
            if self.product_variant_id and len(self.product_variant_id) == 1:
                self.product_variant_id.usd_standard_price = usd_standard_price

    def _update_cost_base_on_currency_rate(self):
        products = self.search([('standard_price', '>', 0)])
        for product in products:
            product._update_cost_from_currency()

    def _update_cost_from_currency(self):
        rate_obj = self.env['res.currency.rate']
        currency = self.env['res.currency'].search([('name', '=', 'USD')])
        date = self.env.context.get('date') or fields.Date.today()
        currency_rate_id = rate_obj.search([
            ('name', '=', date),
            ('currency_id', '=', currency.id),
            ('company_id', '=', self.env.company.id)])
        if currency_rate_id:
            currency_cost = 1 / currency_rate_id.rate
        else:
            currency_rate_id = rate_obj.search([
                ('currency_id', '=', currency.id),
                ('company_id', '=', self.env.company.id),
            ], limit=1, order="name ASC")
            currency_cost = 1 / currency_rate_id.rate
        usd_standard_price = self.standard_price / currency_cost
        self.usd_standard_price = usd_standard_price
        self.write({
            'usd_standard_price': usd_standard_price,
        })
        if self.product_variant_id and len(self.product_variant_id) == 1:
            self.product_variant_id.write({
                'usd_standard_price': usd_standard_price,
            })

    @api.depends_context('force_company')
    @api.depends('product_variant_ids', 'product_variant_ids.standard_price')
    def _compute_standard_price(self):
        # Depends on force_company context because standard_price is
        # company_dependent on the product_product
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.standard_price = template.product_variant_ids.standard_price
            template.onchange_usd_cost()
        for template in (self - unique_variants):
            template.standard_price = 0.0
            template.usd_standard_price = 0.0


class ProductProduct(models.Model):
    _inherit = 'product.product'

    usd_standard_price = fields.Float(
        string='Costo en USD',
        store=True,
        readonly=True,
        copy=False,
    )

    @api.onchange('standard_price')
    def onchange_usd_cost(self):
        if self.usd_standard_price:
            rate_obj = self.env['res.currency.rate']
            currency = self.env['res.currency'].search([('name', '=', 'USD')])
            date = self.env.context.get('date') or fields.Date.today()
            currency_rate_id = rate_obj.search([
                ('name', '=', date),
                ('currency_id', '=', currency.id),
                ('company_id', '=', self.env.company.id)])
            if currency_rate_id:
                currency_cost = 1 / currency_rate_id.rate
            else:
                currency_rate_id = rate_obj.search([
                    ('currency_id', '=', currency.id),
                    ('company_id', '=', self.env.company.id),
                ], limit=1, order="name ASC")
                currency_cost = 1 / currency_rate_id.rate
            usd_standard_price = self.standard_price / currency_cost 
            self.usd_standard_price = usd_standard_price
            self.write.usd_standard_price = usd_standard_price
            if self.product_variant_id and len(self.product_variant_id) == 1:
                self.product_variant_id.usd_standard_price = usd_standard_price
