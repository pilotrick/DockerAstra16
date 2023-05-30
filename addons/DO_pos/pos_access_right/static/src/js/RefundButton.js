odoo.define("pos_access_right.RefundButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const RefundButton = require("point_of_sale.RefundButton");
    const {onMounted} = owl;

    const PosRefundButton = (RefundButton) =>
        class extends RefundButton {
            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.mounted();
                });
            }

            mounted() {
                let cashier = this.env.pos.get_cashier();
                if (cashier.hasGroupRefund == false){
                    $('i[title="Reembolso"]').parent().addClass('disabled-mode');
                    $('i[title="Reembolso"]').parent().css('background-color', 'lightgrey');
                    $('i[title="Reembolso"]').parent().css('pointer-events', 'none');
                    $('i[title="Refund"]').parent().addClass('disabled-mode');
                    $('i[title="Refund"]').parent().css('background-color', 'lightgrey');
                    $('i[title="Refund"]').parent().css('pointer-events', 'none');
                }
            }
        };

    Registries.Component.extend(RefundButton, PosRefundButton);

    return RefundButton;
});