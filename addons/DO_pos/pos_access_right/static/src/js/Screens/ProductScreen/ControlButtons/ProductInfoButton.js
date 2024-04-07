odoo.define("pos_access_right.ProductInfoButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const ProductInfoButton = require("point_of_sale.ProductInfoButton");
    const { onMounted } = owl;

    const PosProductInfoButton = (ProductInfoButton) =>
        class extends ProductInfoButton {
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
                if (cashier.hasGroupProductInfo == false){
                    $('.fa-info-circle').parent().addClass('disabled-mode');
                    $('.fa-info-circle').parent().css('background-color', 'lightgrey');
                    $('.fa-info-circle').parent().css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(ProductInfoButton, PosProductInfoButton);

    return ProductInfoButton;
});