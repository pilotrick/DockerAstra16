/** @odoo-module **/
import session from 'web.session';
import { Component, useRef, useState, onWillStart} from "@odoo/owl";
import  { KitchenScreenNavbar }  from "./KitchenScreenNavbar";
import  { OrderCardBackend } from "../CardOrder/OrderCardBackend";
import { useService } from "@web/core/utils/hooks";



export class MainComponent extends Component {
    setup(){
        super.setup(...arguments);
        this.state = useState({'orderData': []})
        this.posCategories = [];
        this.orderContent = useRef('order-content');
        this.kitchenScreen = useRef('kitchen-screen');
        this.orm = useService("orm");
        onWillStart(this.onWillStart);
        this.env.services.bus_service.addEventListener('notification', ({ detail: notifications }) => {
            for (const { payload, type } of notifications) {
                if (type === "kitchen.order") {
                    this.loadKitchenRecords(payload.order_data);
                }
            }
        });
    }
    loadKitchenRecords(kitchenData){
        var orderData = [];
        for (let order of kitchenData){
            order.order_lines = order.order_lines.filter((line) => !_.contains(['Done','Cancel'], line.state) && _.contains(this.posCategories, line.categ_id));
            if(order.order_lines.length > 0){
                orderData.push(order);
            }
        }
        this.state.orderData = orderData;
    }
    async onWillStart() {
        let posOrderData = await this.orm.call("pos.order", "get_broadcast_data", [], {});
        const [posCategories] = await this.orm.call("res.users", "read", [session.uid, ['pos_category_ids']], {})
        this.posCategories = posCategories.pos_category_ids
        this.loadKitchenRecords(posOrderData);
    }
    clickLeft(){
        this.orderContent.el.scrollLeft -= 330;
    }
    clickRight(){
        this.orderContent.el.scrollLeft += 330;
    }
    clickDoubleLeft(){
        this.orderContent.el.scrollLeft -= 1200;
    }
    clickDoubleRight(){
        this.orderContent.el.scrollLeft += 1200;
    }
    clickTopLeft(){
        this.kitchenScreen.el.scrollTop = 0;
        this.orderContent.el.scrollLeft = 0;
    }
    clickTopRight(){
        this.orderContent.el.scrollLeft = this.orderContent.el.scrollWidth;
        this.kitchenScreen.el.scrollTop = this.kitchenScreen.el.scrollTop;
    }
    async loginUserObject(){
        return await session.rpc('/get_pos_order_data', {});
    }
}
MainComponent.template = "MainComponent";
MainComponent.components = {KitchenScreenNavbar, OrderCardBackend};