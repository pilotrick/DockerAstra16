odoo.define('real_estate_bs', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var website = require('website.website');
    
    $(document).ready(function() {
        var garden = $('input[name="garden"]');
        var gardenDiv = $('#garden-things');
        
        garden.on('change', function() {
            if(garden.is(':checked') && garden.val() == 'no') {
            // if(garden.val() == 'no') {
                gardenDiv.hide();
            } else {
                gardenDiv.show();
            }
        });
    });
    
});