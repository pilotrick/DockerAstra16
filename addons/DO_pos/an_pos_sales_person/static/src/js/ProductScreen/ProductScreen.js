odoo.define('an_pos_sales_person.ProductScreen', function (require) {
    'use strict';

    const Registries = require("point_of_sale.Registries");
    const ProductScreen = require('point_of_sale.ProductScreen');
    var core = require('web.core');
    var _t = core._t;

    const ProductScreenInherit = (ProductScreen) =>
        class extends ProductScreen {
            async _onClickPay() {
                var order = this.env.pos.get_order();
                if (this.env.pos.config.allow_salesperson && this.env.pos.config.action_type == 'manual' && order !== null){
                    var orderlines = order.get_orderlines();
                    var empty_salesperson_name = orderlines.find(
                        (line) => line.salesperson_name == undefined || line.salesperson_name === ''
                    );
                    if (empty_salesperson_name) {
                        this.showPopup('ErrorPopup', {
                            title: 'Error',
                            body: _t("You must select a cashier in the product lines."),
                        });
                        return false;
                    }
                }

                return super._onClickPay();
            }
            hasChangeSalespersonControlRights(){
                if (this.env.pos.get_cashier().hasGroupChangeSalesman) {
                    return true;
                }
                return false;
            }
        };

    Registries.Component.extend(ProductScreen, ProductScreenInherit);
});
