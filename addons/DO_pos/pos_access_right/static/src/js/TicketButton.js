odoo.define("pos_access_right.TicketButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const TicketButton = require("point_of_sale.TicketButton");
    const { onMounted } = owl;

    const PosTicketButton = (TicketButton) =>
        class extends TicketButton {
            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.HideButtonOrder();
                });
            }

            HideButtonOrder() {
                let cashier = this.env.pos.get_cashier();
                if (cashier){
                    //console.log("SYR: %o",cashier);
                    if (cashier.hasGroupOrder == false){
                        $('.ticket-button').prop('disabled', true);
                        $('.ticket-button').css('background-color', 'lightgrey');
                        $('.ticket-button').css('pointer-events', 'none');
                    }
                }
            }
        };

    Registries.Component.extend(TicketButton, PosTicketButton);

    return TicketButton;
});