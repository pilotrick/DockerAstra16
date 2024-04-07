odoo.define('pos_multi_uoms', function (require) {
"use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const PosDB = require('point_of_sale.DB');
    const { PosGlobalState, Orderline } = require('point_of_sale.models');
    var utils = require('web.utils');

    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    const MultiUomPosGlobalState = (PosGlobalState) => class MultiUomPosGlobalState extends PosGlobalState {
        async _processData(loadedData) {
             await super._processData(...arguments);
            if (this.config.allow_multi_uom) {
                this.wv_uom_list = loadedData['product.multi.uom'];
            }
        }
    }
    Registries.Model.extend(PosGlobalState, MultiUomPosGlobalState);



    class MulitUOMWidget extends AbstractAwaitablePopup {
        multi_uom_button(event){
            // const value = $(event.target).html();
            var uom_id = $(event.target).data('uom_id');
            var price = $(event.target).data('price');
            var line = this.env.pos.get_order().get_selected_orderline();
            if(line){
                line.set_unit_price(price);
                line.set_product_uom(uom_id);
                line.price_manually_set = true;
            }
            this.cancel();
        }
    }
    MulitUOMWidget.template = 'MulitUOMWidget';
    MulitUOMWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };

    Registries.Component.add(MulitUOMWidget);

    class ChangeUOMButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        get selectedOrderline() {
            return this.env.pos.get_order().get_selected_orderline();
        }
        async onClick() {
            if (!this.selectedOrderline) return;
            var modifiers_list = [];
            var product = this.selectedOrderline.get_product();
            var wv_uom_list = this.env.pos.wv_uom_list;
            var multi_uom_ids = product.multi_uom_ids;
            for(var i=0;i<wv_uom_list.length;i++){
                if(multi_uom_ids.indexOf(wv_uom_list[i].id)>=0){
                    modifiers_list.push(wv_uom_list[i]);
                }
            }
            await this.showPopup('MulitUOMWidget', {
                title: this.env._t(' POS Multi UOM '),
                modifiers_list:modifiers_list,
            });
        }
    }
    ChangeUOMButton.template = 'ChangeUOMButton';

    ProductScreen.addControlButton({
        component: ChangeUOMButton,
        condition: function() {
            return this.env.pos.config.allow_multi_uom;
        },
    });

    Registries.Component.add(ChangeUOMButton);

    const PosMultiUomOrderline = (Orderline) => class PosMultiUomOrderline extends Orderline {
        constructor() {
            super(...arguments);
            this.wvproduct_uom = '';
        }

        set_product_uom(uom_id){
            this.wvproduct_uom = this.pos.units_by_id[uom_id];
            // this.trigger('change',this);
        }

        get_unit(){
            var unit_id = this.product.uom_id;
            if(!unit_id){
                return undefined;
            }
            unit_id = unit_id[0];
            if(!this.pos){
                return undefined;
            }
            return this.wvproduct_uom == '' ? this.pos.units_by_id[unit_id] : this.wvproduct_uom;
        }

        export_as_JSON(){
            var unit_id = this.product.uom_id;
            var json = super.export_as_JSON(...arguments);
            json.product_uom = this.wvproduct_uom == '' ? unit_id[0] : this.wvproduct_uom.id;
            return json;
        }
        init_from_JSON(json){
            super.init_from_JSON(...arguments);
            this.wvproduct_uom = json.wvproduct_uom;
        }
    }
    Registries.Model.extend(Orderline, PosMultiUomOrderline);
});

