odoo.define('aspl_pos_kitchen_screen.Orderline', function(require) {
    'use strict';

    const OrderLine = require('point_of_sale.Orderline');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    const OrderLineInherit = OrderLine =>
        class extends OrderLine {
            get addStateColor(){
                const highlightClass = {'Waiting': '#555555', 'Preparing': '#f44336', 'Delivering': '#795548'}
                if(Object.keys(highlightClass).includes(this.props.line.state)){
                    return highlightClass[this.props.line.state];
                }
            }
            displayNotification(message){
                return this.showNotification(this.env._t(message), 1500);
            }
            async deleteOrderLine(order, line, vals){
                 const removeOrderLine = await  this.rpc({
                    model: 'pos.order.line',
                    method: 'remove_order_line',
                    args: [[line.server_id], vals],
                })
                if(removeOrderLine){
                    this.showNotification(this.env._t(`${line.product.display_name} Deleted!`, 1500));
                     line.set_quantity('remove');
                     await this.env.pos.push_orders(order, {draft:true});
                }
            }
            async DeleteLineFromOrder(){
                let order = this.env.pos.get_order();
                const line = this.props.line;
                const {delete_order_line_reason, is_delete_order_line} = this.env.pos.user;
                 let removeLineObj = {
                                    'product_id': line.product.id,
                                    'reason_id': '',
                                    'description': ''
                                }
                if(is_delete_order_line){
                    if(delete_order_line_reason && !this.env.pos.removeProductReason.length){
                        return this.showNotification(this.env._t("No predefined Remove Product Reason Found!, <br/>goto Point of Sale->Orders->Remove Product Reason",1500));
                    }
                    const reasonList = [...this.env.pos.removeProductReason].map(item => {
                                                                    return {id: item.id, label: item.name, item: item};
                                                                });
                    const { confirmed, payload: selectedReason } = await this.showPopup('SelectionPopup', {
                                                                            title: this.env._t('Select Reason'),
                                                                            list: reasonList });
                    if (confirmed) {
                        removeLineObj.reason_id = selectedReason.id;
                        if (selectedReason.description){
                            const { confirmed, payload: inputNote } = await this.showPopup('TextAreaPopup', {
                                title: this.env._t('Add Description'),
                            });
                            if (confirmed) {
                                removeLineObj.description = inputNote;
                            }
                        }
                        const removeOrderLineBackend = await this.deleteOrderLine(order, line, removeLineObj);
                    }
                }else{
                    removeLineObj
                    const removeOrderLineBackend = await this.deleteOrderLine(order, line, removeLineObj);
                }
            }
        };

    Registries.Component.extend(OrderLine, OrderLineInherit);

    return OrderLine;
});
