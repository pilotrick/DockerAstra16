odoo.define("pos_access_right.SetPricelistButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const SetPricelistButton = require("point_of_sale.SetPricelistButton");
    const { onMounted } = owl;

    const PosSetPricelistButton = (SetPricelistButton) =>
        class extends SetPricelistButton {
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
                if (cashier.hasGroupSetPricelist == false){
                    $('.o_pricelist_button').addClass('disabled-mode');
                    $('.o_pricelist_button').css('background-color', 'lightgrey');
                    $('.o_pricelist_button').css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(SetPricelistButton, PosSetPricelistButton);

    return SetPricelistButton;
});