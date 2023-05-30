/** @odoo-module **/
/* global html2canvas */
import session from 'web.session';
import { Component, onMounted, onWillUnmount, useEffect, useSubEnv, useRef, useState, xml } from "@odoo/owl";

var Session = require('web.Session');
var rpc = require('web.rpc');
import { useService } from "@web/core/utils/hooks";
var devices = require('aspl_pos_kitchen_screen.devices');
const { renderToString } = require('@web/core/utils/render');
var EpsonPrinter = require('aspl_pos_kitchen_screen.printerEpson');


export class OrderCardLineBackend extends Component {

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.proxy = new devices.ProxyDevice(this);
        this.proxy.connect_to_printer();
    }
    async clickLineState(){
        const lineState = {'Waiting':'Preparing', 'Preparing': 'Delivering', 'Delivering':'Done'};
        this.props.line.state = lineState[this.props.line.state]
        await this.orm.call("pos.order.line",
            "update_orderline_state", [{'state': this.props.line.state,
                                        'order_line_id':this.props.line.id,
                                        'order_id': this.props.line.order_id}], {});
    }
    get textStyle(){
        if(this.props.line.state == 'Delivering'){
            return 'line-through'
        }
    }
    async htmlToImg(receipt) {
        $('.pos-receipt-print').html(receipt);
        this.receipt = $('.pos-receipt-print>.pos-receipt');
        this.receipt.parent().css({ left: 0, right: 'auto'});
        return html2canvas(this.receipt[0], {
            height: Math.ceil(this.receipt.outerHeight() + this.receipt.offset().top),
            width: Math.ceil(this.receipt.outerWidth() + 2 * this.receipt.offset().left),
            scale: 1,
        }).then(canvas => {
            $('.pos-receipt-print').empty();
            return this.process_canvas(canvas);
        });
    }
    process_canvas(canvas) {
        return canvas.toDataURL('image/jpeg').replace('data:image/jpeg;base64,','');
    }
    async userInfo(user_id){
         return await this.orm.call("res.users", "read", [user_id, ['selection_printer','iotbox_ip_address','network_ip_address']], {});
    }
    async printLine(){
        const report = renderToString('OrderLinePrint',
            Object.assign({
                line: this.props.line,
                order: this.props.order,
            })
        );
        let UserInfo = await this.userInfo(session.user_id);
        if(UserInfo && UserInfo.length > 0){
            const {selection_printer, network_ip_address,  iotbox_ip_address} = UserInfo[0]
            if(UserInfo[0].selection_printer == 'iot_box'){
                let image = await this.htmlToImg(report);
                this.connection = new Session(undefined, iotbox_ip_address, { use_cors: true});
                return this.connection.rpc('/hw_proxy/default_printer_action', {
                    data: {
                        action: 'print_receipt',
                        receipt: image,
                    }
                });
            } else if(UserInfo[0].selection_printer == 'network'){
                this.proxy.printer = new EpsonPrinter(UserInfo[0].network_ip_address , this);
                const printResult = await this.proxy.printer.print_receipt(report);
                if (!printResult.successful) {
                    console.log("\n Title",printResult.message.title)
                    console.log("\n\n Message",printResult.message.body)
                }
            }
        } else{
            alert("Please set printer configuration !");
        }
    }
}
OrderCardLineBackend.template = "OrderCardLineBackend";
