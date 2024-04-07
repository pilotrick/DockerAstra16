odoo.define('aspl_pos_kitchen_screen.OrderSyncScreenButton', function(require) {
    'use strict';

    const { useState } = owl;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class OrderSyncScreenButton extends PosComponent {
        setup() {
            super.setup();
        }
        onClick() {
            this.trigger('click-sync-order-screen');
        }
        get blockButton() {
            return this.props.data !==  'KitchenScreen' ? '' : 'blockButton';
        }
        get count() {
           return this.props.countOrder || 0;
        }
    }
    OrderSyncScreenButton.template = 'OrderSyncScreenButton';

    Registries.Component.add(OrderSyncScreenButton);

    return OrderSyncScreenButton;
});
