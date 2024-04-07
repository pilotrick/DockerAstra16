/** @odoo-module **/

import session from 'web.session';
//const { Component, hooks } = owl;
import { Component, onMounted, onWillUnmount, useEffect, useSubEnv, useRef, useState, xml } from "@odoo/owl";
//import { Component, onMounted, useExternalListener, useState } from "@odoo/owl";
//const { useExternalListener, useRef } = hooks;
//const { useState } = owl.hooks;
export class KitchenScreenNavbar extends Component {
    constructor(){
        super(...arguments);
    }
    get loginUser(){
        return session.name;
    }
}
KitchenScreenNavbar.template = "KitchenScreenNavbar";