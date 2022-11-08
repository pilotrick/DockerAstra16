odoo.define('website_warehouse.payment_form', require => {
    'use strict';

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');

    const WWPaymentMixin = {

        // --------------------------------------------------------------------------
        // Private
        // --------------------------------------------------------------------------

    	_prepareTransactionRouteParams: function (provider, paymentOptionId, flow) {
        	var warehouse_id = $('select[name="field1"]').val();
            const transactionRouteParams = this._super(...arguments);
            return {
                ...transactionRouteParams,
                'warehouse': warehouse_id ? parseInt(warehouse_id) : undefined,
            };
        },

    };

    checkoutForm.include(WWPaymentMixin);
    manageForm.include(WWPaymentMixin);

});