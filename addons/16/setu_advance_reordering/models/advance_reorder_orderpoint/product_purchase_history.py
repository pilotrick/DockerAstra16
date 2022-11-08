from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ProductPurchaseHistory(models.Model):
    _name = "product.purchase.history"
    _description = """
    -This model is used to keep product purchase history which we highlights in order points
    -Purchase history will be updated time to time by cron or manual"""

    partner_id = fields.Many2one("res.partner","Vendor")
    product_id = fields.Many2one("product.product", "Product")
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    orderpoint_id = fields.Many2one("stock.warehouse.orderpoint", "Order Point", ondelete='cascade')
    purchase_id = fields.Many2one("purchase.order", "Purchase Order")
    po_qty = fields.Float("PO Qty")
    purchase_price = fields.Float("Purchase Price")
    currency_id = fields.Many2one("res.currency", "Currency")
    po_date = fields.Date("Purchase Date")
    lead_time = fields.Float("Lead Time")

    def update_product_purchase_history(self):
        end_date = datetime.now().date()
        start_date = end_date.replace(day=1)
        # category_ids = company_ids = {}
        # if self.product_category_ids:
        #     categories = self.env['product.category'].search([('id', 'child_of', self.product_category_ids.ids)])
        #     category_ids = set(categories.ids) or {}
        # products = self.product_ids and set(self.product_ids.ids) or {}

        # if self.company_ids:
        #     companies = self.env['res.company'].search([('id', 'child_of', self.company_ids.ids)])
        #     company_ids = set(companies.ids) or {}
        # else:
        #     company_ids = set(self.env.context.get('allowed_company_ids', False) or self.env.user.company_ids.ids) or {}

        # warehouses = self.warehouse_ids and set(self.warehouse_ids.ids) or {}
        query = """
                        Select * from update_product_purchase_history('{}','{}','%s','%s','%s')
                    """ % (
        start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), self.env.user.id)
        self._cr.execute(query)

        ## calcute lead times
        # domain = []
        # if products:
        #     domain.append(('product_id', 'in', products))
        # if warehouses:
        #     domain.append(('warehouse_id', 'in', warehouses))

        orderpoints = self.env['stock.warehouse.orderpoint'].search([])
        orderpoints and orderpoints._calculate_lead_time()



