odoo.define("pos_access_right.OrderlineCustomerNoteButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const OrderlineCustomerNoteButton = require("point_of_sale.OrderlineCustomerNoteButton");
    const { onMounted } = owl;

    const PosOrderlineCustomerNoteButton = (OrderlineCustomerNoteButton) =>
        class extends OrderlineCustomerNoteButton {
            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.mounted();
                });
            }

            mounted() {
                let cashier = this.env.pos.get_cashier();
                //console.log("SYR: %o",$('i[class="fa-sticky-note"]').parent());
                if (cashier.hasGroupCustomerNote == false){
                    $('.fa-sticky-note').parent().addClass('disabled-mode');
                    $('.fa-sticky-note').parent().css('background-color', 'lightgrey');
                    $('.fa-sticky-note').parent().css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(OrderlineCustomerNoteButton, PosOrderlineCustomerNoteButton);

    return OrderlineCustomerNoteButton;
});