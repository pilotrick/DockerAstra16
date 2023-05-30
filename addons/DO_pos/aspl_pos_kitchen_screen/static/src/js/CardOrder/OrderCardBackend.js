/** @odoo-module **/
/* global html2canvas */
import session from 'web.session';
import { Component } from "@odoo/owl";
import { OrderCardLineBackend } from "./OrderCardLineBackend";
const { useListener } = require("@web/core/utils/hooks");
var Session = require('web.Session');
var rpc = require('web.rpc');
var devices = require('aspl_pos_kitchen_screen.devices');
import { useService } from "@web/core/utils/hooks";
const { renderToString } = require('@web/core/utils/render');
var EpsonPrinter = require('aspl_pos_kitchen_screen.printerEpson');

export class OrderCardBackend extends Component {
    setup(){
        super.setup();
        this.orm = useService("orm");
        this.proxy = new devices.ProxyDevice(this);
        this.proxy.connect_to_printer();
    }
    get headerClass(){
        return '#8bc34a';
    }
    get imageUrl() {
        if(this.props.order.order_type == 'dine_in'){
            return `/aspl_pos_kitchen_screen/static/src/img/table.png`;
        }else if(this.props.order.order_type == 'take_away'){
            return `/aspl_pos_kitchen_screen/static/src/img/takeaway_kitchen.png`;
        }else if(this.props.order.order_type == 'delivery'){
            return `/aspl_pos_kitchen_screen/static/src/img/delivery_kitchen.png`;
        }
    }
    get orderStateColor(){
        if(this.props.order.order_state == 'Start'){
            return '#4CAF50';
        }else if(this.props.order.order_state == 'Done'){
            return '#03a9f4';
        }else if(this.props.order.order_state == 'Deliver'){
            return '#795548';
        }
    }
    async userInfo(user_id){
         return await this.orm.call("res.users", "read", [user_id, ['selection_printer','iotbox_ip_address','network_ip_address']], {});
    }
    async printOrder(){
        const report = renderToString('OrderPrint',
            Object.assign({
                order: this.props.order
            })
        );
        let UserInfo = await this.userInfo(session.user_id);
        if(UserInfo && UserInfo.length > 0){
            if(UserInfo[0].selection_printer == 'iot_box'){
                let image = await this.htmlToImg(report);
                this.connection = new Session(undefined, UserInfo[0].iotbox_ip_address, { use_cors: true});
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
            } else {
                alert("Please set printer configuration !");
            }
        } else{
            alert("Please set printer configuration !");
        }
    }
    async htmlToImg(receipt) {
        $('.pos-receipt-print').html(receipt);
        this.receipt = $('.pos-receipt-print>.pos-receipt');
        this.receipt.parent().css({ left: 0, right: 'auto' });
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
}
OrderCardBackend.template = "OrderCardBackend";
OrderCardBackend.components = {OrderCardLineBackend};
