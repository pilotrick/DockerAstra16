odoo.define("pos_access_right_restaurant.OrderlineNoteButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const OrderlineNoteButton = require("pos_restaurant.OrderlineNoteButton");
    const { onMounted } = owl;

    const PosOrderlineNoteButton = (OrderlineNoteButton) =>
        class extends OrderlineNoteButton {
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
                if (cashier.hasGroupInternalNotes == false){
                    $('.fa-tag').parent().prop('disabled', true);
                    $('.fa-tag').parent().css('background-color', 'lightgrey');
                    $('.fa-tag').parent().css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(OrderlineNoteButton, PosOrderlineNoteButton);

    return OrderlineNoteButton;
});
