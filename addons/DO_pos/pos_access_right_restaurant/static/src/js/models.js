odoo.define("pos_access_right_restaurant.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var session = require('web.session');

    var group_internal_notes_id = false;
    var group_split_bill_id = false;
    var group_transfer_order_id = false;
    var group_guest_id = false;
    var group_print_bill_id = false;
    var group_cutlery_id = false;
    var group_edit_floor_id = false;
        
    session.user_has_group('pos_access_right_restaurant.group_internal_notes_id').then(function (has_create_group) {
        group_internal_notes_id = has_create_group;
    });
    session.user_has_group('pos_access_right_restaurant.group_split_bill_id').then(function (has_create_group) {
        group_split_bill_id = has_create_group;
    });
    session.user_has_group('pos_access_right_restaurant.group_transfer_order_id').then(function (has_create_group) {
        group_transfer_order_id = has_create_group;
    });
    session.user_has_group('pos_access_right_restaurant.group_guest_id').then(function (has_create_group) {
        group_guest_id = has_create_group;
    });
    session.user_has_group('pos_access_right_restaurant.group_print_bill_id').then(function (has_create_group) {
        group_print_bill_id = has_create_group;
    });
    session.user_has_group('pos_access_right_restaurant.group_cutlery_id').then(function (has_create_group) {
        group_cutlery_id = has_create_group;
    });
    session.user_has_group('pos_access_right_restaurant.group_edit_floor_id').then(function (has_create_group) {
        group_edit_floor_id = has_create_group;
    });
    
    const PosAccessRightRestaurantGlobalState = (PosGlobalState) => class PosAccessRightRestaurantGlobalState extends PosGlobalState {
    
        get_cashier() {

            const pos_cashier = super.get_cashier();
            if (pos_cashier == null){
                return false
            }
            pos_cashier.hasGroupInternalNotes = group_internal_notes_id;
            pos_cashier.hasGroupSplitBill = group_split_bill_id;
            pos_cashier.hasGroupTransferOrder = group_transfer_order_id;
            pos_cashier.hasGuest = group_guest_id;
            pos_cashier.hasPrintBill = group_print_bill_id;
            pos_cashier.hasGroupCutlery = group_cutlery_id;
            pos_cashier.hasGroupEditFloor = group_edit_floor_id;
            //console.log("pos_cashier: %o", pos_cashier)
            return pos_cashier;
        }
    }
    Registries.Model.extend(PosGlobalState, PosAccessRightRestaurantGlobalState);

    
});
