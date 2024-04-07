odoo.define("l10n_do_pos.models", function (require) {
  "use strict";

    var rpc = require("web.rpc");
    const Registries = require('point_of_sale.Registries');
    var { PosGlobalState, Order, } = require('point_of_sale.models');

    const PosGlobalStateInherit = (PosGlobalState) =>
        class PosGlobalStateInherit extends PosGlobalState {
            constructor() {
                super(...arguments);
                this.payer_types_selection = {
                    'taxpayer': 'Contribuyente',
                    'non_payer': 'Cliente de Consumo',
                    'nonprofit': 'Sin fines de lucro',
                    'special': 'Exento',
                    'governmental': 'Gubernamental',
                    'foreigner': 'Extranjero',
                }
            }
            /**
             * Envia un arreglo con las ordenes al servidor para generar las facturas
             * y luego de creadas facturas para las que sean de nota de credito actualizamos
             * la BD offline con los cambios
             * @param {Object} orders - Objeto con la lista de ordenes
             * @param {Object} options - Objeto con los configuracion opcional
             * @returns {Promise} Promise con la lista de ids generados en el servidor
             * @private
             */
            _save_to_server (orders, options) {
                var self = this;
                var server = super._save_to_server(...arguments);
                server.then(function (result){
                    var currentOrder = self.get_order();
                    if (result.length > 0 && currentOrder){
                        if(result[0].pos_reference == currentOrder.name){
                            currentOrder.ncf = result[0].ncf;
                            currentOrder.sale_fiscal_type = result[0].sale_fiscal_type;
                            currentOrder.origin_ncf = result[0].origin_ncf;
                        }
                    }
                });

                return server;
            }
        };
    Registries.Model.extend(PosGlobalState, PosGlobalStateInherit);

    const OrderInherit = (Order) => class OrderInherit extends Order {
        constructor() {
            super(...arguments);
            if (this.pos.config.only_invoice && !this.get_partner())
                this.to_invoice = true;

            if (!this.get_partner()) {
                var pos_default_partner = this.pos.config.default_partner_id;
                
                if (pos_default_partner) {
                    var client = this.pos.db.get_partner_by_id(pos_default_partner[0]);
                    if (client) {
                        this.set_partner(client);
                    }
                }
            }
            this.save_to_db();
        }
        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            this.ncf = json.ncf;
            this.sale_fiscal_type = json.sale_fiscal_type;
            this.origin_ncf = json.origin_ncf;
            this.to_invoice = json.to_invoice;
        }
        export_as_JSON() {
            var json = super.export_as_JSON(...arguments);
            json.ncf = this.ncf;
            json.sale_fiscal_type = this.sale_fiscal_type;
            json.origin_ncf = this.origin_ncf;
            json.to_invoice = this.to_invoice;
            return json;
        }
        export_for_printing() {
            var self = this;
            var result = super.export_for_printing(...arguments);
            result.company.company_address = self.pos.company.company_address;
            result.company.l10n_do_ncf_exp_date = self.pos.company.l10n_do_ncf_exp_date;
            result.ncf = self.ncf;
            result.sale_fiscal_type = self.sale_fiscal_type;
            result.origin_ncf = self.origin_ncf;
            result.to_invoice = self.to_invoice;
            return result;
        }
    }
    Registries.Model.extend(Order, OrderInherit);

});
