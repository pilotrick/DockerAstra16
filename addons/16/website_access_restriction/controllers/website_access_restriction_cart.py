from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route

class CustomWebsiteSaleCart(WebsiteSale):

    @route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        user = request.env.user
        if not user.has_group('base.group_user') and not user.has_group('base.group_portal'):
            return request.redirect('/web/login')

        return super(CustomWebsiteSaleCart, self).cart(access_token=access_token, revive=revive, **post)
    
    @route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(
        self, product_id, add_qty=1, set_qty=0,
        product_custom_attribute_values=None, no_variant_attribute_values=None,
        express=False, **kwargs
    ):
        user = request.env.user
        if not user.has_group('base.group_user') and not user.has_group('base.group_portal'):
            return request.redirect('/web/login')

        return super(CustomWebsiteSaleCart, self).cart_update(
            product_id, add_qty=add_qty, set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
            express=express, **kwargs
        )

    @route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(
        self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
        product_custom_attribute_values=None, no_variant_attribute_values=None, **kw
    ):
        user = request.env.user
        if not user.has_group('base.group_user') and not user.has_group('base.group_portal'):
            return {'redirect': '/web/login'}

        return super(CustomWebsiteSaleCart, self).cart_update_json(
            product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, display=display,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values, **kw
        )