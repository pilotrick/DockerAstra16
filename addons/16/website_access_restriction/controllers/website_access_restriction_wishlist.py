from odoo.http import request, route
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist

class CustomWebsiteSaleWishlist(WebsiteSaleWishlist):

  @route(['/shop/wishlist'], type='http', auth="public", website=True, sitemap=False)
  def get_wishlist(self, count=False, **kw):
    user = request.env.user
    if not user.has_group('base.group_user') and not user.has_group('base.group_portal'):
      return request.redirect('/web/login')

    return super(CustomWebsiteSaleWishlist, self).get_wishlist(count=count, **kw)
    

  @route(['/shop/wishlist/add'], type='json', methods=['POST'], auth="public", website=True)
  def add_to_wishlist(self, product_id, **kw):
    user = request.env.user
    if not user.has_group('base.group_user') and not user.has_group('base.group_portal'):
      return {'redirect': '/web/login'}

    return super(CustomWebsiteSaleWishlist, self).add_to_wishlist(product_id, **kw)


  @route(['/shop/wishlist/remove/<model("product.wishlist"):wish>'], type='json', auth='public', website=True)
  def rm_from_wishlist(self, wish, **kw):
    user = request.env.user
    if not user.has_group('base.group_user') and not user.has_group('base.group_portal'):
      return {'redirect': '/web/login'}
    
    return super(CustomWebsiteSaleWishlist, self).rm_from_wishlist(wish, **kw)
