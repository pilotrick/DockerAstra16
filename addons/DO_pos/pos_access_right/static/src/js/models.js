odoo.define("pos_access_right.models", function (require) {
    "use strict";

    var { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var session = require('web.session');

    var group_negative_qty = false;
    var group_discount = false;
    var group_change_unit_price = false;
    var group_multi_order = false;
    var group_delete_order = false;
    var group_payment = false;
    var group_refund = false;
    var group_refund_invoice = false;
    var group_refund_reprint = false;
    var group_quotation_order = false;
    var group_qty = false;
    var group_order = false;
    var group_delete = false;
    var group_product_info_id = false;
    var group_fiscal_position_id = false;
    var group_customer_note_id = false;
    var group_product_item_id = false;
    var group_number_char_id = false;
    var group_set_pricelist_id = false;
    
    session.user_has_group('pos_access_right.group_negative_qty').then(function (has_create_group) {
        group_negative_qty = has_create_group;
    });
    session.user_has_group('pos_access_right.group_discount').then(function (has_create_group) {
        group_discount = has_create_group;
    });
    session.user_has_group('pos_access_right.group_change_unit_price').then(function (has_create_group) {
        group_change_unit_price = has_create_group;
    });
    session.user_has_group('pos_access_right.group_multi_order').then(function (has_create_group) {
        group_multi_order = has_create_group;
    });
    session.user_has_group('pos_access_right.group_delete_order').then(function (has_create_group) {
        group_delete_order = has_create_group;
    });
    session.user_has_group('pos_access_right.group_payment').then(function (has_create_group) {
        group_payment = has_create_group;
    });
    session.user_has_group('pos_access_right.group_refund').then(function (has_create_group) {
        group_refund = has_create_group;
    });
    session.user_has_group('pos_access_right.group_refund_invoice').then(function (has_create_group) {
        group_refund_invoice = has_create_group;
    });
    session.user_has_group('pos_access_right.group_refund_reprint').then(function (has_create_group) {
        group_refund_reprint = has_create_group;
    });
    session.user_has_group('pos_access_right.group_quotation_order').then(function (has_create_group) {
        group_quotation_order = has_create_group;
    });
    session.user_has_group('pos_access_right.group_qty').then(function (has_create_group) {
        group_qty = has_create_group;
    });
    session.user_has_group('pos_access_right.group_order').then(function (has_create_group) {
        group_order = has_create_group;
    });
    session.user_has_group('pos_access_right.group_delete').then(function (has_create_group) {
        group_delete = has_create_group;
    });
    session.user_has_group('pos_access_right.group_product_info_id').then(function (has_create_group) {
        group_product_info_id = has_create_group;
    });
    session.user_has_group('pos_access_right.group_fiscal_position_id').then(function (has_create_group) {
        group_fiscal_position_id = has_create_group;
    });
    session.user_has_group('pos_access_right.group_customer_note_id').then(function (has_create_group) {
        group_customer_note_id = has_create_group;
    });
    session.user_has_group('pos_access_right.group_product_item_id').then(function (has_create_group) {
        group_product_item_id = has_create_group;
    });
    session.user_has_group('pos_access_right.group_number_char_id').then(function (has_create_group) {
        group_number_char_id = has_create_group;
    });
    session.user_has_group('pos_access_right.group_set_pricelist_id').then(function (has_create_group) {
        group_set_pricelist_id = has_create_group;
    });
    
    const PosAccessRightGlobalState = (PosGlobalState) => class PosAccessRightGlobalState extends PosGlobalState {
    
        get_cashier() {

            const pos_cashier = super.get_cashier();
            if (pos_cashier == null){
                return false
            }
            pos_cashier.hasGroupNegativeQty = group_negative_qty;
            pos_cashier.hasGroupDiscount = group_discount;
            pos_cashier.hasGroupPriceControl = group_change_unit_price;
            pos_cashier.hasGroupMultiOrder = group_multi_order; 
            pos_cashier.hasGroupDeleteOrder = group_delete_order; 
            pos_cashier.hasGroupPayment = group_payment;
            pos_cashier.hasGroupRefund = group_refund;
            pos_cashier.hasGroupRefundInvoice = group_refund_invoice;
            pos_cashier.hasGroupRefundReprint = group_refund_reprint;
            pos_cashier.hasGroupQuotationOrder = group_quotation_order;
            pos_cashier.hasGroupQty = group_qty;
            pos_cashier.hasGroupOrder = group_order; 
            pos_cashier.hasGroupDelete = group_delete;
            pos_cashier.hasGroupProductInfo = group_product_info_id;
            pos_cashier.hasGroupFiscalPosition = group_fiscal_position_id;
            pos_cashier.hasGroupCustomerNote = group_customer_note_id;
            pos_cashier.hasGroupProductItem = group_product_item_id;
            pos_cashier.hasGroupNumberChar = group_number_char_id;
            pos_cashier.hasGroupSetPricelist = group_set_pricelist_id;
            return pos_cashier;
        }
    }
    Registries.Model.extend(PosGlobalState, PosAccessRightGlobalState);

});
