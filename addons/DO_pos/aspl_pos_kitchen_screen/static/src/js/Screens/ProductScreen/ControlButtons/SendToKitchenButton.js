odoo.define('aspl_pos_kitchen_screen.SendToKitchenButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class SendToKitchenButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick(){
            var selectedOrder = this.env.pos.get_order();
            selectedOrder.initialize_validation_date();
            if(selectedOrder.is_empty()){
                this.showNotification('Please select product!!');
            }else{
                try{
                    selectedOrder.set_send_to_kitchen(true);
                    const orderLinesState = _.pluck(selectedOrder.orderlines, 'state');
                    let orderState;
                    if(orderLinesState.includes('Waiting')){
                        orderState = 'Start';
                    }else if(orderLinesState.includes('Preparing')){
                        orderState = 'Done';
                    }else if(orderLinesState.includes('Delivering')){
                        orderState = 'Deliver';
                    }else if(orderLinesState.includes('Done')){
                        orderState = 'Complete';
                    }
                    selectedOrder.set_order_state(orderState);
                    var orderId = await this.env.pos.push_orders(selectedOrder, {draft:true});
                    selectedOrder.setServerId(orderId[0].id);
                    let orderLineIds = await this.orderLineIds(orderId[0].id);
                    for(var line of selectedOrder.get_orderlines()){
                        for(var lineID of orderLineIds){
                            if(line.cid === lineID.line_cid || line.server_id == lineID.server_id){
                                line.setServerId(lineID.id);
                                line.setLineState(lineID.state);
                            }
                        }
                    }
                } catch(ex){
                    console.warn('Order Not Send, Please check your network connection!');
                }
            }
        }
        orderLineIds(orderId){
            return this.rpc({
                model: 'pos.order.line',
                method: 'search_read',
                fields: ['line_cid', 'state'],
                domain: [['order_id', '=', orderId]]
            })
        }
    }
    SendToKitchenButton.template = 'SendToKitchenButton';

    ProductScreen.addControlButton({
        component: SendToKitchenButton,
        condition: function() {
            return ['manager', 'waiter'].includes(this.env.pos.user.kitchen_screen_user)  &&
                   this.env.pos.config.restaurant_mode == 'full_service';
        },

    });

    Registries.Component.add(SendToKitchenButton);

    return SendToKitchenButton;
});
