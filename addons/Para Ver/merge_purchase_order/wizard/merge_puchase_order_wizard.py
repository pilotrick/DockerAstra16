# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MergePurchaseOrder(models.TransientModel):
    _name = 'merge.purchase.order'
    _description = 'Merge Purchase Order'
    merge_type = \
        fields.Selection([
            ('new_cancel',
                'Crear nueva orden y cancelar las seleccionadas'),
            ('new_delete',
             'Crear nueva orden y eliminar las seleccionadas'),
            ('merge_cancel',
             'Combinar ordenes and y cancelar las seleccionadas'),
            ('merge_delete',
                'Combinar ordenes and y Eliminar las seleccionadas')],
            default='new_delete', string="Tipo de Combinacion")
    purchase_order_id = fields.Many2one('purchase.order', 'Orden de Compra Principal')
    
    supplier_id = fields.Many2one('res.partner', 'Cambiar Proveedor?')
    
    sumar_producto = fields.Boolean('Sumar producto?')
    
    
    @api.model
    def default_get(self, fields):
        res = super(MergePurchaseOrder, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        purchase_ids = self.env['purchase.order'].browse(active_ids)
        partner = purchase_ids[0].partner_id.id
        res.update({
            'supplier_id': partner
        })
        return res

    @api.onchange('merge_type')
    def onchange_merge_type(self):
        res = {}
        for order in self:
            order.purchase_order_id = False
            if order.merge_type in ['merge_cancel', 'merge_delete']:
                purchase_orders = self.env['purchase.order'].browse(
                    self._context.get('active_ids', []))
                res['domain'] = {
                    'purchase_order_id':
                    [('id', 'in',
                        [purchase.id for purchase in purchase_orders])]
                }
            return res

    def merge_orders(self):
        purchase_orders = self.env['purchase.order'].browse(
            self._context.get('active_ids', []))
        existing_po_line = False
        sec = 10
        if len(self._context.get('active_ids', [])) < 2:
            raise UserError(
                _('Seleccione al menos dos órdenes de compra para realizar '
                    'la operacion.'))
        if any(order.state != 'draft' for order in purchase_orders):
            raise UserError(
                _('Seleccione Órdenes de compra que están en estado Borrador '
                   'para realizar la operación de fusión.'))
        
        partner = self.supplier_id.id
        if self.merge_type == 'new_cancel':
            po = self.env['purchase.order'].with_context({
                'trigger_onchange': True,
                'onchange_fields_to_trigger': [partner]
            }).create({'partner_id': partner})
            for order in purchase_orders:
                for line in order.order_line:
                    
                    default = {'order_id': po.id, 'sequence': sec}
                    existing_po_line = False
                    if po.order_line and self.sumar_producto:
                        for poline in po.order_line:
                            if not line.display_type and line.product_id == poline.product_id and\
                                    line.price_unit == poline.price_unit:
                                existing_po_line = poline
                                break
                    if existing_po_line:
                        existing_po_line.product_qty += line.product_qty
                        po_taxes = [
                            tax.id for tax in existing_po_line.taxes_id]
                        [po_taxes.append((tax.id))
                         for tax in line.taxes_id]
                        existing_po_line.taxes_id = \
                            [(6, 0, po_taxes)]
                    else:
                        line.copy(default=default)
            for order in purchase_orders:
                order.button_cancel()
        elif self.merge_type == 'new_delete':
            po = self.env['purchase.order'].with_context({
                'trigger_onchange': True,
                'onchange_fields_to_trigger': [partner]
            }).create({'partner_id': partner})

            for order in purchase_orders:
                for line in order.order_line:
                    default = {'order_id': po.id, 'sequence': sec}
                    existing_po_line = False
                    if not line.display_type and  po.order_line and self.sumar_producto:
                        for po_line in po.order_line:
                            if line.product_id == po_line.product_id and \
                                    line.price_unit == po_line.price_unit:
                                existing_po_line = po_line
                                break
                    if existing_po_line:
                        existing_po_line.product_qty += line.product_qty
                        po_taxes = [
                            tax.id for tax in existing_po_line.taxes_id]
                        [po_taxes.append((tax.id))
                         for tax in line.taxes_id]
                        existing_po_line.taxes_id = \
                            [(6, 0, po_taxes)]
                    else:
                        line.copy(default=default)
            for order in purchase_orders:
                order.sudo().button_cancel()
                order.sudo().unlink()
        elif self.merge_type == 'merge_cancel':
           
            po = self.purchase_order_id
            for order in purchase_orders:
                if order == po:
                    continue
                for line in order.order_line:
                    default = {'order_id': self.purchase_order_id.id, 'sequence': sec}
                    existing_po_line = False
                    if po.order_line and self.sumar_producto:
                        for po_line in po.order_line:
                            if not line.display_type and line.product_id == po_line.product_id and \
                                    line.price_unit == po_line.price_unit:
                                existing_po_line = po_line
                                break
                    if existing_po_line:
                        existing_po_line.product_qty += line.product_qty
                        po_taxes = [
                            tax.id for tax in existing_po_line.taxes_id]
                        [po_taxes.append((tax.id))
                         for tax in line.taxes_id]
                        existing_po_line.taxes_id = \
                            [(6, 0, po_taxes)]
                    else:
                        line.copy(default=default)
            for order in purchase_orders:
                if order != po:
                    order.sudo().button_cancel()
        else:
            
            po = self.purchase_order_id
            for order in purchase_orders:
                if order == po:
                    continue
                for line in order.order_line:
                    default = {'order_id': self.purchase_order_id.id, 'sequence': sec}
                    existing_po_line = False
                    if po.order_line and self.sumar_producto:
                        for po_line in po.order_line:
                            if not line.display_type and line.product_id == po_line.product_id and \
                                    line.price_unit == po_line.price_unit:
                                existing_po_line = po_line
                                break
                    if existing_po_line:
                        existing_po_line.product_qty += line.product_qty
                        po_taxes = [
                            tax.id for tax in existing_po_line.taxes_id]
                        [po_taxes.append((tax.id))
                         for tax in line.taxes_id]
                        existing_po_line.taxes_id = \
                            [(6, 0, po_taxes)]
                    else:
                        line.copy(default=default)
            for order in purchase_orders:
                if order != po:
                    order.sudo().button_cancel()
                    order.sudo().unlink()
