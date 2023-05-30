odoo.define("pos_access_right_restaurant.TableGuestsButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const TableGuestsButton = require("pos_restaurant.TableGuestsButton");
    const { onMounted } = owl;

    const PosTableGuestsButton = (TableGuestsButton) =>
        class extends TableGuestsButton {
            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.mounted();
                });
            }

            mounted() {
                let cashier = this.env.pos.get_cashier();
                //console.log("SYR: %o",cashier.hasGroupRefundReprint);
                if (cashier.hasGuest == false){
                    $('.control-button-number').parent().prop('disabled', true);
                    $('.control-button-number').parent().css('background-color', 'lightgrey');
                    $('.control-button-number').parent().css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(TableGuestsButton, PosTableGuestsButton);

    return TableGuestsButton;
});
