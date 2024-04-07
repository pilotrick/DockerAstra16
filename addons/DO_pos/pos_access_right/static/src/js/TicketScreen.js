odoo.define("pos_access_right.TicketScreen", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const TicketScreen = require("point_of_sale.TicketScreen");
    const { onMounted } = owl;

    const PosTicketScreen = (TicketScreen) =>
        class extends TicketScreen {
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
                if (cashier.hasGroupMultiOrder == false){
                    $('.highlight').prop('disabled', true);
                    $('.highlight').css('background-color', 'lightgrey');
                    $('.highlight').css('pointer-events', 'none');
                }
                if (cashier.hasGroupDeleteOrder == false){
                    $('.delete-button').prop('disabled', true);
                    $('.delete-button').css('background-color', 'lightgrey');
                    $('.delete-button').css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(TicketScreen, PosTicketScreen);

    return TicketScreen;
});
