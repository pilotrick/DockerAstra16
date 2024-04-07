odoo.define("pos_access_right.NumpadWidget", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const NumpadWidget = require("point_of_sale.NumpadWidget");
    const {onMounted} = owl;

    const PosNumpadWidget = (NumpadWidget) =>
        class extends NumpadWidget {

            setup() {
                super.setup();
                let self = this;
                onMounted(() => {
                   self.mounted();
                });
            }

            mounted() {
                let cashier = this.env.pos.get_cashier()
                $('.mode-button').each(function(idx,el){
                    if (cashier.hasGroupDiscount == false){
                        if (['% Disc','% Desc'].includes($(el).text())){
                            $(el).addClass('disabled-mode');
                            $(el).css('background-color', 'lightgrey');
                        }
                    }
                    if (cashier.hasGroupQty == false){
                        if (['Qty','Ctdad'].includes($(el).text())){
                            $(el).addClass('disabled-mode');
                            $(el).removeClass('selected-mode');
                            $(el).css({'background-color':'lightgrey', 'color':'#555555'});
                        };
                    }
                    if (cashier.hasGroupPriceControl == false){
                        if (['Price','Precio'].includes($(el).text())){
                            $(el).addClass('disabled-mode');
                            $(el).css('background-color', 'lightgrey');
                        }
                    }
                });
                if (cashier.hasGroupNumberChar == false){ 
                    $('.number-char').prop('disabled', true);
                    $('.number-char').css('background-color', 'lightgrey');
                }
                if (cashier.hasGroupNegativeQty == false){
                    $('.numpad-minus').prop('disabled', true);
                    $('.numpad-minus').css('background-color', 'lightgrey');
                }
                if (cashier.hasGroupDelete == false){
                    $('.numpad-backspace').prop('disabled', true);
                    $('.numpad-backspace').css('background-color', 'lightgrey');
                }
                
            }
        };

    Registries.Component.extend(NumpadWidget, PosNumpadWidget);

    return NumpadWidget;
});
