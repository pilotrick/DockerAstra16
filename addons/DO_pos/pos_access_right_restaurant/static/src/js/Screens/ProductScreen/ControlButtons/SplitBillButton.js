odoo.define("pos_access_right_restaurant.SplitBillButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const SplitBillButton = require("pos_restaurant.SplitBillButton");
    const { onMounted } = owl;

    const PosSplitBillButton = (SplitBillButton) =>
        class extends SplitBillButton {
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
                if (cashier.hasGroupSplitBill == false){
                    $('.order-split').prop('disabled', true);
                    $('.order-split').css('background-color', 'lightgrey');
                    $('.order-split').css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(SplitBillButton, PosSplitBillButton);

    return SplitBillButton;
});
