/** @odoo-module **/
import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";
import { EnterpriseNavBar } from "./navbar/navbar";
import { useService } from "@web/core/utils/hooks";
import { useExternalListener, Component, onMounted, onWillUnmount, useEffect, useSubEnv, useRef, useState, xml } from "@odoo/owl";
import { useTooltip } from "@web/core/tooltip/tooltip_hook";
import { hasTouch } from "@web/core/browser/feature_detection";
const { registry } = require("@web/core/registry");
import Core from 'web.core';
import rpc from 'web.rpc';
import session from 'web.session';
const qweb = Core.qweb;
const { Component } = owl;
import  { KitchenScreenNavbar }  from "../js/KitchenScreenNavbar";
import  { backendKitchenScreen }  from "../order/BackendOrderCard";
import ajax from 'web.ajax';
export class customWebClient extends WebClient {
    setup() {
        super.setup();
        this.orderContent = useRef('order-content');
        this.kitchenScreen = useRef('kitchen-screen');
        this.state = useState({orderDate: []})
        this.env.services.bus_service.addEventListener('notification', ({ detail: notifications }) => {
            for (const { payload, type } of notifications) {
                if (type === "kitchen.order") {
                    this.state.orderData = payload.screen_display_data;
                }
            }
        });
    }

    async printOrder(){
        var res = ajax.jsonRpc("/get_pos_order_data", 'call', {
            }).then(function(result){
            });
    }

    async logOutKitchenScreen(){
        var res = this.rpc("/web/session/logout", {'type': 'http'});
    }

}
var Promise = session.user_has_group('aspl_pos_kitchen_screen_backend.group_kitchen_screen_backend');
Promise.then(function(result) {
    if (result){
        customWebClient.template = "backendKitchenScreen";
    } else {
        customWebClient.template = "web.WebClient";
    }
});
customWebClient.components = { ...WebClient.components, backendKitchenScreen,KitchenScreenNavbar};



