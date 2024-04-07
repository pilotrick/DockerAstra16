odoo.define("an_pos_sales_person_restaurant.models", function(require) {
	"use strict";

	var { Orderline} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
	var core = require('web.core');
	var _t = core._t;

	const OrderLineInherit = (Orderline) => class OrderLineInherit extends Orderline {
        init_from_JSON(json) {
		    console.log(json);
		    if (this.pos.config.module_pos_restaurant && typeof(json.it_salesperson) === 'object'){
		        console.log(111);
                this.set_it_salesperson(json.it_salesperson[0]);
            }
            super.init_from_JSON(...arguments);
        }
	};

	Registries.Model.extend(Orderline, OrderLineInherit);
});

