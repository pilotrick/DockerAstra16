odoo.define('aspl_pos_kitchen_screen.OrderCardLine', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const { nextFrame } = require('point_of_sale.utils');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef } = owl;
    const { renderToString } = require('@web/core/utils/render');

    class OrderCardLine extends PosComponent {
        setup() {
            super.setup();
        }
        async clickLineState(){
            if(this.props.line.state == 'Waiting'){
                this.props.line.state = 'Preparing';
            }else if(this.props.line.state == 'Preparing'){
                this.props.line.state = 'Delivering';
            }else if(this.props.line.state == 'Delivering'){
                this.props.line.state = 'Done';
            }
            await this.rpc({
                model: 'pos.order.line',
                method: 'update_orderline_state',
                args: [{'state': this.props.line.state,
                        'order_line_id':this.props.line.id,
                        'order_id': this.props.line.order_id}],
            });
            this.trigger('click-line-state')
        }
        get textStyle(){
            if(this.props.line.state == 'Delivering'){
                return 'line-through'
            }
        }
        async printLine(){
            if (this.env.proxy.printer) {
                const report = renderToString('OrderLinePrint',
                    Object.assign({
                        line: this.props.line,
                        order: this.props.order,
                    })
                );
                const printResult = await this.env.proxy.printer.print_receipt(report);
                if (printResult.successful) {
                    return true;
                } else {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: printResult.message.title,
                        body: 'Do you want to print using the web printer?',
                    });
                    if (confirmed) {
                        await nextFrame();
                    }
                    return false;
                }
            }
        }
    }
    OrderCardLine.template = 'OrderCardLine';

    Registries.Component.add(OrderCardLine);

    return OrderCardLine;
});
