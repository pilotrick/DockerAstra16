from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ProductSalesHistory(models.Model):
    _name = "product.sales.history"
    _description = """update_product_sales_history
    -This model is used to keep the product sales history which we highlights in order points
    -Sales history will be updated time to time by cron or manual"""

    product_id = fields.Many2one("product.product","Product")
    warehouse_id = fields.Many2one("stock.warehouse","Warehouse")
    orderpoint_id = fields.Many2one("stock.warehouse.orderpoint", "Order Point", ondelete='cascade')
    sales_qty = fields.Float("Sales Qty")
    total_orders = fields.Integer("Total Sales Order")
    average_daily_sale = fields.Float("Average Daily Sales")
    max_daily_sale_qty = fields.Float("Maximum Daily Sales Qty")
    min_daily_sale_qty =fields.Float("Minimum Daily Sales Qty")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    duration = fields.Integer("Duration In Days")

    def update_product_sales_history(self):
        end_date = datetime.now().date()
        start_date = end_date.replace(day=1)
        query = """
            Select * from update_product_sales_history('{}','{}','{}','{}','%s','%s', %s)
        """ % (
        start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), self.env.user.id)
        self._cr.execute(query)

        ## calcute lead times
        domain = []
        orderpoints = self.env['stock.warehouse.orderpoint'].search(domain)
        orderpoints and orderpoints.calculate_sales_average_max()
