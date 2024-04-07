odoo.define('aspl_pos_kitchen_screen.Chrome', function(require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useListener } = require("@web/core/utils/hooks");
    const { Gui } = require('point_of_sale.Gui');
    const { EventBus, onWillStart, useState, onMounted, onPatched, onRendered , useSubEnv} = owl;


    const AsplKitchenChrome = (Chrome) =>
        class extends Chrome {
            async start(){
                await super.start();
                this.state.orderData = this.env.pos.kitchenScreenData;
                this.state.orderSyncData = this.env.pos.orderSyncData;
                this.orderList = this.env.pos.get_order_list();
            }
            setup() {
                super.setup();
                this.state.orderData = [];
                this.state.orderSyncData = [];
                this.orderList = [];
                useListener('click-kitchen-screen', this._clickKitchenScreen);
                useListener('click-sync-order-screen', this._clickSyncOrderScreen);
                this.env.services.bus_service.addEventListener('notification', ({ detail: notifications }) => {
                    for (const { payload, type } of notifications) {
                        if (type === "kitchen.order") {
                            let kitchenOrders = payload.order_data;
                            let syncOrderList = kitchenOrders.filter((order)=> order.state == 'draft');;
                            let orderData = [];
                            let allOrderLine = {};
                            for(let order of kitchenOrders) {
                                order.order_lines = order.order_lines.filter(function(line) {
                                    allOrderLine[line.id] = line.state;
                                    return !_.contains(['Done','Cancel'], line.state);
                                });
                                if(order.order_lines.length > 0){
                                    orderData.push(order)
                                }
                             }
                            this.state.orderData = orderData;
                            this.state.orderSyncData = syncOrderList;
                            if(allOrderLine){
                                this.updatePosScreenOrder(allOrderLine);
                            }
                        }else if(type === 'kitchen.order.remove'){
                            let orderList = this.orderList
                            for(let order of orderList){
                                if(order && payload.order_id == order.server_id){
                                    if(['delete', 'cancel'].includes(payload.is_remove)){
                                        order.server_id = false;
                                        this.env.pos.removeOrder(order)
                                    }
                                }
                            }
                        }else if(type === 'remove.pos.order'){
                            const orderList = this.env.pos.get_order_list();
                            for(let order of orderList) {
                                if(order.server_id && order.server_id === payload.server_id){
                                  this.env.pos.removeOrder(order);
                                  this.showNotification(this.env._t(`Paid : ${order.name}}`));
                                  break;
                                }
                            }
                        }
                    }
                });
            }
            updatePosScreenOrder(orderLineDate){
                let orderList = this.orderList;
                for(let order of orderList){
                    if(order && order.server_id){
                        for(let line of order.orderlines){
                            if(line && line.server_id && orderLineDate[line.server_id]){
                                line.setLineState(orderLineDate[line.server_id]);
                            }
                        }
                    }
                }
            }
            get isTicketButtonShown(){
                return this.mainScreen.name !== 'KitchenScreen';
            }
            get isKitchenScreen(){
                return this.mainScreen.name === 'KitchenScreen';
            }
            get currentScreenName(){
                return this.mainScreen.name;
            }
            get isManager(){
                if(this.env.pos.config.is_table_management && this.env.pos.config.floor_ids &&
                    this.env.pos.config.floor_ids.length > 0){
                    if(this.mainScreen.name === 'FloorScreen' || this.mainScreen.name === 'KitchenScreen'){
                        return this.env.pos.user.kitchen_screen_user === 'manager';
                    }
                } else {
                    return this.env.pos.user.kitchen_screen_user === 'manager';
                }
            }
            _clickSyncOrderScreen(){
                this.showScreen('SyncOrderScreen');
            }
            _clickKitchenScreen(){
                if(this.mainScreen.name === 'KitchenScreen'){
                    if(this.env.pos.config.is_table_management && this.env.pos.config.floor_ids &&
                        this.env.pos.config.floor_ids.length > 0){
                            Gui.showScreen('FloorScreen');
                    } else {
                        Gui.showScreen('ProductScreen');
                    }
                } else{
                    Gui.showScreen('KitchenScreen', {orderData: this.env.pos.kitchenScreenData});
                }
            }
        };

    Registries.Component.extend(Chrome, AsplKitchenChrome);

    return Chrome;
});