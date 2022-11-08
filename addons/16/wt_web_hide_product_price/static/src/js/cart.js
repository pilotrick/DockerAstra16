odoo.define('wt_web_hide_product_price.cart', function (require) {
'use strict';

var core = require('web.core');
var publicWidget = require('web.public.widget');
var Dialog = require('web.Dialog');
var _t = core._t;

publicWidget.registry.websiteproductAddtoCart = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'click #add_to_cart_unclickable': '_onAddtoCartClick',
    },

    start: function () {
        var self = this;
        return this._super.apply(this, arguments);
    },

    _onAddtoCartClick: function (ev) {
            var content = $('<div>').html(_t('<p>you need to login to buy a product!<p/>') );
            new Dialog(self, {
                    title: _t('Warning!'),
                    size: 'medium',
                    $content: content,
                    buttons: [
                    {text: _t('Ok'), close: true}]
                }).open();
    },

});
});
