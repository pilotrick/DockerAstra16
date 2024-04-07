odoo.define('aspl_pos_kitchen_screen.PaymentScreen', function (require) {
    'use strict';

    const { _t } = require('web.core');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { posbus } = require('point_of_sale.utils');


    const PaymentScreenInh = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
            }
            async redirectBack(){
                var order = this.env.pos.get_order();
                if(order && order.is_from_sync_screen){
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Remove Order'),
                        body: this.env._t(
                            'Would you like to remove current order?'
                        ),
                    });
                    if (confirmed) {
                        await order.destroy({ reason: 'abandon' });
                        await posbus.trigger('order-deleted');
                        this.showScreen('ProductScreen');
                    }else{
                        this.showScreen('ProductScreen');
                    }
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PaymentScreenInh);

    return PaymentScreenInh;
});
