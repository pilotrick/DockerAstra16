odoo.define('pos_sync_order', function(require){
    var exports = {};
    var Backbone = window.Backbone;
    var models = require('point_of_sale.models');
    var session = require("web.session");
    var PosDB = require('point_of_sale.DB');
    const { posbus } = require('point_of_sale.utils');

    const LongpollingBus = require('pos_longpolling.LongpollingBus');


    LongpollingBus.include({
        _restartPolling() {
            if (this._pollRpc) {
                // this._pollRpc.abort();
            } else {
                this.startPolling();
            }
        },
    });
    
    PosDB.include({
        load: function(store,deft){
            if(this.cache[store] !== undefined){
                return this.cache[store];
            }
            var data = "";
            if(store != "unpaid_orders"){
                data = localStorage[this.name + '_' + store];
            }
            if(data !== undefined && data !== ""){
                data = JSON.parse(data);
                this.cache[store] = data;
                return data;
            }else{
                return deft;
            }
            return deft;
        },
        save: function(store,data){
            if(store != "unpaid_orders"){
                localStorage[this.name + '_' + store] = JSON.stringify(data);
                this.cache[store] = data;
            }
        },
    });

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function(){
            var self = this;
            this.pos_session = null;
            this.pos_kitchen_data = [];
            PosModelSuper.prototype.initialize.apply(this, arguments);
            this.get('orders').bind('remove', function(order, collection, options){
                if(self.sync_session && self.sync_session.allow_remove_sync && self.config.wv_session_id){
                    self.sync_session.send({'action':'remove_order','order':order.uid});
                }
            });
           this.ready.then(function () {
                if(! self.config.allow_incoming_orders){
                    return
                }
                var channel_name = "pos_sync_session";
                var callback = function(message){
                    // console.log("Testing the messages>>>>>>>>>>>>>>>>>>>>",message);
                    // self.db.add_products(_.map(message.data, function (product) {
                    //     product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                    //     return new models.Product({}, product);
                    // }));
                    // self.gui.screen_instances['products'].replace();
                    // if(message['action']=="update_order"){
                    //     self.update_the_order(message['order']);
                    // }
                    // else if(message['action']=="remove_order"){
                    //     var order = self.get('orders').find(function (order) {
                    //         return order.uid == message['order'];
                    //     });
                    //     if(order){
                    //         order.destroy({'reason': 'abandon'});
                    //          self.gui.show_screen(self.gui.get_current_screen(),{},'refresh');
                    //     }
                    // }
                    if(self.config.pos_kitchen_view){
                        if(message['action']=="update_order"){
                            var all_data = self.pos_kitchen_data;
                            var p_tok = true;
                            for(var i=0;i<all_data.length;i++){
                                if(all_data[i].uid == message['order'].uid){
                                    p_tok = false;
                                    self.pos_kitchen_data[i] = message['order'];
                                }
                            }
                            if(p_tok){
                                self.pos_kitchen_data.push(message['order']);
                            }
                            self.gui.show_screen('kitchen_screen',{},'refresh');
                        }
                        else if(message['action']=="remove_order"){
                            var all_data = self.pos_kitchen_data;
                            for(var i=0;i<all_data.length;i++){
                                if(all_data[i].uid == message['order']){
                                    self.pos_kitchen_data.splice(i, 1);
                                }
                            }
                            self.gui.show_screen('kitchen_screen',{},'refresh');
                        }
                    }
                    else{
                        if(message['action']=="update_order"){
                            self.update_the_order(message['order']);
                        }
                        else if(message['action']=="remove_order"){
                            var order = self.get('orders').find(function (order) {
                                return order.uid == message['order'];
                            });
                            if(order){
                                order.destroy({'reason': 'abandon'});
                                posbus.trigger('order-deleted');
                                self.env.pos.trigger('change:selectedOrder', self.env.pos, self.env.pos.get_order());
                                // self.gui.show_screen(self.gui.get_current_screen(),{},'refresh');
                            }
                        }

                    }
                }
                self.bus.add_channel_callback(channel_name, callback, self);
                if (self.config.sync_server){
                    self.add_bus('sync_server', self.config.sync_server);
                    self.get_bus('sync_server').add_channel_callback(channel_name, callback, self);
                    self.sync_bus = self.get_bus('sync_server');
                    self.get_bus('sync_server').start();
                } else {
                    self.sync_bus = self.get_bus();
                    if (!self.config.autostart_longpolling) {
                        self.sync_bus.start();
                    }
                }
            });
        },
        update_the_order: function(sync_order){
            var self = this;
            if(!self.config.allow_incoming_orders)
                return;
            var order = this.get('orders').find(function(ord){
                return ord.uid == sync_order.uid;
            });
            if (!order){
                var sequence_number = sync_order.sequence_number;
                if (sequence_number == self.pos_session.sequence_number){
                } else if (sequence_number > self.pos_session.sequence_number){
                self.pos_session.sequence_number = sequence_number;
                }
                order = new models.Order({},{pos:this});
                order.uid = sync_order.uid;
    
                var current_order = self.get_order();
                self.get('orders').add(order);
                self.set('selectedOrder', current_order);
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
                    if(order.get_client() != null){
                        order.set_client(null);
                    }
                }
                if(cust.id != order.get_client().id){
                    order.set_client(cust);
                }
            }
            else{
                if(order.get_client() != null){
                    order.set_client(null);
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
            if(order_lines){
                for(var i=0;i<order_lines.length;i++){
                    var order_line_data = order_lines[i][2];
                    var product = self.db.get_product_by_id(order_line_data.product_id);
                    // if (!line){
                        var line = new models.Orderline({}, {pos: self, order: order, product: product,token_var:false});
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
                    line.cuid = order_line_data.cuid;
                    line.extra_id = order_line_data.extra_id;
                    line.token_var = true;
                } 
            }
            return order;
        },
        load_server_data: function () {
            res = PosModelSuper.prototype.load_server_data.apply(this);
            var self = this;
            return res.then(function () {
                if (self.config.wv_session_id) {
                    self.sync_session = new exports.SyncSession(self);
                    // self.sync_session.start();
                    self.sync_session.send({'action':'sync_all_orders','order':self.config.id});
                }
            });
        },
    });
    var test_varialbe = true;
    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        initialize: function(){
            var self = this;
            self.token_var = true;
            self.wait_token = true;
            OrderlineSuper.prototype.initialize.apply(this, arguments);
            var user = this.pos.cashier || this.pos.user;
            created_by_name = user.name;
            self.created_by_name = created_by_name;
            self.session_short_name =this.pos.config.session_short_name||'';
            self.order_line_status = 0;
            self.wvnote = this.wvnote || "";
            this.cuid = this.order.generate_unique_id() + '-' + this.id;
            this.bind('change', function(line){
                if(self.token_var && test_varialbe){
                    if(this.pos.sync_session && this.pos.config.wv_session_id && this.pos.config.allow_auto_sync){
                        test_varialbe =false;
                        var order = self.order
                        self.wait_token =false;
                        if(order){
                            setTimeout(function(){ 
                            self.pos.sync_session.send({'action':'update_order','order':self.order.export_as_JSON()});

                               test_varialbe =true;
                            }, 500);
                        }
                    }
                }     
            });    
        },
         wvset_note: function(wvnote){
                this.wvnote = wvnote;
                this.trigger('change',this);
        },
        wvget_note: function(note){
            return this.wvnote;
        },
        export_as_JSON: function(){
            var data = OrderlineSuper.prototype.export_as_JSON.apply(this, arguments);
            data.cuid = this.cuid;
            data.wvnote = this.wvnote;
            data.order_line_status = this.order_line_status;
            data.created_by_name = this.created_by_name;
            data.session_short_name = this.session_short_name;
            return data;
        }
    });
    var token_remove = true;
    var OrderSuper = models.Order;
    models.Order = models.Order.extend({
        initialize: function(attributes, options){
            var self = this;
            options = options || {};
            OrderSuper.prototype.initialize.apply(this, arguments);
            this.session_short_name = this.pos.config.session_short_name || '';
            this.wait_customer = true;
            this.wait_temp = true;
            this.order_priority = this.order_priority || 0;
        },
        remove_orderline: function(line){
            OrderSuper.prototype.remove_orderline.apply(this, arguments);
            var self = this;
            if(this.pos.sync_session && this.pos.config.wv_session_id && this.pos.config.allow_auto_sync){
                if(token_remove){
                    token_remove = false;
                    setTimeout(function(){ 
                        self.pos.sync_session.send({'action':'update_order','order':self.export_as_JSON()});
                        token_remove = true;
                    }, 1100);
                }
            }
        },
        set_client: function(client){
            var self = this;
            OrderSuper.prototype.set_client.apply(this,arguments);
            if(this.pos.sync_session && this.pos.config.wv_session_id && this.wait_customer && this.wait_temp && this.pos.config.allow_auto_sync){
                this.wait_temp = false;
                setTimeout(function(){ 
                    self.pos.sync_session.send({'action':'update_order','order':self.export_as_JSON()});
                    this.wait_temp = true;
                }, 1500);
            }
            else{
                self.wait_customer =true;
            }
        },
        add_product: function(){
            var self = this;
            OrderSuper.prototype.add_product.apply(this, arguments);
            // this.get_last_orderline().token_var=false;
            // setTimeout(function(){self.get_last_orderline().token_var=true;}, 1300);
        },
        export_as_JSON: function(){
            var data = OrderSuper.prototype.export_as_JSON.apply(this, arguments);
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
        },
    });
    exports.SyncSession = Backbone.Model.extend({
        initialize: function(pos){
            this.pos = pos;
        },
        start: function(){
            var self = this;
            this.allow_remove_sync = false;
        },
        send: function(order){
            var self = this;
            session.rpc('/pos_sync_session/',{
                        session_id: self.pos.config.wv_session_id[0],
                        order: order,
                        pos_config_id:self.pos.config.id,
            }).then(function(results){
                    if(typeof results === "object"){
                        if(results['action']=='sync_all_orders'){
                            if(results['order'].length >0){
                                _.each(results['order'], function(res){
                                    self.pos.update_the_order(res['order']);
                                });
                                var uid_list = [];
                                for(var i=0;i<results['order'].length;i++){
                                    uid_list.push(results['order'][i]['order'].uid);
                                }
                                if(uid_list.length > 0){
                                    var list_orders = self.pos.get('orders');
                                    _.each(list_orders.models, function(wvorder){
                                        if(wvorder != undefined){
                                            if(uid_list.indexOf(wvorder.uid)<0){
                                               wvorder.destroy({'reason': 'abandon'});
                                               self.pos.trigger('change:selectedOrder', self.pos, self.pos.get_order()); 
                                            }
                                        }
                                    });
                                }
                            }
                        }
                    }
                    self.allow_remove_sync = true;
            },
            function (error, e) {
                e.preventDefault();
                console.log("Please Check your Internet Connection.")
            });
        },

    });
    return exports;
});
