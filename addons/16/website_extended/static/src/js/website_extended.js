odoo.define('website_extended.website_extended', function (require) {
    "use strict";

    var sAnimations = require('website.content.snippets.animation');
    var ajax = require('web.ajax');

    sAnimations.registry.website_extended_js = sAnimations.Class.extend({
        selector: "#wrapwrap",
        events: {
            'click #element_id': 'function_name',
        },
        start: function () {
            self = this;
        },

        });

    });