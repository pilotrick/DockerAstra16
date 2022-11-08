odoo.define('sh_corpomate_theme.js_editor_corpomate', function (require) {
    'use strict';

    const publicWidget = require("web.public.widget");
    

    publicWidget.registry.ShWebsiteEditorCorpomate = publicWidget.Widget.extend({
        selector: "#wrapwrap",
        disabledInEditableMode: true,

        /**
         * @constructor
         */
        init: function () {
            this._super.apply(this, arguments);
            
        },    


        destroy: function () {
            var self = this;
            
            this._super.apply(this, arguments);
            $('section.o_footer_copyright').find('a').addClass('oe_edited_link')
            $('section.o_footer_copyright').find('a').attr('contenteditable','true')
        },    

        
    });
    

});
