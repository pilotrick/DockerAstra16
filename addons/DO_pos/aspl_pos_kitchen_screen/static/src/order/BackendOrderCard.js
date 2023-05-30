/** @odoo-module **/
import { WebClient } from "@web/webclient/webclient";
import { Component, onMounted, onWillUnmount, useEffect, useSubEnv, useRef, useState, xml } from "@odoo/owl";
//const { Component, hooks } = owl;
//const { useListener } = require('web.custom_hooks');
import  { KitchenScreenNavbar }  from "../js/KitchenScreenNavbar";
export class backendKitchenScreen extends Component {
    setup() {
    }
}
backendKitchenScreen.template = 'backendKitchenScreen';
backendKitchenScreen.components = {KitchenScreenNavbar};