odoo.define("pos_access_right.SetSaleOrderButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const SetSaleOrderButton = require("pos_sale.SetSaleOrderButton");
    const {onMounted} = owl;

    const PosSetSaleOrderButton = (SetSaleOrderButton) =>
        class extends SetSaleOrderButton {
            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.mounted();
                });
            }

            mounted() {
                let cashier = this.env.pos.get_cashier();
                //console.log("SYR: %o",cashier);
                if (cashier.hasGroupQuotationOrder == false){
                    $('.o_sale_order_button').prop('disabled', true);
                    $('.o_sale_order_button').css('background-color', 'lightgrey');
                    $('.o_sale_order_button').css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(SetSaleOrderButton, PosSetSaleOrderButton);

    return SetSaleOrderButton;
});