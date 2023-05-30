odoo.define("an_pos_sales_person.PosModel", function(require) {
	"use strict";

	var rpc = require("web.rpc");
	var core = require('web.core');
    var { PosGlobalState, Order, Orderline} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
	var _t = core._t;

	const PosGlobalStateInherit = (PosGlobalState) =>
        class PosGlobalStateInherit extends PosGlobalState {
            async _processData(loadedData) {
                await super._processData(...arguments);
                if (this.config.allow_salesperson) {
                    this.users = loadedData['users'];
                }
            }
            /**
             * Le agrega al cajero el campo hasGroupChangeSalesman para identificar si
             * puede cambiar de cajero en el modo 'manual'.

             * @returns {Object} Cajero con el campo hasGroupChangeSalesman.
             */
            get_cashier() {
                const pos_cashier = super.get_cashier(...arguments);
                if (this.env.pos.config.allow_salesperson && this.env.pos.config.action_type == 'manual'){
                    const cashier = this.env.pos.users.find(
                        (user) => user.id === pos_cashier.user_id
                    );
                    pos_cashier.hasGroupChangeSalesman =
                        cashier &&
                        pos_cashier.groups_id.includes(
                            this.env.pos.config.group_change_salesperson_id[0]
                        );
                }
                return pos_cashier;
            }
    };

    Registries.Model.extend(PosGlobalState, PosGlobalStateInherit);
	
	const OrderInherit = (Order) => class OrderInherit extends Order {
        export_for_printing() {
            var data = super.export_for_printing(...arguments);
            var cashiers = []; // Cajeros(empleados) de la orden sin repetir.
            var orderlines = this.get_orderlines();
            for (var line in orderlines){
                if (!cashiers.includes(orderlines[line].salesperson_name)) {
                    cashiers.push(orderlines[line].salesperson_name);
                }
            }
            data.cashiers = cashiers;
            return data;
        }
        set_orderline_options(orderline, options) {
            super.set_orderline_options(...arguments);
            if (options.it_salesperson) {
                orderline.it_salesperson = options.it_salesperson;
                orderline.salesperson_name = options.salesperson_name;
            }
        }
        /**
         * Se sobreescribe el metodo para establece el vendedor en las lineas en el modo 'automatico'.
         */
        async add_product(product, options){
            //Accion de _clickProduct que viene del ProductScreen
            if (this.pos.config.allow_salesperson
                && !('refunded_orderline_id' in options)
                && this.pos.config.action_type == 'automatic'){
                var cashier = this.pos.get_cashier();
                var cashier_id = cashier ? cashier.id : false;

                super.add_product(...arguments);
                if (this.get_selected_orderline() !== undefined
                    && cashier_id
                    && this.get_selected_orderline().get_it_salesperson() == false){
                    this.get_selected_orderline().set_it_salesperson(cashier_id);
                }
            }
            else {
                Object.assign(options, {
                    merge: false,
                });
                super.add_product(...arguments);
            }
        }
    }

    Registries.Model.extend(Order, OrderInherit);
	
	const OrderLineInherit = (Orderline) => class OrderLineInherit extends Orderline {
		constructor() {
            super(...arguments);
            if (!this.it_salesperson){
                this.it_salesperson = 0;
                this.salesperson_name = "";
			}
		}
		clone(){
		    var orderline = super.clone(...arguments);
		    orderline.it_salesperson = this.it_salesperson;
		    orderline.salesperson_name = this.salesperson_name;
		    return orderline;
		}
		can_be_merged_with(orderline) {
		    if (this.pos.config.allow_salesperson && this.pos.config.action_type == 'automatic'){
                var cashier = this.pos.get_cashier();
                var cashier_id = cashier ? cashier.id : false;

                if (this.it_salesperson !== cashier_id) {
                    return false;
                }
            }

            return super.can_be_merged_with(...arguments);
        }
		set_it_salesperson(it_salesperson){
            this.it_salesperson = it_salesperson;
            var employee = this.pos.employee_by_id[it_salesperson];
            this.salesperson_name = employee.name;
        }
		get_it_salesperson(){
		    return this.it_salesperson;
		}
		get_salesperson_name(){
		    return this.salesperson_name;
		}
		init_from_JSON(json) {
		    super.init_from_JSON(...arguments);
            this.set_it_salesperson(json.it_salesperson);
        }
		export_as_JSON() {
			var data = super.export_as_JSON(...arguments);
			data.it_salesperson = this.get_it_salesperson();
			data.salesperson_name = this.get_salesperson_name();
			return data;
		}
		export_for_printing() {
			var data = super.export_for_printing(...arguments);
			data.it_salesperson = this.get_it_salesperson();
			data.salesperson_name = this.get_salesperson_name();
			return data;
		}
	};

	Registries.Model.extend(Orderline, OrderLineInherit);
	
});

odoo.define('an_pos_sales_person.ITControlButtons', function(require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    var core = require('web.core');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    var _t = core._t;

    const { useState } = owl;

    class PosSalesperson extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this._manage_salesperson);
        }
        /**
         * Envia los empleados al popup PosSalespersonPopup y luego lo muestra.
         */
        _manage_salesperson() {
            var list_of_salesperson = this.env.pos.employees;
            this.showPopup('PosSalespersonPopup', {'list_of_salesperson': list_of_salesperson});
        }
    };

    PosSalesperson.template = 'PosSalesperson';
    Registries.Component.add(PosSalesperson);

    class PosSalespersonPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.filter = useState({ value: "" });
        }
        get displayedSalesperson() {
            var list_salesperson = this.props.list_of_salesperson;
            if (this.filter.value != ""){
                return list_salesperson.filter((t) => t.name.match(this.filter.value));
            }
            return list_salesperson;
        }
        click_on_salesperson(event) {
            var self = this;
            var salesperson_id = parseInt(event.currentTarget.dataset['salespersonId']);
            if (this.env.pos.get_order().get_selected_orderline() !== undefined){
        	    this.env.pos.get_order().get_selected_orderline().set_it_salesperson(salesperson_id);
            }
            else{
                Gui.showPopup('ErrorPopup', {
                    'title': _t('Error !!!'),
                    'body': _t("Sorry, add product to order line inorder to add salesperson."),
                });
                return;
            }
        }
    };
    PosSalespersonPopup.template = 'PosSalespersonPopup';
    Registries.Component.add(PosSalespersonPopup);
    return PosSalesperson, PosSalespersonPopup;
});

odoo.define('an_pos_sales_person.Orderline', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const Orderline = require('point_of_sale.Orderline');

    const OrderlineCustom = Orderline =>
        class extends Orderline {
            addSalesperson() {
                var list_of_salesperson = this.env.pos.employees;
                this.showPopup('PosSalespersonPopup', {'list_of_salesperson': list_of_salesperson});
            }
    };
    Registries.Component.extend(Orderline, OrderlineCustom);
    return Orderline;
});