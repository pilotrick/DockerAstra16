odoo.define('sh_image_hotspot_snippet.image_hotspot_options', function(require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

	options.registry.add_image_hotshpot = options.Class.extend({
    	events:{
	        'click we-button.sh_add_hotspot':'_addHotspot',
	    },
		
	    _addHotspot: function () {
	    	var spot = '<div class="image_hotspot hotspot_style_1 popover_style_1" data-prod-select-id="" style="cursor: pointer;margin-bottom:0; position: absolute; z-index: 100; top:50%;left: 50%;transform: translate(-50%, -50%);"><button class="hotspot_info" data-container="body" data-toggle="popover" data-placement="bottom" data-content="product_info" data-html="true"><i class="fa fa-circle text-primary"/></button></div>';
			this.$target.after(spot);
			//var static_info = $(qweb.render("sh_image_hotspot_snippet.static_image_hotspot_info_style_1"));
			//static_info.appendTo($('.image_hotspot'));
			//var static_data = this.$target.find(".static_image_hotspot_info").html();
            //var static_data_bgcolor = this.$target.find(".static_image_hotspot_info").css('background-color');
            //his.$target.find('.hotspot_info').attr('data-content', '<div class="static_image_hotspot_info" style="background-color: '+static_data_bgcolor+'">'+static_data+'</div>');
			
	    },
	});

	options.registry.hotspot_posi = options.Class.extend({
    	events:{
	        'change we-range.horizontal_posi':'_horizontalposi',
	        'change we-range.vertical_posi':'_verticalposi',
	        'click we-button.show_preview':'_showstaticpreview',
			'click .popover_styles we-button':'_onClickPopoverStyle',
			'click .hotspot_styles we-button':'_onClickHotspotStyle',
	    },
	    _horizontalposi: function () {
	    	var horizontal_posi = this.$target.attr('data-horizontal_posi');
	    	var horizontal_posi = horizontal_posi+'%';
	    	this.$target.css('left', horizontal_posi);
	    },

	    _verticalposi: function () {
	    	var vertical_posi = this.$target.attr('data-vertical_posi');
	    	var vertical_posi = vertical_posi+'%';
	    	this.$target.css('top', vertical_posi);
	    },

		_onClickHotspotStyle: function () {
			var Style1 = $(this.$target.hasClass('hotspot_style_1'));
			if(Style1){
				this.$target.find("i[class*='fa-']").removeClass (function (index, css) {
				  return (css.match (/(^|\s)fa-\S+/g) || []).join(' ');
				});
				this.$target.find('i.fa').addClass('fa-circle')
			}
			
			var Style2 = this.$target.hasClass('hotspot_style_2');
			
			if(Style2){
				this.$target.find("i[class*='fa-']").removeClass (function (index, css) {
				  return (css.match (/(^|\s)fa-\S+/g) || []).join(' ');
				});
				this.$target.find('i.fa').addClass('fa-plus')
			}
			
			var Style3 = this.$target.hasClass('hotspot_style_3');
			
			if(Style3){
				this.$target.find("i[class*='fa-']").removeClass (function (index, css) {
				  return (css.match (/(^|\s)fa-\S+/g) || []).join(' ');
				});
				this.$target.find('i.fa').addClass('fa-info')
			}
			
			
		},

		_onClickPopoverStyle: function (ev) {
			var styleOption = $(ev.currentTarget).data('select-data-attribute');
			if(styleOption){
				this._rpc({
                route: "/sh_image_hotspot_info",
                params: {
                    styleOption: styleOption,
                },
				}).then((data) => {
					if(data.html){
						if(this.$target.find('.static_image_hotspot_info')){
							this.$target.find('.static_image_hotspot_info').remove()
						}
						var static_info = data.html
						var html = '<section class="static_image_hotspot_info show_edit position-absolute w-auto">' +static_info+ '</section>'
						this.$target.append(html);
					}
	            });
			}
			
		},

	    _showstaticpreview: function () {
			
	    	if (this.$target.find(".static_image_hotspot_info").hasClass('show_edit')) {
	    		this.$target.find(".static_image_hotspot_info").removeClass('show_edit')
                var hotspot_btn = this.$target.find('.static_image_hotspot_info .hotspot-link > a');
                var hotspot_btn_style = this.$target.find('.static_image_hotspot_info .hotspot-link > a').attr('style');
                if($(hotspot_btn).find('font').length > 0){
                    var font_text = $(hotspot_btn).find('font').text();
                    var font_style = $(hotspot_btn).find('font').attr('style');
                    $(hotspot_btn).text(font_text);
                    if (hotspot_btn_style == undefined){
                        $(hotspot_btn).attr('style',font_style);
                    } else{
                        $(hotspot_btn).attr('style',hotspot_btn_style + font_style);
                    }
                }
                var static_data = this.$target.find(".static_image_hotspot_info").html();
                var static_data_bgcolor = this.$target.find(".static_image_hotspot_info").css('background-color');
                this.$target.find('.hotspot_info').attr('data-content', '<div class="static_image_hotspot_info" style="background-color: '+static_data_bgcolor+'">'+static_data+'</div>');
	    	} else {
	    		this.$target.find(".static_image_hotspot_info").addClass('show_edit')
	    	}
	    },

    });
	
});