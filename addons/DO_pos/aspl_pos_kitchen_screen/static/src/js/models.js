odoo.define('aspl_pos_kitchen_screen.models', function (require) {
    "use strict";

    var { PosGlobalState, Order, Orderline, Payment } = require('point_of_sale.models');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;
    var utils = require('web.utils');
    var session = require('web.session');
    var round_pr = utils.round_precision;
    var QWeb = core.qweb;

    const Registries = require('point_of_sale.Registries');

    const PosAsplKitchenScreenGlobalState = (PosGlobalState) => class PosAsplKitchenScreenGlobalState extends PosGlobalState {
        constructor(obj) {
            super(obj);
            this.kitchenScreenData = [];
            this.orderSyncData = [];
            this.deliveryTypeById = {};
            this.deliveryUserById = {};
        }
        async _processData(loadedData) {
            await super._processData(...arguments);
            this.removeProductReason = loadedData['remove.product.reason'];
            this.pos_order_ids = loadedData['pos.order'];
            let kitchenOrderList = [];
            let kitchenData = await loadedData['kitchen.data'];
            for(let order of kitchenData) {
                order.order_lines = order.order_lines.filter((line) => !_.contains(['Done','Cancel'], line.state));
                if(order.order_lines.length > 0){
                    kitchenOrderList.push(order);
                }
            }
            this.kitchenScreenData = kitchenOrderList;
            this.orderSyncData = kitchenData.filter((order)=> order.state == 'draft');
            this.deliveryTypes = await loadedData['delivery.type'];
            this.deliveryUsers = await loadedData['delivery.users'];
            if(this.deliveryTypes){
                for(let type of this.deliveryTypes){
                    this.deliveryTypeById[type.id] = type;
                }
                for(let user of this.deliveryUsers){
                    this.deliveryUserById[user.id] = user;
                }
            }
        }
        set_kitchen_screen_data(data){
            this.kitchenScreenData = data;
        }
        get_kitchen_screen_data(){
            return this.kitchenScreenData;
        }
    }
    Registries.Model.extend(PosGlobalState, PosAsplKitchenScreenGlobalState);

    const asplKitchenScreenOrder = (Order) => class asplKitchenScreenOrder extends Order {
        constructor(obj, options) {
            super(...arguments);
            this.server_id = this.server_id || false;
            this.waiter_id = this.waiter_id || false;
            this.send_to_kitchen = this.send_to_kitchen || false;
            this.order_state = this.order_state || 'Start';
            this.is_from_sync_screen = this.is_from_sync_screen || false;
            this.orderType = this.orderType || this.pos.config.default_delivery_type;
            this.deliveryBy = this.deliveryBy || false;
            this.deliveryService = this.deliveryService || false;
            this.deliveryCharges = this.deliveryCharges || false;
        }
        set_waiter_id(waiter){
            this.waiter_id = waiter;
            this.trigger('change', this);
        }
        get_waiter_id(){
            return this.waiter_id;
        }
        set_order_state(state){
            this.order_state = state;
        }
        get_order_state(){
            return this.order_state;
        }
        set_send_to_kitchen(flag){
            this.send_to_kitchen = flag;
        }
        get_send_to_kitchen(){
            return this.send_to_kitchen;
        }
        setServerId(server_id){
            this.server_id = server_id;
        }
        getServerId(){
            return this.server_id;
        }
        setOrderType(type) {
            this.orderType = type;
        }
        getOrderType() {
            return this.orderType;
        }
        setDeliveryCharge(charges) {
            this.deliveryCharges = charges;
        }
        getDeliveryCharge() {
            return this.deliveryCharges;
        }
        setDeliveryPerson(deliveredBy) {
            this.deliveryBy = deliveredBy;
        }
        getDeliveryPerson() {
            return this.deliveryBy;
        }
        setDeliveryService(service) {
            this.deliveryService = service;
        }
        getDeliveryService() {
            return this.deliveryService;
        }
        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            this.send_to_kitchen = json.send_to_kitchen;
            this.server_id = json.server_id;
            this.waiter_id = json.waiter_id;
            this.order_state = json.order_state;
            this.is_from_sync_screen = json.is_from_sync_screen;
            this.orderType = json.order_type ? json.order_type : json.orderType;
            this.deliveryBy = json.deliver_by ? json.deliver_by[0] : json.deliveryBy;
            this.deliveryService = json.delivery_service ? json.delivery_service[0] : json.deliveryService;
            this.deliveryCharges = json.deliveryCharges;
        }
        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.send_to_kitchen = this.send_to_kitchen || false;
            json.server_id = this.server_id;
            json.waiter_id = this.waiter_id;
            json.order_state = this.order_state;
            json.is_from_sync_screen = this.is_from_sync_screen;
            json.orderType = this.orderType;
            json.deliveryService = this.deliveryService;
            json.deliveryBy = this.deliveryBy;
            json.deliveryCharges = this.deliveryCharges;
            return json;
        }
        export_for_printing() {
            const json = super.export_for_printing(...arguments);
            const type = {'take_away': 'Take Away',
                          'dine_in': 'Dine In',
                          'delivery': 'Delivery'}
            json.orderType = this.getOrderType();
            json.deliveryService = this.deliveryService ? this.pos.deliveryTypeById[this.deliveryService]: false;
            json.deliveryBy = this.deliveryBy ? this.pos.deliveryUserById[this.deliveryBy] : false;
            json.deliveryCharges = this.deliveryCharges;
            json.orderTitle = type[this.getOrderType()]
            return json;
        }
    }
    Registries.Model.extend(Order, asplKitchenScreenOrder);

    const asplKitchenScreenOrderLine = (Orderline) => class asplKitchenScreenOrderLine extends Orderline {
        constructor(obj, options) {
            super(...arguments);
            this.state = this.state || 'Waiting';
            this.server_id = this.server_id || false;
            this.line_cid = this.cid || false;
            return this;
        }
        setLineState(state) {
            this.state = state;
        }
        getLineState(){
            return this.state;
        }
        setServerId(server_id){
            this.server_id = server_id;
        }
        getServerId(server_id){
            return this.server_id;
        }
        clone(){
            const orderline = super.clone(...arguments);
            orderline.state = this.state;
            orderline.server_id = this.server_id;
            orderline.line_cid = this.line_cid;
            return orderline;
        }
        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            this.server_id = json.server_id;
            this.line_cid = json.line_cid;
            this.state = json.state;
        }
        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.state = this.state;
            json.server_id = this.server_id;
            json.line_cid = this.line_cid;
            return json;
        }
        can_be_merged_with(orderline) {
            if (this.state != orderline.state){
                return false
            }else {
                return super.can_be_merged_with(...arguments);
            }
        }
    }

    Registries.Model.extend(Orderline, asplKitchenScreenOrderLine);
});