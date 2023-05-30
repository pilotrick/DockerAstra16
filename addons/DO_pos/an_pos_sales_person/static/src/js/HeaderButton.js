odoo.define('an_pos_sales_person.HeaderButton', function (require) {
    'use strict';

    const HeaderButton = require('point_of_sale.HeaderButton');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;

    const HeaderButtonInherit = (HeaderButton) =>
        class extends HeaderButton {
            async onClick() {
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

                return super.onClick();
            }
        }
    Registries.Component.extend(HeaderButton, HeaderButtonInherit);
});
