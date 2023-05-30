odoo.define('aspl_pos_kitchen_screen.SyncOrderScreen', function (require) {
    'use strict';

    const { useState, useRef } = owl;
    const Registries = require('point_of_sale.Registries');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const { useListener, useAutofocus } = require("@web/core/utils/hooks");
    const { Order,Orderline } = require('point_of_sale.models');


    class SyncOrderScreen extends IndependentToOrderScreen {
        setup() {
            super.setup();
            useListener('close-screen', this._onCloseScreen);
            useListener('filter-selected', this._onFilterSelected);
            useListener('search', this._onSearch);
            useListener('cancel-order', this._onCancelOrder);
            useListener('pay-order', this._onPayOrder);
            useAutofocus({ selector: '.search input' });
            this.searchDetails = {};
            this.filter = null;
        }
        _onCloseScreen() {
            if(this.env.pos.config.is_table_management && this.env.pos.config.floor_ids &&
                this.env.pos.config.floor_ids.length > 0){
                    this.showScreen('FloorScreen');
            } else {
                this.showScreen('ProductScreen');
            }
        }
        async _onFilterSelected(event) {
            this.filter = event.detail.filter;
            this.render();
        }
        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }
        async _onCancelOrder({ detail: order }) {
            const { confirmed } = await this.showPopup('ConfirmPopup', {
                title: this.env._t('Cancel Order'),
                body: this.env._t(
                    'Would you like to cancel selected order?'
                ),
            });
            if (confirmed) {
                const { confirmed, payload: inputNote } = await this.showPopup('TextAreaPopup', {
                    startingValue: '',
                    title: this.env._t('Add Cancel Order Reason'),
                });
                await this.rpc({
                    model: 'pos.order',
                    method: 'cancel_pos_order',
                    args: [[order.order_id], inputNote]
                });
            }
        }
        async _onPayOrder({ detail: order }){
            const orderFound = this.env.pos.get_order_list().filter((posOrder) => {
                    return posOrder.server_id == order.order_id
                })
            if(orderFound.length > 0){
                this.env.pos.set_order(orderFound[0]);
                this.env.pos.selectedOrder = orderFound[0];
                this.showScreen('PaymentScreen');
            }else{
                const orderData = await this.rpc({
                    model: 'pos.order',
                    method: 'export_for_ui',
                    args: [[order.order_id]]
                });
                orderData[0].server_id = order.order_id
                let newOrder = this.env.pos.makeOrderReactive(Order.create({}, { pos: this.env.pos, json: orderData[0]}));
                if(order && order.table_id) {
                    const table = this.env.pos.tables_by_id[order.table_id];
                    newOrder.table = table || null;
                }
                this.env.pos.set_order(newOrder);
                this.env.pos.orders.add(newOrder);
                this.env.pos.selectedOrder = newOrder;
                this.showScreen('PaymentScreen');
            }
        }
        getSelectedOrderlineId() {
            return this._state.ui.selectedOrderlineIds[this._state.ui.selectedSyncedOrderId];
        }
        getFilteredOrderList() {
            const { fieldName, searchTerm } = this.searchDetails;
            const searchField = this._getSearchFields()[fieldName];
            const searchCheck = (order) => {
                if (!searchField) return true;
                const repr = searchField.repr(order);
                if (repr === null) return true;
                if (!searchTerm) return true;
                return repr && repr.toString().toLowerCase().includes(searchTerm.toLowerCase());
            };
            const predicate = (order) => {
                return searchCheck(order);
            };
            return this._getOrderList().filter(predicate);
        }
        getDate(order) {
            return moment(order.order_time).format('YYYY-MM-DD hh:mm A');
        }
        getTotal(order) {
            return this.env.pos.format_currency(order.total);
        }
        _getSearchFields() {
            var fields = {}
            fields = {
                RECEIPT_NUMBER:{
                    'repr': (order) => order.order_reference,
                    displayName: this.env._t('Receipt Number'),
                    modelField: 'order_reference',
                },
                CUSTOMER: {
                    repr: (order) => order.customer,
                    displayName: this.env._t('Customer'),
                    modelField: 'customer',
                },
            };
            return fields;
        }
        getOrderType(type){
            const orderType = {'take_away': 'Take Away', 'dine_in': 'Dine In', 'delivery': 'Delivery'};
            return orderType[type];
        }
        getSearchOrderSyncConfig() {
            return {
                searchFields: new Map(
                    Object.entries(this._getSearchFields()).map(([key, val]) => [key, val.displayName])
                ),
                filter: { show: true, options: this._getFilterOptions() },
                defaultSearchDetails: this.searchDetails,
                defaultFilter: this.filter,
            };
        }
        _getOrderList() {
            let orderList = this.props.orderSyncData;
            return this.props.orderSyncData;
        }
        _getFilterOptions() {
            const orderStates = this._getOrderStates();
            return orderStates;
        }
        _getOrderStates() {
            const states = new Map();
            states.set('ACTIVE_ORDERS', {
                text: this.env._t('All orders'),
            });
            return states;
        }
    }

    SyncOrderScreen.template = 'SyncOrderScreen';
    SyncOrderScreen.defaultProps = {
        destinationOrder: null,
        reuseSavedUIState: false,
        ui: {},
    };

    Registries.Component.add(SyncOrderScreen);

    return SyncOrderScreen;
});
