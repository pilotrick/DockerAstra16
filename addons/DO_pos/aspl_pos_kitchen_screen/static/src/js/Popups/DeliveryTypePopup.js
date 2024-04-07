odoo.define('aspl_pos_kitchen_screen.DeliveryTypePopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    const { useState } = owl;
    const { _lt } = require('@web/core/l10n/translation');

    class DeliveryTypePopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            useListener('click-delivery-block', this._onClickDeliverySection);
            let order = this.env.pos.get_order();
            const {selectedDeliveryService, isDeliveryCharges} = this.props;
            this.state = useState({ isHighlight: '',
                                    selectedDelivery: selectedDeliveryService || false,
                                    isDeliveryCharge: isDeliveryCharges,
                                    deliveryUser: order.getDeliveryPerson() || false});
        }
        serviceById(id){
            return this.pos.env.deliveryTypeById[id];
        }
        _onClickDeliverySection({detail : event}){
            this.state.selectedDelivery = event;
        }
        getPayload() {
            return Object.assign({}, { 'type' : this.state.selectedDelivery,
                                       'charges' : this.state.isDeliveryCharge,
                                       'user': parseInt(this.state.deliveryUser)});
        }
        confirm(event) {
            if (this.state.selectedDelivery){
                if (this.state.deliveryUser){
                    super.confirm();
                } else {
                    this.state.isHighlight = 'delivery_highlight';
                }
            } else {
                this.showNotification(this.env._t("Please Select Delivery Service ",1500));
            }
        }
    }
    DeliveryTypePopup.template = 'DeliveryTypePopup';
    DeliveryTypePopup.defaultProps = {
        confirmText: _lt('Confirm'),
        cancelText: _lt('Cancel'),
        body: '',
    };

    Registries.Component.add(DeliveryTypePopup);

    return DeliveryTypePopup;
});
