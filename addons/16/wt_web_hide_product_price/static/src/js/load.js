odoo.define('wt_web_hide_product_price.recently_viewd_product_template.xml', function (require) {
'use strict';
var core = require('web.core');
var concurrency = require('web.concurrency');
var config = require('web.config');
var ajax = require('web.ajax');
var qweb = core.qweb;
var session = require('web.session')
var publicWidget = require('web.public.widget');
var utils = require('web.utils');
var wSaleUtils = require('website_sale.utils');
var session = require('web.session');
// var recentproduct = require('website_sale.recently_viewed');

var qweb = core.qweb;

ajax.loadXML('/wt_web_hide_product_price/static/src/xml/recently_viewd_product_template.xml', qweb);


publicWidget.registry.productsRecentlyViewedSnippet.include({
        /*
         Adds the stock checking to the regular _render method
        @override
        */
        _render: function (res) {
        var products = res['products'];
        var user_id = res['user'];
        var hide_price = res['website']
        var price_email = res['website_price_email']
        var mobileProducts = [], webProducts = [], productsTemp = [];
        _.each(products, function (product) {
            if (productsTemp.length === 4) {
                webProducts.push(productsTemp);
                productsTemp = [];
            }
            product['user'] = user_id
            product['hide_price'] = hide_price
            product['email'] = price_email
            console.log("444444444444444444444444",products)

            productsTemp.push(product);
            mobileProducts.push([product]);
        });
        if (productsTemp.length) {
            webProducts.push(productsTemp);
        }

        this.mobileCarousel = $(qweb.render('website_sale.productsRecentlyViewed', {
            uniqueId: this.uniqueId,
            productFrame: 1,
            productsGroups: mobileProducts,
        }));
        this.webCarousel = $(qweb.render('website_sale.productsRecentlyViewed', {
            uniqueId: this.uniqueId,
            productFrame: 4,
            productsGroups: webProducts,
        }));
        this._addCarousel();
        this.$el.toggleClass('d-none', !(products && products.length));
    },
});

    publicWidget.registry.productsSearchBar.include({
        _render: function (res) {
        var $prevMenu = this.$menu;
        this.$el.toggleClass('dropdown show', !!res);
        if (res) {
            var products = res['products'];
            var user_id = res['user'];
            var hide_price = res['website']
            this.$menu = $(qweb.render('website_sale.productsSearchBar.autocomplete', {
                products: products,
                user: user_id,
                hide_price: hide_price,
                hasMoreProducts: products.length < res['products_count'],
                currency: res['currency'],
                widget: this,
            }));
            // console.log("%%%%%%%%%%user%%%%%%%%%%%",user)
            this.$menu.css('min-width', this.autocompleteMinWidth);
            this.$el.append(this.$menu);
        }
        if ($prevMenu) {
            $prevMenu.remove();
        }
    },
    })
});