odoo.define("pos_access_right_restaurant.TransferOrderButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const TransferOrderButton = require("pos_restaurant.TransferOrderButton");
    const { onMounted } = owl;

    const PosTransferOrderButton = (TransferOrderButton) =>
        class extends TransferOrderButton {
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
                if (cashier.hasGroupTransferOrder == false){
                    $('.fa-arrow-right').parent().prop('disabled', true);
                    $('.fa-arrow-right').parent().css('background-color', 'lightgrey');
                    $('.fa-arrow-right').parent().css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(TransferOrderButton, PosTransferOrderButton);

    return TransferOrderButton;
});
