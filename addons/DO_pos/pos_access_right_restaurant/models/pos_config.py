# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    group_internal_notes_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups_restaurant",
        string="POS - Habilita Botón Notas Internas",
        help="This field is there to pass the id of the 'PoS - Internal Notes'"
             " Group to the Point of Sale Frontend.",
    )
    group_split_bill_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups_restaurant",
        string="POS - Habilita Botón Dividir Cuentas",
        help="This field is there to pass the id of the 'PoS - Split Bill'"
             " Group to the Point of Sale Frontend.",
    )
    group_transfer_order_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups_restaurant",
        string="POS - Habilita Botón Transferir Orden",
        help="This field is there to pass the id of the 'PoS - Transfer Order'"
             " Group to the Point of Sale Frontend.",
    )
    group_guest_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups_restaurant",
        string="POS - Habilita Botón Huéspedes",
        help="This field is there to pass the id of the 'PoS - Guest'"
             " Group to the Point of Sale Frontend.",
    )
    group_print_bill_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups_restaurant",
        string="POS - Habilita Botón Imprimir Cuenta",
        help="This field is there to pass the id of the 'PoS - Print Bill'"
             " Group to the Point of Sale Frontend.",
    )

    group_cutlery_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Pedido",
        help="This field is there to pass the id of the 'PoS - Cutlery'"
             " Group to the Point of Sale Frontend.",
    )
    group_edit_floor_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Editar Piso (Rest.)",
        help="This field is there to pass the id of the 'PoS - Cutlery'"
             " Group to the Point of Sale Frontend.",
    )

    def _compute_groups_restaurant(self):
        self.update(
            {
                "group_internal_notes_id": self.env.ref("pos_access_right_restaurant.group_internal_notes_id").id,
                "group_split_bill_id": self.env.ref("pos_access_right_restaurant.group_split_bill_id").id,
                "group_transfer_order_id": self.env.ref("pos_access_right_restaurant.group_transfer_order_id").id,
                "group_guest_id": self.env.ref("pos_access_right_restaurant.group_guest_id").id,
                "group_print_bill_id": self.env.ref("pos_access_right_restaurant.group_print_bill_id").id,
                "group_cutlery_id": self.env.ref("pos_access_right_restaurant.group_cutlery_id").id,
                "group_edit_floor_id": self.env.ref("pos_access_right_restaurant.group_edit_floor_id").id,
            }
        )
