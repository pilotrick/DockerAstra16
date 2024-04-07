# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
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
    CosteEnDestino = fields.Float(string='Coste en destino', tracking=True)
    TipoDivision = fields.Selection([('cost','Costo'),('weight','Peso'),('volume','Volumen'),('amount','Cantidad')], string='Tipo de Costeo', required=True, related='product_purchase.metodoCosteo')
    Gravamen = fields.Float(string='Gravamen')
    GestionAduanal = fields.Float(string='Gestion Aduanal')
    MontoTotalLiq = fields.Float(string='Total de Gastos', readonly=True)
    product_purchase = fields.One2many('requisicion.compra.productos', 'id_purchase', string='Productos')
    product_info = fields.One2many('requisicion.compra.productos.info', 'product_id_info', string="Información de Productos")
    product_total = fields.One2many('requisicion.compra.productos.total', 'product_id_total', string="Liquidación Total")
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('requisicion.compra')
        return super().create(vals)
    
    @api.onchange('FleteTerreste','FleteMaritimo', 'CosteEnDestino', 'GestionAduanal')
    def compute_sum_total(self):
        for record in self:
            if record.FleteTerreste or record.FleteMaritimo or record.CosteEnDestino or record.GestionAduanal:
                record.MontoTotalLiq = record.FleteMaritimo + record.FleteTerreste + record.GestionAduanal + record.CosteEnDestino
              
    
    def compute_total(self):
        
        TotalAdjustementLines = self.env['requisicion.compra.productos.total']
        TotalAdjustementLines.search([('product_id_total', 'in', self.ids)]).unlink()
        
        dataTotal={}
        for rec in self:
            for inf in rec.product_info:
                dataTotal = {
                    "product_id_total": rec.id,
                    "productTotal": inf.product,
                    "montoTotal": inf.TotalMontoTotalLiq,
                    "cantidad": inf.TotalProductCantidad,
                    "PrecioViejo": inf.unit,
                }
                TotalAdjustementLines.create(dataTotal)
        
        AdjustementLines = self.env['requisicion.compra.productos.info']
        AdjustementLines.search([('product_id_info', 'in', self.ids)]).unlink()
        
        data={}
        for rec in self:
            for p in rec.product_purchase:
                data = {
                    "product_id_info": rec.id,
                    "product": p.name,
                    "TotalProductVolumen": p.ProductVolumen,
                    "TotalProductWeight": p.ProductWeight,
                    "TotalProductCantidad": p.ProductCantidad,
                    "TotalFleteMaritimo": rec.FleteMaritimo,
                    "TotalFleteTerreste": rec.FleteTerreste,
                    "TotalGestionAduanal": rec.GestionAduanal,
                    "gravamen_info": p.ProductGravamen,
                    "TotalProductGravamen": rec.Gravamen,
                    "unit": p.precio_unidad,
                }
                AdjustementLines.create(data)
                
            for val in rec.product_info:
                for line in rec.product_total:
                    
                    if rec.TipoDivision == 'amount':
                        for value in self.browse(self.ids):
                            suma_amount = 0.0
                            total = 0.0
                            liq_total = 0.0
                            for i in value.product_info:
                                total += i.TotalProductCantidad
                                liq_total += (i.TotalMontoTotalLiq)
                                suma_amount = total
                                
                            liq = rec.FleteMaritimo + rec.FleteTerreste + rec.GestionAduanal
                            val.TotalMontoTotalLiq = (liq / suma_amount) * val.TotalProductCantidad
                            val.TotalFleteTerreste = (rec.FleteTerreste / suma_amount) * val.TotalProductCantidad
                            val.TotalFleteMaritimo = (rec.FleteMaritimo / suma_amount) * val.TotalProductCantidad
                            val.TotalGestionAduanal = (rec.GestionAduanal / suma_amount) * val.TotalProductCantidad
                            rec.MontoTotalLiq = liq + rec.CosteEnDestino
                            
                            amount_total = line.PrecioViejo + line.montoTotal
                            line.PrecioNuevo = amount_total
                            line.TotalMontoTotalLiqPorArticulo = amount_total
                        
                        for res in rec.product_info.filtered(lambda x: x.gravamen_info):
                            registry = len(rec.product_purchase.filtered(lambda x: x.ProductGravamen))
                            var1 = rec.FleteMaritimo + rec.FleteTerreste + rec.GestionAduanal
                            var2 = (var1 / suma_amount)
                            res.TotalMontoTotalLiq = (var2 * res.TotalProductCantidad)
                            
                            # total_gravamen = (val.TotalProductGravamen/100) * liq
                            var_gravamen = rec.Gravamen / registry
                            val.TotalProductGravamen = var_gravamen
                            res.TotalMontoTotalLiq += var_gravamen
                            
                            rec.MontoTotalLiq += var_gravamen
                            
                            line.PrecioNuevo = amount_total
                            line.TotalMontoTotalLiqPorArticulo = amount_total
                            for p in rec.product_purchase:
                                p.gravamen = var_gravamen
                        
                    elif rec.TipoDivision == 'weight':
                        for value in self.browse(self.ids):
                            suma_weight= 0.0
                            total = 0.0
                            liq_total = 0.0
                            for i in value.product_info:
                                total += i.TotalProductWeight
                                liq_total += i.TotalMontoTotalLiq
                                suma_weight = total
                                rec.MontoTotalLiq = liq_total + rec.CosteEnDestino
                        
                            liq = rec.FleteMaritimo + rec.FleteTerreste + rec.GestionAduanal
                            val.TotalMontoTotalLiq = (liq / suma_weight) * val.TotalProductWeight
                            val.TotalFleteTerreste = (rec.FleteTerreste / suma_weight) * val.TotalProductWeight
                            val.TotalFleteMaritimo = (rec.FleteMaritimo / suma_weight) * val.TotalProductWeight
                            val.TotalGestionAduanal = (rec.GestionAduanal / suma_weight) * val.TotalProductWeight
                            rec.MontoTotalLiq = liq + rec.CosteEnDestino
                            
                            weight_total = line.PrecioViejo + line.montoTotal
                            line.PrecioNuevo = weight_total
                            line.TotalMontoTotalLiqPorArticulo = weight_total
                            
                        for res in rec.product_info.filtered(lambda x: x.gravamen_info):
                            registry = len(rec.product_purchase.filtered(lambda x: x.ProductGravamen))
                            var1 = rec.FleteMaritimo + rec.FleteTerreste + rec.GestionAduanal
                            var2 = (var1 / suma_weight)
                            res.TotalMontoTotalLiq = (var2 * res.TotalProductWeight)
                            
                            # total_gravamen = (val.TotalProductGravamen/100) * liq
                            var_gravamen = rec.Gravamen / registry
                            val.TotalProductGravamen = var_gravamen
                            res.TotalMontoTotalLiq += var_gravamen
                            
                            rec.MontoTotalLiq += var_gravamen
                            
                            line.PrecioNuevo = suma_weight
                            line.TotalMontoTotalLiqPorArticulo = suma_weight
                            for p in rec.product_purchase:
                                p.gravamen = var_gravamen
                        
                    elif rec.TipoDivision == 'volume':
                        for value in self.browse(self.ids):
                            suma_volume= 0.0
                            total = 0.0
                            liq_total = 0.0
                            for i in value.product_info:
                                total += i.TotalProductVolumen
                                liq_total += i.TotalMontoTotalLiq
                                suma_volume = total
                                rec.MontoTotalLiq = liq_total + rec.CosteEnDestino
                        
                            liq = rec.FleteMaritimo + rec.FleteTerreste + rec.GestionAduanal
                            val.TotalMontoTotalLiq =  (liq / suma_volume) * val.TotalProductVolumen
                            val.TotalFleteTerreste = (rec.FleteTerreste / suma_volume) * val.TotalProductVolumen
                            val.TotalFleteMaritimo = (rec.FleteMaritimo / suma_volume) * val.TotalProductVolumen
                            val.TotalGestionAduanal = (rec.GestionAduanal / suma_volume) * val.TotalProductVolumen
                            rec.MontoTotalLiq = liq + rec.CosteEnDestino
                            
                            volume_total = line.PrecioViejo + line.montoTotal
                            line.PrecioNuevo = volume_total
                            line.TotalMontoTotalLiqPorArticulo = volume_total
                        
                        for res in rec.product_info.filtered(lambda x: x.gravamen_info):
                            registry = len(rec.product_purchase.filtered(lambda x: x.ProductGravamen))
                            var1 = rec.FleteMaritimo + rec.FleteTerreste + rec.GestionAduanal
                            var2 = (var1 / suma_volume)
                            res.TotalMontoTotalLiq = (var2 * res.TotalProductVolumen)
                            
                            # total_gravamen = (val.TotalProductGravamen/100) * liq
                            var_gravamen = rec.Gravamen / registry
                            val.TotalProductGravamen = var_gravamen
                            res.TotalMontoTotalLiq += var_gravamen
                            
                            rec.MontoTotalLiq += var_gravamen
                            
                            line.PrecioNuevo = suma_volume
                            line.TotalMontoTotalLiqPorArticulo = suma_volume
                            for p in rec.product_purchase:
                                p.gravamen = var_gravamen
                    
                    elif rec.TipoDivision == 'cost':
                        for value in self.browse(self.ids):
                            suma_cost= 0.0
                            liq_total = 0.0
                            for i in value.product_info:
                                suma_cost += i.unit
                                liq_total += i.TotalMontoTotalLiq
                                rec.MontoTotalLiq = liq_total + rec.CosteEnDestino
                                
                            liq = rec.FleteMaritimo + rec.FleteTerreste + rec.GestionAduanal
                            val.TotalMontoTotalLiq =  (liq / suma_cost) * val.unit
                            val.TotalFleteTerreste = (rec.FleteTerreste / suma_cost) * val.unit
                            val.TotalFleteMaritimo = (rec.FleteMaritimo / suma_cost) * val.unit
                            val.TotalGestionAduanal = (rec.GestionAduanal / suma_cost) * val.unit
                            rec.MontoTotalLiq = liq + rec.CosteEnDestino
                            
                            cost_total = line.PrecioViejo + line.montoTotal
                            line.PrecioNuevo = cost_total
                            line.TotalMontoTotalLiqPorArticulo = cost_total
                        
                        for res in rec.product_info.filtered(lambda x: x.gravamen_info):
                            registry = len(rec.product_purchase.filtered(lambda x: x.ProductGravamen))
                            var1 = rec.FleteMaritimo + rec.FleteTerreste + rec.GestionAduanal
                            var2 = (var1 / suma_cost)
                            res.TotalMontoTotalLiq = (var2 * res.unit)
                            
                            # total_gravamen = (val.TotalProductGravamen/100) * liq
                            var_gravamen = rec.Gravamen / registry
                            val.TotalProductGravamen = var_gravamen
                            res.TotalMontoTotalLiq += var_gravamen
                            
                            rec.MontoTotalLiq += var_gravamen
                            
                            line.PrecioNuevo = suma_cost
                            line.TotalMontoTotalLiqPorArticulo = suma_cost
                            for p in rec.product_purchase:
                                p.gravamen = var_gravamen
                             
                    
class LiquidacionProducto(models.Model):
    _name = 'requisicion.compra.productos'
    _description = 'Liquidacion de compras'

    name = fields.Char(string='Producto')
    ProductVolumen = fields.Float(string='Volumen', required=True)
    ProductWeight = fields.Float(string='Peso', required=True)
    ProductCantidad = fields.Integer(string='Cantidad', required=True)
    ProductGravamen = fields.Boolean(string='Tiene Gravamen')
    id_purchase = fields.Many2one('requisicion.compra', string="Product ID")
    gravamen = fields.Float(string='Gravamen', readonly=True)
    precio_unidad = fields.Float(string='Precio Por Unidad', required=True)
    metodoCosteo = fields.Selection([('cost','Costo'),('weight','Peso'),('volume','Volumen'),('amount','Cantidad')], string='Tipo de Costeo', required=True)
    
class LiquidacionProductoInfo(models.Model):
    _name = 'requisicion.compra.productos.info'
    _description = 'Liquidacion de compras'

    product = fields.Char(string='Producto', readonly=True)
    TotalProductVolumen = fields.Float(string='Volumen', readonly=True)
    TotalProductWeight = fields.Float(string='Peso', readonly=True)
    TotalProductCantidad = fields.Integer(string='Cantidad', readonly=True)
    TotalProductGravamen = fields.Float(string='Tiene Gravamen', readonly=True)
    TotalFleteTerreste = fields.Float(string='Flete Terrestre', readonly=True)
    TotalFleteMaritimo = fields.Float(string='Flete Maritimo', readonly=True)
    TotalGestionAduanal = fields.Float(string='Gestion Aduanal', readonly=True)
    TotalMontoTotalLiq = fields.Float(string='Total de Gastos', readonly=True)
    product_id_info = fields.Many2one('requisicion.compra', string="Product ID")
    gravamen_info = fields.Boolean(string='Tiene Gravamen')
    unit = fields.Float(string='Unit')
    
class LiquidacionProducto(models.Model):
    _name = 'requisicion.compra.productos.total'
    _description = 'Liquidacion de compras'

    productTotal = fields.Char(string='Producto', readonly=True)
    PrecioViejo = fields.Float(string='Precio(Viejo)')
    PrecioNuevo = fields.Float(string='Precio(Nuevo)', readonly=True)
    TotalMontoTotalLiqPorArticulo = fields.Float(string='Total de Gastos por Articulo', readonly=True)
    product_id_total = fields.Many2one('requisicion.compra', string="Product ID")
    montoTotal = fields.Float(string="Monto total", readonly=True)
    cantidad = fields.Integer(string="cantidad", readonly=True)
    total_product = fields.Many2one('requisicion.compra.productos.info', string="total")
