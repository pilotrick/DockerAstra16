odoo.define('aspl_pos_kitchen_screen.KitchenScreenButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    class KitchenScreenButton extends PosComponent {
        setup() {
            super.setup();
        }
        async onClick() {
            this.trigger('click-kitchen-screen');
        }
        get blockButton() {
            return this.props.data !==  'SyncOrderScreen' ? '' : 'blockButton';
        }
        get count(){
            return this.props.countOrder || 0;
        }
    }
    KitchenScreenButton.template = 'KitchenScreenButton';

    Registries.Component.add(KitchenScreenButton);

    return KitchenScreenButton;
});
