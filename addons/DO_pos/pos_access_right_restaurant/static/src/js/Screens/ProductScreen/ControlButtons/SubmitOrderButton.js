odoo.define("pos_access_right_restaurant.SubmitOrderButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const SubmitOrderButton = require("pos_restaurant.SubmitOrderButton");
    const { onMounted } = owl;

    const PosSubmitOrderButton = (SubmitOrderButton) =>
        class extends SubmitOrderButton {
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
                if (cashier.hasGroupCutlery == false){
                    $('.fa-cutlery').parent().prop('disabled', true);
                    $('.fa-cutlery').parent().css('background-color', 'lightgrey');
                    $('.fa-cutlery').parent().css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(SubmitOrderButton, PosSubmitOrderButton);

    return SubmitOrderButton;
});
