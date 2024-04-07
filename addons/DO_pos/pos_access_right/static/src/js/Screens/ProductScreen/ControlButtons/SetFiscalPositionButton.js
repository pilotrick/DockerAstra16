odoo.define("pos_access_right.SetFiscalPositionButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const SetFiscalPositionButton = require("point_of_sale.SetFiscalPositionButton");
    const { onMounted } = owl;

    const PosSetFiscalPositionButton = (SetFiscalPositionButton) =>
        class extends SetFiscalPositionButton {
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
                if (cashier.hasGroupFiscalPosition == false){
                    $('.fa-book').parent().addClass('disabled-mode');
                    $('.fa-book').parent().css('background-color', 'lightgrey');
                    $('.fa-book').parent().css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(SetFiscalPositionButton, PosSetFiscalPositionButton);

    return SetFiscalPositionButton;
});