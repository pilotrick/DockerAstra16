odoo.define('aspl_pos_kitchen_screen.ProductScreen', function(require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen')
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    const AsplKitchenProductScreen = ProductScreen =>
        class extends ProductScreen {
            setup() {
                super.setup();
                useListener('set-order-type-mode', this._setOrderTypeMode);
            }
            _setOrderTypeMode(event) {
                const { mode } = event.detail;
                this.state.orderTypeMode = mode;
            }
            async _onClickPay() {
                if(this.env.pos.user.kitchen_screen_user === 'waiter'){
                    this.showNotification(this.env._t('You do not have a rights of payment!'));
                    return
                }
                if (this.currentOrder.getOrderType() == 'delivery') {
                    if (!this.currentOrder.get_partner()) {
                        this.showNotification(this.env._t("Please select the customer first.", 1500));
                        return;
                    }
                    let orderLines = this.currentOrder.get_orderlines().filter(
                                        (line)=>this.env.pos.config.delivery_charge_product_id[0] == line.product.id);

                    if (!orderLines) {
                        this.showNotification(this.env._t("Please Select The Delivery Service.", 1500));
                    }
                    super._onClickPay();
                } else {
                    super._onClickPay();
                }
            }
            async _setValue(val){
                let line = this.currentOrder.get_selected_orderline();
                if(line === undefined){
                    super._setValue(...arguments);
                    return;
                }
                if(line.state != 'Waiting' && this.env.pos.numpadMode  === 'quantity'){
                    this.showNotification('You can not change the quantity!')
                }else{
                    super._setValue(...arguments);
                }
            }
        };

    Registries.Component.extend(ProductScreen, AsplKitchenProductScreen);

    return ProductScreen;
});
