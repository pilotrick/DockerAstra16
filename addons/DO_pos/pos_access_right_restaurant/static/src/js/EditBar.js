odoo.define("pos_access_right_restaurant.EditBar", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const EditBar = require("pos_restaurant.EditBar");
    const { onMounted } = owl;

    const PosEditBar = (EditBar) =>
        class extends EditBar {
            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.mounted();
                });
            }

            mounted() {
                let cashier = this.env.pos.get_cashier();
                if (cashier){
                    if (cashier.hasGroupEditFloor == false){
                        //console.log("SYR: %o",cashier);
                        $('.edit-bar').prop('disabled', true);
                        //$('.edit-bar').css('background-color', 'lightgrey');
                        $('.edit-bar').css('opacity', '0.4');
                        $('.edit-bar').css('pointer-events', 'none');
                    }
                }
                
            }
        };

    Registries.Component.extend(EditBar, PosEditBar);

    return EditBar;
});
