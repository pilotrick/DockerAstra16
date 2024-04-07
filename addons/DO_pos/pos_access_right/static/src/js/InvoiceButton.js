odoo.define("pos_access_right.InvoiceButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const InvoiceButton = require("point_of_sale.InvoiceButton");
    const { onMounted } = owl;

    const PosInvoiceButton = (InvoiceButton) =>
        class extends InvoiceButton {
            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.mounted();
                });
            }

            mounted() {
                let cashier = this.env.pos.get_cashier();
                //console.log("SYR: %o",cashier.hasGroupRefundInvoice);
                if (cashier.hasGroupRefundInvoice == false){
                    $('.fa-file-pdf-o').parent().prop('disabled', true);
                    $('.fa-file-pdf-o').parent().css('background-color', 'lightgrey');
                    $('.fa-file-pdf-o').parent().css('pointer-events', 'none');
                }
                
            }
        };

    Registries.Component.extend(InvoiceButton, PosInvoiceButton);

    return InvoiceButton;
});
