odoo.define("pos_access_right.ReprintReceiptButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const ReprintReceiptButton = require("point_of_sale.ReprintReceiptButton");
    const { onMounted } = owl;

    const PosReprintReceiptButton = (ReprintReceiptButton) =>
        class extends ReprintReceiptButton {
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
                if (cashier.hasGroupRefundReprint == false){
                    $('.fa-print').parent().prop('disabled', true);
                    $('.fa-print').parent().css('background-color', 'lightgrey');
                    $('.fa-print').parent().css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(ReprintReceiptButton, PosReprintReceiptButton);

    return ReprintReceiptButton;
});
