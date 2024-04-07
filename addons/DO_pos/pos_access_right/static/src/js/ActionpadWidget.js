odoo.define("pos_access_right.ActionpadWidget", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const ActionpadWidget = require("point_of_sale.ActionpadWidget");
    const {onMounted} = owl;

    const PosActionpadWidget = (ActionpadWidget) =>
        class extends ActionpadWidget {

            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.mounted();
                });
            }

            mounted() {
                let cashier = this.env.pos.get_cashier()

                if (cashier.hasGroupPayment == false){ 
                    $('.pay').prop('disabled', true);
                    //$('.pay').css('background-color', 'lightgrey');
                    $('.pay').css('opacity', '0.4');
                }
            }
        };

    Registries.Component.extend(ActionpadWidget, PosActionpadWidget);

    return ActionpadWidget;
});
