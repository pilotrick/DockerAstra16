/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { useOwnDebugContext } from "@web/core/debug/debug_context";
import { registry } from "@web/core/registry";
import { DebugMenu } from "@web/core/debug/debug_menu";
import { localization } from "@web/core/l10n/localization";
import  { MainComponent }  from "../MainComponent/MainComponent";
import { Component, onMounted, onWillUnmount, useSubEnv, useRef, useState, xml } from "@odoo/owl";
import Core from 'web.core';
import rpc from 'web.rpc';
import session from 'web.session';
const qweb = Core.qweb;

import ajax from 'web.ajax';
export class customWebClient extends WebClient {
    constructor(){
        super(...arguments);
        this.userData = [];
        this.state = useState({'userObj' : []})
    }
    setup() {
        super.setup();
        this.orderContent = useRef('order-content');
        this.kitchenScreen = useRef('kitchen-screen');
    }
    async logOutKitchenScreen(){
        var res = this.rpc("/web/session/logout", {'type': 'http'});
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
}

var Promise = session.rpc('/get_user_role', {});
Promise.then(function(result) {
    customWebClient.template = result == 'cook' ?  "backendKitchenScreen" : 'web.WebClient';
});

customWebClient.components = { ...WebClient.components, MainComponent};



