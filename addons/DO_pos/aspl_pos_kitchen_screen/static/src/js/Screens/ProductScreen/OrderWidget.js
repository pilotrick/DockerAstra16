odoo.define('aspl_pos_kitchen_screen.OrderWidget', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const OrderWidget = require('point_of_sale.OrderWidget');
    const models = require('point_of_sale.models');
    const { useListener } = require("@web/core/utils/hooks");
    const { useState } = owl;
    const { Orderline } = require('point_of_sale.models');

    const OrderWidgetInherit = (OrderWidget) =>
    class extends OrderWidget {
        setup() {
            super.setup();
            this.state = useState({...this.state, orderType: this.order.getOrderType()});
            useListener('delivery-OrderMode', () => this.setDeliveryMode('delivery'));
            useListener('take-away-OrderMode', () => this.setTakeAwayMode('take_away'));
            useListener('dine-in-OrderMode', () => this.setDineInMode('dine_in'));
        }
        async setDeliveryMode(OrderType) {
            this.state.orderType = OrderType;
            if(!this.order.get_partner()){
                this.showNotification(this.env._t("Please Select the Customer!",1500));
                return;
            }
            if (this.env.pos.deliveryTypes && this.env.pos.config.service_ids.length > 0) {
                let selectedDelivery = false;
                if(this.order.getDeliveryService()){
                    selectedDelivery = this.env.pos.deliveryTypeById[this.order.getDeliveryService()];
                }
                const { confirmed, payload } =
                            await this.showPopup('DeliveryTypePopup', {title: this.env._t('Delivery Services'),
                            selectedDeliveryService : selectedDelivery,
                            isDeliveryCharges: this.order.getDeliveryCharge(),
                            order: this.order});
                if (confirmed) {
                    let {user, type, charges} = payload;
                    this.state.OrderType = OrderType;
                    this.order.setDeliveryPerson(user);
                    this.order.setOrderType(OrderType);
                    this.order.setDeliveryCharge(charges ? type.charges : 0);
                    this.order.setDeliveryService(type.id);
                    const deliverProduct = this.env.pos.db.get_product_by_id
                                         (this.env.pos.config.delivery_charge_product_id[0]);
                    let orderLines = this.order.get_orderlines();
                    let flag = false;
                    const charge = charges ? type.charges : 0
                    for (let orderLine of orderLines) {
                        if (deliverProduct.id == orderLine.product.id) {
                            flag = true;
                            orderLine.set_unit_price(charge);
                            orderLine.setLineState('Done');
                            break;
                        }
                    }
                    if (!flag) {
                        let new_line = Orderline.create({}, {
                            pos: this.env.pos,
                            order: this.order,
                            product: deliverProduct,
                            price: charge,
                            price_manually_set: true,
                        });
                        new_line.set_unit_price(charge);
                        new_line.setLineState('Done');
                        this.order.add_orderline(new_line);
                    }
                }
            } else {
                 this.showNotification(this.env._t("Please select the customer first ",1500));
            }
        }
        removeDeliveryLine(){
            for (let orderLine of this.order.get_orderlines()) {
                if(orderLine.product.id === this.env.pos.config.delivery_charge_product_id[0]){
                    order.remove_orderline(orderLine);
                    break;
                }
            }
        }
        setTakeAwayMode(OrderType) {
            if(this.order.order_type === "delivery")  this.removeDeliveryLine();
            this.order.setOrderType(OrderType);
            this.state.orderType = OrderType;
        }
        setDineInMode(OrderType) {
            this.state.orderType = OrderType;
            if(this.order.order_type === "delivery") this.removeDeliveryLine();
            this.order.setOrderType(OrderType);
            this.state.OrderType = OrderType;
        }
    }
    Registries.Component.extend(OrderWidget, OrderWidgetInherit);

    return OrderWidget;
});
