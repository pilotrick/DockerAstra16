from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    usd_price = fields.Float(
        string='Precio en USD',
    )

    @api.onchange('usd_price')
    def onchange_price(self):
        if self.usd_price:
            rate_obj = self.env['res.currency.rate']
            currency = self.env['res.currency'].search([('name', '=', 'USD')])
            date = self.env.context.get('date') or fields.Date.today()
            currency_rate_id = rate_obj.search([
                ('name', '=', date),
                ('currency_id', '=', currency.id),
                ('company_id', '=', self.env.company.id)])

            if currency_rate_id and currency_rate_id.rate > 0:
                currency_price = 1 / currency_rate_id.rate
            else:

                currency_rate_id = rate_obj.search([
                    ('currency_id', '=', currency.id),
                    ('company_id', '=', self.env.company.id),
                ], limit=1, order="name ASC")

                if currency_rate_id and currency_rate_id.rate > 0:
                    currency_price = 1 / currency_rate_id.rate
                else:
                    raise ValidationError('Debe Colocar la Tasa Primero')
                    
            list_price = currency_price * self.usd_price
            self.list_price = list_price
            self.usd_price = self.usd_price
            if self.product_variant_id and len(self.product_variant_id) == 1:
                self.product_variant_id.usd_price = self.usd_price
                self.product_variant_id.lst_price = list_price



    def _update_list_price_base_on_currency_rate(self):
        rate_obj = self.env['res.currency.rate']
        currency = self.env['res.currency'].search([('name', '=', 'USD')])
        date = self.env.context.get('date') or fields.Date.today()
        currency_rate_id = rate_obj.search([
            ('name', '=', date),
            ('currency_id', '=', currency.id),
            ('company_id', '=', self.env.company.id)])
        if currency_rate_id and currency_rate_id.rate > 0:
            currency_price = 1 / currency_rate_id.rate
        else:

            currency_rate_id = rate_obj.search([
                ('currency_id', '=', currency.id),
                ('company_id', '=', self.env.company.id),
            ], limit=1, order="name ASC")

            if currency_rate_id and currency_rate_id.rate > 0:
                currency_price = 1 / currency_rate_id.rate
            else:
                raise ValidationError('Debe Colocar la Tasa Primero')


        # currrency_rate = self._get_currency_rate()
        self.env.cr.execute("""
            SELECT id, usd_price FROM product_template 
            WHERE usd_price > 0;
        """)
        products = self.env.cr.dictfetchall()
        for product in products:
            product_id = product.get('id')
            usd_price = product.get('usd_price') * currency_price
            self.env.cr.execute("UPDATE product_template set list_price = %f "
                                "WHERE id = %d;" % (usd_price, product_id))
            _logger.info("Product ID: %d | USD Price: %f" % (
                product_id, usd_price))

    def _update_list_price_base_on_currency_rate_old(self):
        products = self.search([('usd_price', '>', 0)])
        for product in products:
            product._update_price_from_currency()

    def _update_price_from_currency(self):
        rate_obj = self.env['res.currency.rate']
        currency = self.env['res.currency'].search([('name', '=', 'USD')])
        date = self.env.context.get('date') or fields.Date.today()
        currency_rate_id = rate_obj.search([
            ('name', '=', date),
            ('currency_id', '=', currency.id),
            ('company_id', '=', self.env.company.id)])
        
        if currency_rate_id and currency_rate_id.rate > 0:
            currency_price = 1 / currency_rate_id.rate
        else:

            currency_rate_id = rate_obj.search([
                ('currency_id', '=', currency.id),
                ('company_id', '=', self.env.company.id),
            ], limit=1, order="name ASC")

            if currency_rate_id and currency_rate_id.rate > 0:
                currency_price = 1 / currency_rate_id.rate
            else:
                raise ValidationError('Debe Colocar la Tasa Primero')

        list_price = currency_price * self.usd_price
        self.write({
            'list_price': list_price,
        })
        if self.product_variant_id:
            self.product_variant_id.write({
                'usd_price': self.usd_price,
                'lst_price': list_price,
            })


class ProductProduct(models.Model):
    _inherit = 'product.product'

    usd_price = fields.Float(
        string='Precio en USD',
    )

    @api.onchange('usd_price')
    def onchange_usd_price(self):
        if self.usd_price:
            rate_obj = self.env['res.currency.rate']
            currency = self.env['res.currency'].search([('name', '=', 'USD')])
            date = self.env.context.get('date') or fields.Date.today()
            currency_rate_id = rate_obj.search([
                ('name', '=', date),
                ('currency_id', '=', currency.id),
                ('company_id', '=', self.env.company.id)])


            if currency_rate_id and currency_rate_id.rate > 0:
                currency_price = 1 / currency_rate_id.rate
            
            else:
                currency_rate_id = rate_obj.search([
                    ('currency_id', '=', currency.id),
                    ('company_id', '=', self.env.company.id),
                ], limit=1, order="name ASC")
                    
                if currency_rate_id and currency_rate_id.rate > 0:
                    currency_price = 1 / currency_rate_id.rate
                else:
                    raise ValidationError('Debe Colocar la Tasa Primero')

            list_price = currency_price * self.usd_price
            self.usd_price = self.usd_price
            self.lst_price = list_price
            self.product_tmpl_id.list_price = list_price
