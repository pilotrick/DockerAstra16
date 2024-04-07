odoo.define('l10n_cu_pos.TicketScreen', function(require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');
    var core    = require('web.core');
    var _t      = core._t;

    const TicketScreenInherit = TicketScreen =>
        class extends TicketScreen {
            //@override
            async _onDoRefund() {
                const order = this.getSelectedSyncedOrder();
                const partner = order.get_partner();
                const destinationOrder =
                    this.props.destinationOrder && partner === this.props.destinationOrder.get_partner()
                        ? this.props.destinationOrder
                        : this._getEmptyOrder(partner);
//                try {
//                    let result = await this.rpc({
//                        model: "pos.order",
//                        method: "get_from_ui",
//                        args: [order.name]
//                      });
//                    destinationOrder.ncf = result.ncf_invoice_related;
//                } catch (error) {
//                    throw error;
//                }
                let result = await this.rpc({
                    model: "pos.order",
                    method: "get_from_ui",
                    args: [order.name]
                });
                if (destinationOrder){
                    destinationOrder.ncf = result.ncf_invoice_related;
                }

                super._onDoRefund();
            }
        };

    Registries.Component.extend(TicketScreen, TicketScreenInherit);
    return TicketScreen;
});
