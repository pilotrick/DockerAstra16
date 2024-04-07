odoo.define('pos_sync_restaurant', function(require){

    const FloorScreen = require('pos_restaurant.FloorScreen');

    const { PosGlobalState, Order, Orderline, Payment,Product } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const TicketButton = require('pos_restaurant.TicketButton');




    const PosRSyncPosGlobalState = (PosGlobalState) => class PosRSyncPosGlobalState extends PosGlobalState {
        update_the_order(sync_order){
            var self = this;
            if (sync_order.table_id) {
                this.table = self.tables_by_id[sync_order.table_id];
            }
            var order = super.update_the_order(...arguments);
            if (sync_order.table_id) {
                order.tableId = sync_order.table_id;
                order.table = self.tables_by_id[sync_order.table_id];
                order.customerCount = sync_order.customer_count;
            }
            return order; 
        }
        unsetTable() {
            // this._syncTableOrdersToServer();
            this.table = null;
            this.set_order(null);
        }
        async setTable(table, orderUid=null) {
            this.table = table;
            // try {
            //     this.loadingOrderState = true;
            //     await this._syncTableOrdersFromServer(table.id);
            // } catch (error) {
            //     throw error;
            // } finally {
                this.loadingOrderState = false;
                const currentOrder = this.getTableOrders(table.id).find(order => orderUid ? order.uid === orderUid : !order.finalized);
                if (currentOrder) {
                    this.set_order(currentOrder);
                } else {
                    this.add_new_order();
                }
            // }
        }
    async transferTable(table) {
        var self = this;
        this.table = table;
        // try {
        //     this.loadingOrderState = true;
        //     await this._syncTableOrdersFromServer(table.id);
        // } catch (error) {
        //     throw error;
        // } finally {
            this.loadingOrderState = false;
            this.orderToTransfer.tableId = table.id;
            this.set_order(this.orderToTransfer);
            this.transferredOrdersSet.add(this.orderToTransfer);
            this.orderToTransfer = null;
            setTimeout(function(){
                self.transfer_data({'action':'update_order','order':self.get_order().export_as_JSON()});
            }, 100);
        // }
    }
    }

    Registries.Model.extend(PosGlobalState, PosRSyncPosGlobalState);

    const PosRSyncOrderline = (Orderline) => class PosRSyncOrderline extends Orderline {
        get_line_diff_hash(){
            if(this.extra_id != undefined){
                return '' + this.extra_id;
            }
            else if(this.extra_id != undefined && this.get_note()){
                return this.extra_id + '|' + this.get_note();
            }
            else if (this.get_note()) {
                return this.id + '|' + this.get_note();
            } else {
                return '' + this.id;
            }
        }
    }
    Registries.Model.extend(Orderline, PosRSyncOrderline);

    const PosRSyncOrder = (Order) => class PosRSyncOrder extends Order {
            setCustomerCount(count) {
                var self = this;
                super.setCustomerCount(...arguments);
                setTimeout(function(){
                    self.pos.transfer_data({'action':'update_order','order':self.export_as_JSON()});
                }, 500);
                
            }
            hasSkippedChanges() {
                if(this.orderlines){
                    var orderlines = this.get_orderlines();
                    if(orderlines != null){
                        for (var i = 0; i < orderlines.length; i++) {
                            if (orderlines[i].mp_skip) {
                                return true;
                            }
                        }
                    }
                }
                return false;
            }
    }
    Registries.Model.extend(Order, PosRSyncOrder);

    const PosRSyncFloorScreen = (FloorScreen) =>
        class extends FloorScreen {
        onMounted() {
            if (this.env.pos.table) {
                this.env.pos.unsetTable();
            }
            this.env.posbus.trigger('start-cash-control');
            this.floorMapRef.el.style.background = this.state.floorBackground;
            this.state.floorMapScrollTop = this.floorMapRef.el.getBoundingClientRect().top;
            // call _tableLongpolling once then set interval of 5sec.
            // this._tableLongpolling();
            // this.tableLongpolling = setInterval(this._tableLongpolling.bind(this), 5000);
        }
    }
    Registries.Component.extend(FloorScreen, PosRSyncFloorScreen);

const PosResSTicketButton = (TicketButton) =>
        class extends TicketButton {
            async onClick() {
                // if (this.env.pos.config.iface_floorplan && !this.props.isTicketScreenShown && !this.env.pos.table) {
                //     try {
                //         this.env.pos.setLoadingOrderState(true);
                //         await this.env.pos._syncAllOrdersFromServer();
                //     } catch (error) {
                //         if (isConnectionError(error)) {
                //             await this.showPopup('OfflineErrorPopup', {
                //                 title: this.env._t('Offline'),
                //                 body: this.env._t('Due to a connection error, the orders are not synchronized.'),
                //             });
                //         } else {
                //             this.showPopup('ErrorPopup', {
                //                 title: this.env._t('Unknown error'),
                //                 body: error.message,
                //             });
                //         }
                //     } finally {
                //         this.env.pos.setLoadingOrderState(false);
                //         this.showScreen('TicketScreen');
                //     }
                // } else {
                //     super.onClick();
                // }
                this.showScreen('TicketScreen');
            }
            /**
             * If no table is set to pos, which means the current main screen
             * is floor screen, then the order count should be based on all the orders.
             */
            get count() {
                if (!this.env.pos || !this.env.pos.config) return 0;
                if (this.env.pos.config.iface_floorplan && this.env.pos.table) {
                    return this.env.pos.getTableOrders(this.env.pos.table.id).length;
                } else {
                    return super.count;
                }
            }
        };

    Registries.Component.extend(TicketButton, PosResSTicketButton);
});
