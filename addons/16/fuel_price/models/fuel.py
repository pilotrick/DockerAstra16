from odoo import api, fields, models, _
import requests
import json
from odoo.exceptions import Warning

class FuelType(models.Model):
    _name = 'fuel.type'

    name = fields.Char('Fuel Type')
    price_ids = fields.One2many('fuel.detail', 'type_id')
    
class FuelDetail(models.Model):
    _name = 'fuel.detail'
    _order = 'date'

    date = fields.Date('date')
    price = fields.Float('Price')
    type_id = fields.Many2one('fuel.type','price_ids', ondelete='cascade')

class ResCompany(models.Model):
    _inherit = 'res.company'

    access_token = fields.Char('Access Token')

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    fuel_id = fields.Many2one('fuel.type')
   
    def fetch_fuel(self):
        access_token = self.env.company.access_token
        url = 'https://api.indexa.do/api/fuels'
        
        if access_token:
            headers = {
                'x-access-token': access_token,
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                raise Warning(_('API Key is not valid or is expired / revoked.'))
            
            res = json.loads(response.text)
            for rec in res.get('data'):
                FuelType = self.env['fuel.type'].search([('name', '=', rec.get('name'))])
                if not FuelType:
                    FuelType.create({'name': rec.get('name'),
                        'price_ids': [(0, 0, {'date': rec.get('date'),'price': rec.get('price')})]
                        })
                else:
                    FuelType.write({'price_ids': [(0, 0, {'date': rec.get('date'),'price': rec.get('price')})]})    
        else:
            raise Warning(_('Set the access token in company first'))
