from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    group_negative_qty_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón +/-",
        help="This field is there to pass the id of the 'PoS - Allow Negative"
        " Quantity' Group to the Point of Sale Frontend.",
    )

    group_discount_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Desc.",
        help="This field is there to pass the id of the 'PoS - Allow Discount'"
        " Group to the Point of Sale Frontend.",
    )

    group_change_unit_price_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Precio",
        help="This field is there to pass the id of the 'PoS - Allow Unit"
        " Price Change' Group to the Point of Sale Frontend.",
    )

    group_multi_order_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón 'Nueva orden'",
        help="This field is there to pass the id of the 'PoS - Many Orders"
        " Group to the Point of Sale Frontend.",
    )

    group_delete_order_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Borrar Ordenes (En menú Órdenes)",
        help="This field is there to pass the id of the 'PoS - Delete Order'"
        " Group to the Point of Sale Frontend.",
    )

    group_payment_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Pagar",
        help="This field is there to pass the id of the 'PoS - Payment'"
        " Group to the Point of Sale Frontend.",
    )

    group_refund_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Reembolso",
        help="This field is there to pass the id of the 'PoS - Refund'"
        " Group to the Point of Sale Frontend.",
    )

    group_refund_invoice_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Factura (En Reembolso)",
        help="This field is there to pass the id of the 'PoS - Refund Invoice'"
        " Group to the Point of Sale Frontend.",
    )

    group_refund_reprint_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Reimprimir (En Reembolso)",
        help="This field is there to pass the id of the 'PoS - Refund Reprint'"
        " Group to the Point of Sale Frontend.",
    )

    group_quotation_order_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Cotización/Orden",
        help="This field is there to pass the id of the 'PoS - Quotation Order'"
        " Group to the Point of Sale Frontend.",
    )

    group_qty_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Cant. (Cantidad)",
        help="This field is there to pass the id of the 'PoS - Qty'"
        " Group to the Point of Sale Frontend.",
    )

    group_order_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Órdenes",
        help="This field is there to pass the id of the 'PoS - Order'"
        " Group to the Point of Sale Frontend.",
    )

    group_delete_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Eliminar lineas de pedido",
        help="This field is there to pass the id of the 'PoS - Delete'"
        " Group to the Point of Sale Frontend.",
    )

    group_product_info_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Informacion",
        help="This field is there to pass the id of the 'PoS - Information'"
             " Group to the Point of Sale Frontend.",
    )

    group_fiscal_position_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Posición fiscal",
        help="This field is there to pass the id of the 'PoS - Fiscal Position'"
             " Group to the Point of Sale Frontend.",
    )

    group_customer_note_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Botón Notas de cliente",
        help="This field is there to pass the id of the 'PoS - Customer Notes'"
             " Group to the Point of Sale Frontend.",
    )

    group_product_item_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita Seleccion de productos",
        help="This field is there to pass the id of the 'PoS - Product Item'"
             " Group to the Point of Sale Frontend.",
    )

    group_number_char_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita el Number Char",
        help="This field is there to pass the id of the 'PoS - Number Char'"
             " Group to the Point of Sale Frontend.",
    )

    group_set_pricelist_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="POS - Habilita el Boton de tarifas",
        help="This field is there to pass the id of the 'PoS - Lista de precios'"
             " Group to the Point of Sale Frontend.",
    )

    def _compute_groups(self):
        self.update(
            {
                "group_negative_qty_id": self.env.ref("pos_access_right.group_negative_qty").id,
                "group_discount_id": self.env.ref("pos_access_right.group_discount").id,
                "group_change_unit_price_id": self.env.ref("pos_access_right.group_change_unit_price").id,
                "group_multi_order_id": self.env.ref("pos_access_right.group_multi_order").id,
                "group_delete_order_id": self.env.ref("pos_access_right.group_delete_order").id,
                "group_payment_id": self.env.ref("pos_access_right.group_payment").id,
                "group_refund_id": self.env.ref("pos_access_right.group_refund").id,
                "group_refund_invoice_id": self.env.ref("pos_access_right.group_refund_invoice").id,
                "group_refund_reprint_id": self.env.ref("pos_access_right.group_refund_reprint").id,
                "group_quotation_order_id": self.env.ref("pos_access_right.group_quotation_order").id,
                "group_qty_id": self.env.ref("pos_access_right.group_qty").id,
                "group_order_id": self.env.ref("pos_access_right.group_order").id,
                "group_delete_id": self.env.ref("pos_access_right.group_delete").id,
                "group_product_info_id": self.env.ref("pos_access_right.group_product_info_id").id,
                "group_fiscal_position_id": self.env.ref("pos_access_right.group_fiscal_position_id").id,
                "group_customer_note_id": self.env.ref("pos_access_right.group_customer_note_id").id,
                "group_product_item_id": self.env.ref("pos_access_right.group_product_item_id").id,
                "group_number_char_id": self.env.ref("pos_access_right.group_number_char_id").id,
                "group_set_pricelist_id": self.env.ref("pos_access_right.group_set_pricelist_id").id,
            }
        )
