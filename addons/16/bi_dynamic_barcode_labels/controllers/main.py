# -*- coding: utf-8 -*-

import json

from odoo.http import Controller, route, request



# -*- coding: utf-8 -*-

import json

from odoo.http import Controller, route, request


class ProductDataController(Controller):
    @route([
        '/zebra_label/report'
    ], type='json')
    def product_data(self, **params):
        data = []
        info_prod = request.env['product.product'].search(
            [('id', '=', params.get("product"))])
        info_tmp = request.env['product.template'].search(
            [('id', '=', info_prod.product_tmpl_id.id)])
        
        info_company = request.env['res.company'].search(
            [('id', '=', params.get("company"))])
        
        price_list = request.env['product.pricelist.item'].search(
            [('product_id', '=', info_prod.id)], limit=1)
        price = price_list.fixed_price if price_list else info_prod.lst_price
        data ="""^XA
^CF0,22
^FB205,2,0,C
^FO10,10
^FD%s^FS
^CF0,17
^FO220,12^FDTel. %s^FS
^FB393,2,0,C
^CF0,20
^FO20,40^
^FD%s^FS
^CF0,18
^BY2,2,60^FO40,80
^BC^FD%s^FS
^CF0,25
^FB150,1,0,C^FO20,170
^FD%s ^FS
^XZ""" % (
        info_company.name.upper(),
        info_company.phone,
        info_prod.name.upper(),
        info_prod.barcode,
        "RD${:,.2f}".format(price)) 
        data = data.replace("\n", "") * params.get("qty")
        return {'data': data}
        
                
     
#         for i in range(1, int(qty)+1):
#             data +="""^XA
# ^CF0,25
# ^FB295,2,0,C^FO30,10
# ^FD%s^FS
# ^CF0,20
# ^FO250,15^FDTel. %s^FS
# ^FB390,2,0,C^FO60,40
# ^FD%s^FS
# ^CF0,18
# ^BY2,2,70
# ^FO120,100^BC^FD%s^FS
# ^CF0,20
# ^FB290,1,0,C
# ^FO20,70^FD$%s US^FS^XZ^XZ""" % (
#     info_company.name.upper(), 
#     info_company.phone,
#     info_tmp.name,
#     info_prod.default_code,  
#     info_tmp.usd_price )
#         return {'data': data.replace('\n','')}
