odoo.define('an_pos_sales_person.HeaderLockButton', function (require) {
    'use strict';

    const HeaderLockButton = require('point_of_sale.HeaderLockButton');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;

    const HeaderLockButtonInherit = (HeaderLockButton) =>
        class extends HeaderLockButton {
            async showLoginScreen() {
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

                return super.showLoginScreen();
            }
        }
    Registries.Component.extend(HeaderLockButton, HeaderLockButtonInherit);
});
