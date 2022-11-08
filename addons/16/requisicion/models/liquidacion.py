# -*- coding: utf-8 -*-

from xml.dom.expatbuilder import parseString
from odoo import api, fields, models, tools, _
from datetime import datetime

class Liquidacion(models.Model):
    _name = 'requisicion.compra'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Liquidacion de compras'

    name = fields.Char('Name', default=lambda self: _('New'),copy=False, readonly=True, tracking=True)
    fecha = fields.Date(string='Fecha')
    Proveedor = fields.Char(string='Proveedor')
    FleteTerreste = fields.Float(string='Flete Terrestre')
    FleteMaritimo = fields.Float(string='Flete Maritimo')
    CosteEnDestino = fields.Float(string='Coste en destino', readonly=True, tracking=True)
    Gravamen = fields.Float(string='Gravamen')
    GestionAduanal = fields.Integer(string='Gestion Aduanal')
    MontoTotalLiq = fields.Float(string='Total de Gastos', related='product_info.TotalMontoTotalLiq')
    product_purchase = fields.One2many('requisicion.compra.productos', 'id_purchase', string='Productos')
    product_info = fields.One2many('requisicion.compra.productos.info', 'product_id_info', string="Información de Productos")
    product_total = fields.One2many('requisicion.compra.productos.total', 'product_id_total', string="Liquidación Total")
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.landed.cost')
        return super().create(vals)
    
    
    def compute_total(self):
        AdjustementLines = self.env['requisicion.compra.productos.info']
        AdjustementLines.search([('product_id_info', 'in', self.ids)]).unlink()
        
        TotalAdjustementLines = self.env['requisicion.compra.productos.total']
        TotalAdjustementLines.search([('product_id_total', 'in', self.ids)]).unlink()
        
        data={}
        dataTotal={}
        for rec in self:
            for p in rec.product_purchase:
                data = {
                    "product_id_info": rec.id,
                    "product": p.name,
                    "TotalProductVolumen": p.ProductVolumen,
                    "TotalProductWeight": p.ProductWeight,
                    "TotalProductCantidad": p.ProductCantidad,
                    "division_cost": p.TipoDivision,
                }
                AdjustementLines.create(data)
                
            for inf in rec.product_info:
                
                dataTotal = {
                    "product_id_total": rec.id,
                    "productTotal": inf.product,
                    "montoTotal": inf.TotalMontoTotalLiq,
                    "cantidad": inf.TotalProductCantidad,
                }
                TotalAdjustementLines.create(dataTotal)
                    
                    #volumen entre cantidad y se multiplica por ek coste total
                    #costo total entre cantidad es igual a costo unitario
                
            for line in rec.product_purchase:
                for val in rec.product_info:
                
                    if line.TipoDivision == 'amount':
                        val.TotalMontoTotalLiq = val.TotalFleteMaritimo + val.TotalFleteTerreste + val.TotalGestionAduanal
                        per_unit = (line.ProductCantidad / val.TotalMontoTotalLiq)
                        val.TotalMontoTotalLiq += per_unit
                        
                        if line.ProductGravamen == True:
                            total = (line.gravamen/100) * val.TotalMontoTotalLiq
                            val.TotalMontoTotalLiq += total
                        
                    elif line.TipoDivision == 'weight':
                        val.TotalMontoTotalLiq = val.TotalFleteMaritimo + val.TotalFleteTerreste + val.TotalGestionAduanal
                        per_unit = (line.ProductWeight / line.ProductCantidad)
                        value = per_unit * val.TotalMontoTotalLiq
                        val.TotalMontoTotalLiq += value
                        
                        if line.ProductGravamen == True:
                            total = (line.gravamen/100) * val.TotalMontoTotalLiq
                            val.TotalMontoTotalLiq += total
                        
                    elif line.TipoDivision == 'volume':
                        val.TotalMontoTotalLiq = val.TotalFleteMaritimo + val.TotalFleteTerreste + val.TotalGestionAduanal
                        per_unit = (line.ProductVolumen / line.ProductCantidad)
                        value = per_unit * val.TotalMontoTotalLiq
                        val.TotalMontoTotalLiq += value
                        
                        if line.ProductGravamen == True:
                            total = (line.gravamen/100) * val.TotalMontoTotalLiq
                            val.TotalMontoTotalLiq += total
                    
                    elif line.TipoDivision == 'cost':
                        val.TotalMontoTotalLiq = val.TotalFleteMaritimo + val.TotalFleteTerreste + val.TotalGestionAduanal
                        per_unit = val.TotalMontoTotalLiq / 100
                        val.method_cost = per_unit
                        
                        
                    
class LiquidacionProducto(models.Model):
    _name = 'requisicion.compra.productos'
    _description = 'Liquidacion de compras'

    name = fields.Char(string='Producto')
    ProductVolumen = fields.Float(string='Volumen')
    ProductWeight = fields.Float(string='Peso')
    ProductCantidad = fields.Integer(string='Cantidad')
    ProductGravamen = fields.Boolean(string='Tiene Gravamen')
    TipoDivision = fields.Selection([('cost','Costo'),('weight','Peso'),('volume','Volumen'),('amount','Cantidad')], string='Tipo de Costeo')
    id_purchase = fields.Many2one('requisicion.compra', string="Product ID")
    gravamen = fields.Float(string='Gravamen', related='id_purchase.Gravamen')
    
class LiquidacionProductoInfo(models.Model):
    _name = 'requisicion.compra.productos.info'
    _description = 'Liquidacion de compras'

    product = fields.Char(string='Producto', readonly=True)
    TotalProductVolumen = fields.Float(string='Volumen', readonly=True)
    TotalProductWeight = fields.Float(string='Peso', readonly=True)
    TotalProductCantidad = fields.Integer(string='Cantidad', readonly=True)
    TotalProductGravamen = fields.Float(string='Tiene Gravamen', related='product_id_info.Gravamen', readonly=True)
    TotalFleteTerreste = fields.Float(string='Flete Terrestre', related='product_id_info.FleteTerreste', readonly=True)
    TotalFleteMaritimo = fields.Float(string='Flete Maritimo', related='product_id_info.FleteMaritimo', readonly=True)
    TotalGestionAduanal = fields.Integer(string='Gestion Aduanal', related='product_id_info.GestionAduanal', readonly=True)
    TotalMontoTotalLiq = fields.Float(string='Total de Gastos')
    product_id_info = fields.Many2one('requisicion.compra', string="Product ID")
    product_id_purchase = fields.Many2one('requisicion.compra.productos', string="purchase")
    division_cost = fields.Selection([('cost','Costo'),('weight','Peso'),('volume','Volumen'),('amount','Cantidad')], string="Metodo de COsteo", readonly=True)
    method_cost = fields.Float(string="(%) del costo", readonly=True)
    
    montoArticulo = fields.Float(string="Articulo")
    # def calculate (self):
    #     for rec in self:
    #         rec.montoArticulo = (rec.TotalMontoTotalLiq / rec.TotalProductCantidad)
    
    totales = fields.Float(string='Total')
    
    # @api.onchange('TotalMontoTotalLiq')
    def sum_tol(self):
        for line in self:
            
        # self.totales = sum(self.env['requisicion.compra.productos.info'].search(['TotalMontoTotalLiq']).mapped('totales'))
            line.totales = sum(line.TotalMontoTotalLiq.mapped('totales'))
        # self.totales = 0.0
        # for s in range(0,len(self.TotalMontoTotalLiq)):
        #     self.totales = self.totales + self.TotalMontoTotalLiq[s]

class LiquidacionProducto(models.Model):
    _name = 'requisicion.compra.productos.total'
    _description = 'Liquidacion de compras'

    productTotal = fields.Char(string='Producto')
    PrecioViejo = fields.Float(string='Precio(Viejo)')
    PrecioNuevo = fields.Float(string='Precio(Nuevo)', compute="compute_monto_total")
    TotalMontoTotalLiqPorArticulo = fields.Float(string='Total de Gastos por Articulo')
    product_id_total = fields.Many2one('requisicion.compra', string="Product ID")
    montoTotal = fields.Float(string="Monto total")
    cantidad = fields.Integer(string="cantidad")
    product_purchase_id = fields.Many2one('requisicion.compra.productos')
    total_product = fields.Many2one('requisicion.compra.productos.info', string="total")
    
    def compute_monto_total(self):
        for rec in self:
            rec.PrecioNuevo = rec.PrecioViejo + rec.TotalMontoTotalLiqPorArticulo
            
    
    
    
    
