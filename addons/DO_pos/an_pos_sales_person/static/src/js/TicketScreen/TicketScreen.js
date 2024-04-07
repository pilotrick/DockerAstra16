odoo.define('an_pos_sales_person.TicketScreen', function(require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');

    const TicketScreenInherit = TicketScreen =>
        class extends TicketScreen {
            _getToRefundDetail(orderline) {
                var detail = super._getToRefundDetail(orderline);
                var line = detail.orderline;
                line["it_salesperson"] = orderline.it_salesperson;
                line["salesperson_name"] = orderline.salesperson_name;
                return detail;
            }
            _prepareRefundOrderlineOptions(toRefundDetail) {
                const { qty, orderline } = toRefundDetail;
                var detail = super._prepareRefundOrderlineOptions(toRefundDetail);
                detail["it_salesperson"] = orderline.it_salesperson;
                detail["salesperson_name"] = orderline.salesperson_name;
                return detail;
            }
        };

    Registries.Component.extend(TicketScreen, TicketScreenInherit);
    return TicketScreen;
});
