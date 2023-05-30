odoo.define('pos_sync_order', function(require){

    var { busService } = require('@bus/services/bus_service');
    var Session = require('web.Session');
    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    var PosDB = require('point_of_sale.DB');
    var session = require('web.session');
    var utils = require('web.utils');
    var field_utils = require("web.field_utils");
    var round_pr = utils.round_precision;
    const { PosGlobalState, Order, Orderline, Payment,Product,Packlotline } = require('point_of_sale.models');
    var { Gui } = require('point_of_sale.Gui');
    var token_remove = true;
    var test_varialbe = true;

    const SyncChrome = (Chrome) =>
    class extends Chrome {
        constructor() {
            super(...arguments);
        }

        async start(){
            
            await super.start();
            await this._poolData();
            var self = this;
            setTimeout(function(){
                if(self.env.pos.config && self.env.pos.config.wv_session_id){                    
                    var list_orders = self.env.pos.get_order_list();
                    while(list_orders.length > 0){
                        self.env.pos.removeOrder(list_orders[0]);
                    }
                    // if(self.env.pos.table){
                    //     self.showScreen('show-main-screen', {name:'FloorScreen', props:{ floor: self.env.pos.table.floor } });

                    //     // self.trigger('show-main-screen', {name:'FloorScreen', props:{ floor: self.env.pos.table.floor } });
                    // }
                     self.env.pos.transfer_data({'action':'sync_all_orders','order':self.env.pos.config.id});
                }
            },1000);
        }

        _poolData(){
            this.env.services['bus_service'].addChannel('pos_sync_session');
            this.env.services['bus_service'].addEventListener('notification', this._onNotification.bind(this));
        }

        _onNotification(notifications){
            var self = this.env.pos;
            for (var detail of notifications.detail) {
                       

                if(detail.type == "pos_sync_session"){

                    // if(message.type == 'product'){
                    // }
                // if(! self.config.allow_incoming_orders){
                //     return
                // }
                var message = detail.payload;                
                // var channel_name = "pos_sync_session";
                // if(self.config.pos_kitchen_view){
                //     if(message['action']=="update_order"){
                //         var all_data = self.pos_kitchen_data;
                //         var p_tok = true;
                //         for(var i=0;i<all_data.length;i++){
                //             if(all_data[i].uid == message['order'].uid){
                //                 p_tok = false;
                //                 self.pos_kitchen_data[i] = message['order'];
                //             }
                //         }
                //         if(p_tok){
                //             self.pos_kitchen_data.push(message['order']);
                //         }
                //         self.gui.show_screen('kitchen_screen',{},'refresh');
                //     }
                //     else if(message['action']=="remove_order"){
                //         var all_data = self.pos_kitchen_data;
                //         for(var i=0;i<all_data.length;i++){
                //             if(all_data[i].uid == message['order']){
                //                 self.pos_kitchen_data.splice(i, 1);
                //             }
                //         }
                //         self.gui.show_screen('kitchen_screen',{},'refresh');
                //     }
                // }
                // else{
                if(message.type == "res_partner"){
                     self.db.add_partners(message.data);
                }
                if(message.type == 'product'){
                    if(message.data.action=="update_order"){
                        // console.log("Tesing>>>>>>>>>>>>>>>>>>>>>",message.order);
                        self.update_the_order(message.data.order);
                    }
                    else if(message.data.action=="remove_order"){
                        var order = self.get_order_list().find(function(ord){
                            return ord.uid == message.data.order;
                        });
                        if(order){
                            
                            if (order === self.get_order()) {
                                if(this.env.pos.table){
                                    this.trigger('show-main-screen', {name:'FloorScreen', props:{ floor: this.env.pos.table.floor } });
                                }
                                else{                                
                                    const currentOrderIndex = self.get_order_list().indexOf(order);
                                    var orderList = self.get_order_list();
                                    this.env.pos.set_order(orderList[currentOrderIndex+1] || orderList[currentOrderIndex-1]);
                                }
                            }
                            this.env.pos.removeOrder(order);
                        }
                    }

                }
                }
                
            }
        }
    }

    Registries.Component.extend(Chrome, SyncChrome);

    const PosSyncPosGlobalState = (PosGlobalState) => class PosSyncPosGlobalState extends PosGlobalState {
        constructor(obj) {
            super(obj);
            this.connection = new Session();
            this.allow_remove_sync = false;
        }
        removeOrder(order) {
            super.removeOrder(...arguments);
            if(this.config.wv_session_id && this.allow_remove_sync){
                this.transfer_data({'action':'remove_order','order':order.uid});
            }
        }
        async transfer_data(data){
            var self = this;
            // 
            await this.connection.rpc('/pos_sync_session/',{
                        session_id: self.config.wv_session_id[0],
                        order: data,
                        pos_config_id:self.config.id,
            }).then(function(results){
                    if(typeof results === "object"){
                        if(results['action']=='sync_all_orders'){
                            if(results['order'].length >0){
                                _.each(results['order'], function(res){
                                    self.update_the_order(res['order']);
                                });
                            }
                        }
                    }
                    self.allow_remove_sync = true;
            },
            function (error, e) {
                // e.preventDefault();
                console.log("Please Check your Internet Connection.")
            });
        // }
        }
        update_the_order(sync_order){
            var self = this;

            if(!self.config.allow_incoming_orders)
                return;
            var order = this.get_order_list().find(function(ord){
                return ord.uid == sync_order.uid;
            });
            if (!order){
                var sequence_number = sync_order.sequence_number;
                if (sequence_number == self.pos_session.sequence_number){
                } else if (sequence_number > self.pos_session.sequence_number){
                self.pos_session.sequence_number = sequence_number;
                }
                order = this.createReactiveOrder();
                order.uid = sync_order.uid;
    
                var current_order = self.get_order();
                self.get_order_list().add(order);
                // self.set('selectedOrder', current_order);
                // self.selectedOrder = current_order;
                self.set_order(current_order);
                $('.with-badge').attr("badge",self.env.pos.get_order_list().length);
            }
            order.wv_partner_id = sync_order.wv_partner_id;
            order.order_c_date = sync_order.order_c_date;
            order.order_priority = sync_order.order_priority;
            order.sequence_number = sync_order.sequence_number;
            order.session_short_name = sync_order.session_short_name;
            order.wait_customer = false;
            if(sync_order.multiprint_resume){
                order.saved_resume =  JSON.parse(sync_order.multiprint_resume);
            }
            order.is_hidden  = sync_order.is_hidden

            if(sync_order.partner_id != false){
                var cust = order.pos.db.get_partner_by_id(sync_order.partner_id);
                if(!cust){
                    if(order.get_partner() != null){
                        order.set_partner(null);
                    }
                }
                if(order.get_partner() == null){
                    order.set_partner(cust);
                }
                else if(cust.id != order.get_partner().id){
                    order.set_partner(cust);
                }
            }
            else{
                if(order.get_partner() != null){
                    order.set_partner(null);
                }
            }
            var not_found = order.orderlines.map(function(r){
                return r.uid;
            });
            var order_lines = sync_order.lines;
            var old_order_line = order.orderlines
            
            while(order.get_last_orderline())
            {
                order.orderlines.remove(order.get_last_orderline());
            }
            var line=false;
            if(order_lines){
                for(var i=0;i<order_lines.length;i++){
                    var order_line_data = order_lines[i][2];
                    var product = self.db.get_product_by_id(order_line_data.product_id);
                    // if (!line){
                        line = Orderline.create({}, {pos: self, order: order, product: product,token_var:false});
                    // }
                    line.token_var = false;
                    line.created_by_name = order_line_data.created_by_name;
                    line.session_short_name = order_line_data.session_short_name;
                    line.order_line_status = order_line_data.order_line_status;
                    if(order_line_data.qty !== undefined){
                        line.set_quantity(order_line_data.qty);
                    }
                    if(order_line_data.price_unit !== undefined){
                        line.set_unit_price(order_line_data.price_unit);
                    }
                    if(order_line_data.discount !== undefined){
                        line.set_discount(order_line_data.discount);
                    }
                    order.orderlines.add(line);
                    if (typeof line.set_dirty === 'function' && typeof order_line_data.mp_dirty !== 'undefined'){
                        line.set_dirty(order_line_data.mp_dirty);
                    }
                    if (typeof line.mp_skip === 'function' && typeof order_line_data.mp_skip !== 'undefined'){
                        line.set_skip(order_line_data.mp_skip);
                    }
                    if(typeof line.set_note === 'function' && typeof order_line_data.note !== 'undefined'){
                        line.set_note(order_line_data.note);
                    }
                    var pack_lot_lines = order_line_data.pack_lot_ids;
                    if(pack_lot_lines.length > 0){
                        for (var i = 0; i < pack_lot_lines.length; i++) {
                            var packlotline = pack_lot_lines[i][2];
                            var pack_lot_line = Packlotline.create({}, {'json': _.extend(packlotline, {'order_line':line})});
                            line.pack_lot_lines.add(pack_lot_line);
                        }
                    }
                    line.cuid = order_line_data.cuid;
                    line.extra_id = order_line_data.extra_id;
                    line.token_var = true;
                } 
            }
            if(line){
                order.selected_orderline = line;
            }
            return order;
        }

        // async load_server_data(){
        //     var data = super.load_server_data(...arguments);
        //     var self = this;
        //     setTimeout(function(){
        //             console.log("Testing the list order>>>>>>>>kkk>>>>>>>>>",self.env.pos);

        //         if(self.env.pos.config && self.env.pos.config.wv_session_id){
        //             var list_orders = self.env.pos.get_order_list();
        //             while(list_orders.length > 0){
        //                 self.removeOrder(list_orders[0]);
        //             }
        //              self.transfer_data({'action':'sync_all_orders','order':self.env.pos.config.id});
        //         }
        //     },1000);
        //     return data;
        // }
    }
    Registries.Model.extend(PosGlobalState, PosSyncPosGlobalState);
    const PosSyncOrderline = (Orderline) => class PosSyncOrderline extends Orderline {
        constructor(obj, options) {
            super(obj, options);
            var self = this;
            self.token_var = true;
            self.wait_token = true;
            
            var user = this.pos.cashier || this.pos.user;
            var created_by_name = user.name;
            self.created_by_name = created_by_name;
            self.session_short_name =this.pos.config.session_short_name||'';
            self.order_line_status = 0;
            self.wvnote = this.wvnote || "";
            this.cuid = this.order.generate_unique_id() + '-' + this.id;
        }
        set_quantity(quantity){
            var self = this;
            var res = super.set_quantity(...arguments);
            if (quantity != 'remove') {
                if(self.token_var && test_varialbe){
                    if(this.pos.config.wv_session_id && this.pos.config.allow_auto_sync){
                        test_varialbe =false;
                        setTimeout(function(){ 
                            self.pos.transfer_data({'action':'update_order','order':self.order.export_as_JSON()});
                        

                           test_varialbe =true;
                        }, 500);
                    }
                }
            }
            return res;
        }

        set_discount(discount){
            var self = this;
            super.set_discount(...arguments);
            if(self.token_var && test_varialbe){
                if(this.pos.config.wv_session_id && this.pos.config.allow_auto_sync){
                    test_varialbe =false;
                    setTimeout(function(){ 
                        self.pos.transfer_data({'action':'update_order','order':self.order.export_as_JSON()});
                    

                       test_varialbe =true;
                    }, 500);
                }
            }
        }

        set_unit_price(price){
            var self = this;
            super.set_unit_price(...arguments);
            // var line = this;
            if(self.token_var && test_varialbe){
                if(this.pos.config.wv_session_id && this.pos.config.allow_auto_sync){
                    test_varialbe =false;
                    setTimeout(function(){ 
                        self.pos.transfer_data({'action':'update_order','order':self.order.export_as_JSON()});
                    

                       test_varialbe =true;
                    }, 500);
                }
            }
        }
         wvset_note(wvnote){
                this.wvnote = wvnote;
                
        }
        wvget_note(note){
            return this.wvnote;
        }
        export_as_JSON(){
            var data = super.export_as_JSON(...arguments);
            data.cuid = this.cuid;
            data.wvnote = this.wvnote;
            data.order_line_status = this.order_line_status;
            data.created_by_name = this.created_by_name;
            data.session_short_name = this.session_short_name;
            return data;
        }
    }
    Registries.Model.extend(Orderline, PosSyncOrderline);

const PosSyncOrder = (Order) => class PosSyncOrder extends Order {
        constructor(obj, options) {
            var res = super(obj, options);
            var self = this;
            options = options || {};
            this.session_short_name = this.pos.config.session_short_name || '';
            this.wait_customer = true;
            this.wait_temp = true;
            this.order_priority = this.order_priority || 0;
            return res;
        }
        // add_product(product, options){
        //     var res = super.add_product(...arguments);
        //     if (product) {
        //         var line = this.get_selected_orderline();
        //         this.pos.transfer_data('add_update_line', {'line' : line});
        //     }
        //     return res;
        // }
        set_partner(partner){
            super.set_partner(...arguments);
            var self = this;
            if(this.pos.config.wv_session_id && this.wait_customer && this.wait_temp && this.pos.config.allow_auto_sync){
                this.wait_temp = false;
                setTimeout(function(){ 
                    self.pos.transfer_data({'action':'update_order','order':self.pos.get_order().export_as_JSON()});
                    this.wait_temp = true;
                }, 1500);
            }
            else{
                self.wait_customer =true;
            }
        }
        remove_orderline(line){
            var self = this;
            var order = super.remove_orderline(...arguments);
            if (line) {
                if(this.pos.get_order()){
                    if(this.pos.config.wv_session_id && this.pos.config.allow_auto_sync){
                        if(token_remove){
                            token_remove = false;
                            setTimeout(function(){ 
                                self.pos.transfer_data({'action':'update_order','order':self.pos.get_order().export_as_JSON()});
                                token_remove = true;
                            }, 1100);
                        }
                    }
                }
            }
            return order
        }
        export_as_JSON(){
            var data = super.export_as_JSON(...arguments);
            var nick_name = ""
            if(this.session_short_name){
                nick_name = this.session_short_name;
            }
            else{
                nick_name = this.pos.config.session_short_name;
            }
            data.session_short_name = nick_name;
            data.order_priority = this.order_priority;
            return data;
        }
    }

    Registries.Model.extend(Order, PosSyncOrder);
});
