odoo.define("pos_access_right_restaurant.PrintBillButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const PrintBillButton = require("pos_restaurant.PrintBillButton");
    const { onMounted } = owl;

    const PosPrintBillButton = (PrintBillButton) =>
        class extends PrintBillButton {
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
                if (cashier.hasPrintBill == false){
                    $('.order-printbill').prop('disabled', true);
                    $('.order-printbill').css('background-color', 'lightgrey');
                    $('.order-printbill').css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(PrintBillButton, PosPrintBillButton);

    return PrintBillButton;
});
