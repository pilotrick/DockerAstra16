# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import http
from odoo.http import request


class WebsitePortfolio(http.Controller):
    @http.route([
        "/page/portfolio",
    ], type="http", auth="public", website=True)
    def portfolio(self, **post):

        search_portfolio = False
        search_categories = False
        if request.website:
            portfolio_obj = request.env["website.portfolio"]
            portfolio_category_obj = request.env["website.portfolio.category"]

            search_portfolio = portfolio_obj.search([
                ("is_active", "=", True),
                ("website_id", "=", request.website.id)
            ])
            search_categories = portfolio_category_obj.search([
                ("is_active", "=", True),
                ("website_id", "=", request.website.id)
            ])

        return request.render(
            "sh_corpomate_theme.portfolio",
            {"portfolio": search_portfolio,
             "categories": search_categories}
        )
