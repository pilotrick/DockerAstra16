odoo.define('sh_corpomate_theme.image_hotspot_frontend', function(require) {
    'use strict';

var publicWidget = require('web.public.widget');
	
	publicWidget.registry.imghotspotpopover = publicWidget.Widget.extend({
		selector: ".image_hotspot",
		events: {
	        'click .hotspot_info': '_openhotspotpopover',
	    },

	    init: function () {
			this._super.apply(this, arguments);
	        this._popoverRPC = null;
	    },
		start: function () {
			var self = this
			var popover_bg = this.$el.find(".static_image_hotspot_info").css('background-color');
			this.$el.find('.hotspot_info').popover({
	            trigger: 'manual',
	            animation: true,
	            html: true,
	            container: 'body',
	            placement: 'bottom',
	            trigger: 'focus',
	            template: '<div class="popover hotspot-popover" style="background-color: '+popover_bg+'; border-color: '+popover_bg+'" role="tooltip"><div class="arrow" style="border-color: '+popover_bg+'"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
	        });
			$("body").addClass("image_hotspot_active");
			this._super.apply(this, arguments);
		},

		_openhotspotpopover: function (ev) {
			var self = this;
			$(this.selector).not(ev.currentTarget).popover('hide');
			self.$el.find('.hotspot_info').popover("show");

		}
	});
	
	
});