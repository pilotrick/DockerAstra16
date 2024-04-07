odoo.define("pos_access_right.ProductItem", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const ProductItem = require("point_of_sale.ProductItem");
    const {onMounted} = owl;

    const PosProductItem = (ProductItem) =>
        class extends ProductItem {

            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.mounted();
                });
            }

            mounted() {
                let cashier = this.env.pos.get_cashier()

                if (cashier.hasGroupProductItem == false){ 
                    $('.product').prop('disabled', true);
                    $('.product').css('pointer-events', 'none');
                    $('.product').css('opacity', '0.4');
                }
            }
        };

    Registries.Component.extend(ProductItem, PosProductItem);

    return ProductItem;
});
