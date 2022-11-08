# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http
from odoo.exceptions import AccessError
from odoo import release

import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression
_logger = logging.getLogger(__name__)

from odoo.addons.website_sale.controllers.main import WebsiteSale


class Hide_price(WebsiteSale):


	def _get_products_recently_viewed(self):
		sup = super(Hide_price, self)._get_products_recently_viewed()
		sup['user'] = request.env.user._is_public()
		sup['website'] = request.website.is_hide_price
		sup['website_price_email'] = request.website.price_support_email
		return sup

	@http.route('/shop/products/autocomplete', type='json', auth='public', website=True)
	def products_autocomplete(self, term, options={}, **kwargs):
		response = super(Hide_price, self).products_autocomplete(term)
		response['user'] = request.env.user._is_public()
		response['website'] = request.website.is_hide_price
		return response