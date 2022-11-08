from odoo import fields, models, api, _, registry, SUPERUSER_ID
from odoo.exceptions import ValidationError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from statistics import mean
from odoo.tools import float_compare, frozendict, split_every
from odoo.addons.stock.models.stock_rule import ProcurementException
from psycopg2 import OperationalError
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)

class StockWarehouseOrderpoint(models.Model):
    _name = "stock.warehouse.orderpoint"
    _inherit = ['stock.warehouse.orderpoint', 'mail.thread', 'mail.activity.mixin']

    def _default_avg_sale_calculation_base(self):
        para = self.env['ir.config_parameter'].sudo().search([('key','=','setu_advance_reordering.average_sale_calculation_base')])
        return para and para.value or 'quarterly_average'

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain="[('type', '=', 'product'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        ondelete='cascade', required=True, check_company=True, change_default=True)

    suggested_min_qty = fields.Integer("Suggested Min Qty")
    suggested_max_qty = fields.Integer("Suggested Max Qty")
    ads_qty = fields.Float("Average Daily Sales", change_default=True,)
    max_daily_sale_qty = fields.Float("Maximum Daily Sales")

    # seven_days_ads = fields.Float("7 Days ADS")
    # fifteen_days_ads = fields.Float("15 Days ADS")
    # thirty_days_ads = fields.Float("30 Days ADS")
    # sixty_days_ads = fields.Float("60 Days ADS")
    # quarterly_days_ads = fields.Float("90 Days ADS")
    # onetwenty_days_ads = fields.Float("120 Days ADS")
    # half_yearly_ads = fields.Float("180 Days ADS")
    # yearly_ads = fields.Float("365 Days ADS")
    #
    # seven_days_max_sale = fields.Float("7 Days MDS")
    # fifteen_max_sale = fields.Float("15 Days MDS")
    # thirty_max_sale = fields.Float("30 Days MDS")
    # sixty_max_sale = fields.Float("60 Days MDS")
    # quarterly_max_sale = fields.Float("90 Days MDS")
    # onetwenty_max_sale = fields.Float("120 Days MDS")
    # half_yearly_max_sale = fields.Float("180 Days MDS")
    # yearly_max_sale = fields.Float("365 Days MDS")

    max_lead_time = fields.Integer("Maximum Lead Time")
    avg_lead_time = fields.Integer("Average Lead Time")
    product_sales_history_ids = fields.One2many("product.sales.history","orderpoint_id","Sales History")
    product_purchase_history_ids = fields.One2many("product.purchase.history","orderpoint_id","Purchase History")
    safety_stock = fields.Float("Safety Stock", change_default=True, )
    buffer_days = fields.Integer("Buffer Days", help="""
        If you will add buffer days then system will add "buffer days * average daily sales" in to the maximum ordered quantity calculation
    """, change_default=True, )
    suggested_safety_stock = fields.Float("Suggested Safety Stock", change_default=True, )
    vendor_selection_strategy = fields.Selection([('NA','Not Applicable'),
                                                  ("cheapest", "Cheapest vendor"),
                                                  ("quickest", "Quickest vendor"),
                                                  ("specific_vendor", "Specific vendor")],
                                                  string="Vendor selection strategy", default="NA",
                                                   help="""This field is useful when purchase order is created from order points 
                                                   that time system checks about the vendor which is suitable for placing an order 
                                                   according to need. Whether quickest vendor, cheapest vendor or specific vendor is suitable 
                                                   for the product"""
                                                  )
    partner_id = fields.Many2one("res.partner","Vendor")
    average_sale_calculation_base = fields.Selection([
        ("weekly_average", "Weekly Sales"),
        ("fifteen_days_average", "15 Days Sales"),
        ("monthly_average", "30 Days Sales"),
        ("bi_monthly_average", "60 Days Sales"),
        ("quarterly_average", "90 Days Sales"),
        ("onetwenty_days_average", "120 Days Sales"),
        ("six_month_averagy", "180 Days Sales"),
        ("annual_average", "Annual Sales")],
        default=_default_avg_sale_calculation_base, change_default=True, string="Get Average Sales From")
    document_creation_option = fields.Selection([('ict', 'Inter Company Transfer'),
                                                 ('iwt', 'Inter Warehouse Transfer'),
                                                 ('po', 'Purchase Order')], string="Create", change_default=True,
                                                default='po',
                                                help="Inter Company Transfer(ICT) - System will create an Inter "
                                                     "Company Transfer.\nInter Warehouse Transfer(IWT) - System will "
                                                     "create an Inter Warehouse Transfer.\nPurchase Order - System "
                                                     "will create a Purchase Order.\n\nNote - ICT and IWT will be "
                                                     "worked as per the configuration of Inter Company Channel.")


    @api.constrains('max_daily_sale_qty', 'max_lead_time')
    def _check_leadtime_ads(self):
        for orderpoint in self:
            if orderpoint.max_daily_sale_qty < orderpoint.ads_qty:
                raise ValidationError(
                    _('Incorrect Max daily sales qty: Maximum daily sales must be greater than average daily sales!')
                )

            if orderpoint.max_lead_time < orderpoint.avg_lead_time:
                raise ValidationError(
                    _('Incorrect Max lead time: Maximum lead time must be greater than average lead time!')
                )

    def _calculate_lead_time(self):
        for orderpoint_id in self.ids:
            orderpoint = self.browse(orderpoint_id)
            orderpoint.write({
                    'avg_lead_time' : orderpoint.product_purchase_history_ids and mean(orderpoint.product_purchase_history_ids.mapped('lead_time')) or 0.0,
                    'max_lead_time' : orderpoint.product_purchase_history_ids and max(orderpoint.product_purchase_history_ids.mapped('lead_time')) or 0.0
             })

    def get_date(self, days):
        return (datetime.today() - relativedelta(days=days)).date()

    def get_sales_data(self, start_date, end_date):
        filtered_data = self.product_sales_history_ids.filtered(
            lambda x: x.start_date >= start_date and x.start_date <= end_date)
        filtered_avg_data = filtered_data.mapped('average_daily_sale')
        filtered_max_data = filtered_data.mapped('max_daily_sale_qty')
        avg_sale = filtered_avg_data and mean(filtered_avg_data) or 0.0
        max_sale = filtered_max_data and max(filtered_max_data) or 0.0
        return avg_sale, max_sale

    def calculate_sales_average_max(self):
        i =0
        for orderpoint_id in self.ids:
            orderpoint = self.browse(orderpoint_id)
            # end_date = datetime.now().date()
            # seven_days_start = self.get_date(7)
            # seven_avg, seven_max = orderpoint.get_sales_data(seven_days_start, end_date)
            # fifteen_days_start = self.get_date(15)
            # fifteen_avg, fifteen_max = orderpoint.get_sales_data(fifteen_days_start, end_date)
            # monthly_start = self.get_date(30)
            # monthly_avg, monthly_max = orderpoint.get_sales_data(monthly_start, end_date)
            # bi_monthly_start = self.get_date(60)
            # bi_monthly_avg, bi_monthly_max = orderpoint.get_sales_data(bi_monthly_start, end_date)
            # quarterly_start = self.get_date(90)
            # quarterly_days_ads, quarterly_max_sale = orderpoint.get_sales_data(quarterly_start, end_date)
            # onetwenty_start = self.get_date(120)
            # onetwenty_days_ads, onetwenty_max_sale = orderpoint.get_sales_data(onetwenty_start, end_date)
            # half_yearly_start = self.get_date(180)
            # half_yearly_ads, half_yearly_max_sale = orderpoint.get_sales_data(half_yearly_start, end_date)
            # yearly_start = self.get_date(365)
            # yearly_ads, yearly_max_sale = orderpoint.get_sales_data(yearly_start, end_date)
            # vals = {
            #     'seven_days_ads' : seven_avg,
            #     'seven_days_max_sale' : seven_max,
            #     'fifteen_days_ads': fifteen_avg,
            #     'fifteen_max_sale': fifteen_max,
            #     'thirty_days_ads': monthly_avg,
            #     'thirty_max_sale': monthly_max,
            #     'sixty_days_ads': bi_monthly_avg,
            #     'sixty_max_sale': bi_monthly_max,
            #     'quarterly_days_ads': quarterly_days_ads,
            #     'quarterly_max_sale': quarterly_max_sale,
            #     'onetwenty_days_ads': onetwenty_days_ads,
            #     'onetwenty_max_sale': onetwenty_max_sale,
            #     'half_yearly_ads': half_yearly_ads,
            #     'half_yearly_max_sale': half_yearly_max_sale,
            #     'yearly_ads': yearly_ads,
            #     'yearly_max_sale': yearly_max_sale,
            # }
            # orderpoint.write(vals)
            orderpoint.onchange_avg_sale_lead_time()
            orderpoint.onchange_safety_stock()
            i = i + 1

    def update_product_purchase_history(self):
        query = """
            Select * from update_product_purchase_history('{%s}','{%s}','%s','%s','%s')
        """ % (
        self.product_id.id, self.warehouse_id.id, self.get_date(365).strftime("%Y-%m-%d"),
        datetime.today().strftime("%Y-%m-%d"), self.env.user.id)
        self._cr.execute(query)

    def update_product_sales_history(self):
        start_date = self.get_date(365).strftime("%Y-%m-%d")
        end_date = datetime.today().strftime("%Y-%m-%d")
        period_ids = self.env['reorder.fiscalperiod'].search([('fpstartdate','>=', start_date),('fpstartdate','<=',end_date)])
        for period in period_ids:
            query = """
                Select * from update_product_sales_history('{}','{%s}','{}','{%s}','%s','%s', '%s')
            """ % (
            self.product_id.id, self.warehouse_id.id, period.fpstartdate.strftime("%Y-%m-%d"),
                period.fpenddate.strftime("%Y-%m-%d"), self.env.user.id)
            self._cr.execute(query)

    @api.onchange('document_creation_option')
    def onchange_document_creation_option(self):
        for record in self:
            document_creation_option = record.document_creation_option
            if document_creation_option and document_creation_option != 'po':
                record.vendor_selection_strategy = ''

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            partner_ids = self.product_id.seller_ids.mapped("name").ids
            return {'domain' : { 'partner_id' : [('id','in', partner_ids)] }}

    @api.onchange('average_sale_calculation_base')
    def onchange_average_sale_calculation_base(self):
        ads_qty = max_daily_sale_qty = 0.0
        if self.average_sale_calculation_base:
            if self.average_sale_calculation_base == "weekly_average":
                ads_qty, max_daily_sale_qty = self.get_avg_and_max_sales(7)
            elif self.average_sale_calculation_base == "fifteen_days_average":
                ads_qty, max_daily_sale_qty = self.get_avg_and_max_sales(15)
            elif self.average_sale_calculation_base == "monthly_average":
                ads_qty, max_daily_sale_qty = self.get_avg_and_max_sales(30)
            elif self.average_sale_calculation_base == "bi_monthly_average":
                ads_qty, max_daily_sale_qty = self.get_avg_and_max_sales(60)
            elif self.average_sale_calculation_base == "quarterly_average":
                ads_qty, max_daily_sale_qty = self.get_avg_and_max_sales(90)
            elif self.average_sale_calculation_base == "onetwenty_days_average":
                ads_qty, max_daily_sale_qty = self.get_avg_and_max_sales(120)
            elif self.average_sale_calculation_base == "six_month_averagy":
                ads_qty, max_daily_sale_qty = self.get_avg_and_max_sales(180)
            elif self.average_sale_calculation_base == "annual_average":
                ads_qty, max_daily_sale_qty = self.get_avg_and_max_sales(365)

        self.ads_qty = ads_qty
        self.max_daily_sale_qty = max_daily_sale_qty

    def get_avg_and_max_sales(self, days):
        """
        This method will calculate average and max sales of a period.
        :param days: Number of days.
        :return: It will return average and max sales of a period.
        """
        end_date = datetime.now().date()
        days_start = self.get_date(days)
        days_avg_sales, days_max_sales = self.get_sales_data(days_start, end_date)
        return days_avg_sales, days_max_sales

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     lead_days = 1
    #     if self.partner_id and self.product_id:
    #         supplier_info = self.product_id.seller_ids.filtered(lambda supplier: supplier.name == self.partner_id)
    #         if supplier_info:
    #             lead_days = supplier_info[0].delay
    #     self.lead_days = lead_days

    # @api.depends('max_daily_sale_qty', 'ads_qty', 'max_lead_time', 'avg_lead_time')
    @api.onchange('max_daily_sale_qty','ads_qty','max_lead_time','avg_lead_time')
    def onchange_avg_sale_lead_time(self):
        self.suggested_safety_stock = round(((self.max_daily_sale_qty * self.max_lead_time) - (self.ads_qty * self.avg_lead_time)),0) or 0

    # @api.depends('suggested_safety_stock')
    @api.onchange('suggested_safety_stock')
    def onchange_safety_stock(self):
        self.suggested_min_qty = ((self.avg_lead_time * self.ads_qty) + self.suggested_safety_stock) or 0
        self.suggested_max_qty = (self.suggested_min_qty + (self.buffer_days * self.ads_qty)) or 0

    @api.onchange('product_min_qty', 'buffer_days', 'safety_stock', 'ads_qty')
    def onchange_min_stock_buffer_days(self):
        self.product_max_qty = round((self.product_min_qty + self.safety_stock + (self.buffer_days * self.ads_qty)),0) or 0
        self.suggested_max_qty = ((self.avg_lead_time * self.ads_qty) + (self.buffer_days * self.ads_qty) + self.suggested_safety_stock) or 0

    def update_order_point_data(self):
        for orderpoint in self:
            vals = {
                'product_min_qty' : orderpoint.suggested_min_qty,
                'safety_stock' : orderpoint.suggested_safety_stock,
                'product_max_qty' : orderpoint.suggested_max_qty,
            }
            orderpoint.write(vals)

    def reset_all_data(self):
        vals = {
            'avg_lead_time' : 0,
            'ads_qty' : 0,
            'max_daily_sale_qty' : 0,
            'max_lead_time' : 0,
            # 'product_purchase_history_ids' : [(6, 0, [])],
        }
        self.write(vals)

    @api.model
    def scheduler_recalculate_data(self):
        """
        This method will recalculate order point calculation whenever its scheduler will run.
        :return:
        """
        orderpoints = self.env['stock.warehouse.orderpoint'].search([('product_id.type','=','product')])
        for orderpoint in orderpoints:
            # orderpoint.recalculate_data()
            orderpoint.update_product_purchase_history()
            orderpoint.update_product_sales_history()
            self._cr.commit()
            orderpoint._calculate_lead_time()
            orderpoint.calculate_sales_average_max()
            orderpoint.onchange_average_sale_calculation_base()
            orderpoint.onchange_safety_stock()
            orderpoint.onchange_avg_sale_lead_time()
            orderpoint.onchange_safety_stock()
            if orderpoint.product_id.update_orderpoint:
                orderpoint.update_order_point_data()
        return True

    def recalculate_data(self):
        self.reset_all_data()
        self.update_product_purchase_history()
        self.update_product_sales_history()
        self._calculate_lead_time()
        self.calculate_sales_average_max()
        self.onchange_average_sale_calculation_base()
        self.onchange_safety_stock()
        self.onchange_avg_sale_lead_time()
        self.onchange_safety_stock()

    def create_schedule_activity(self, values):
        """
        This method will create activity for order point.
        :param values: Dictionary of activity values.
        :return: It will return activity object.
        """
        activity_obj = self.env['mail.activity']
        document = "ICT" if self.document_creation_option == 'ict' else "IWT"
        message = "<b>Can't create %s for this orderpoint, because %s channel not found for this company. Create " \
                  "%s manually.</b>"%(document, document, document)
        model = self.env['ir.model'].sudo().search([('model', '=', 'stock.warehouse.orderpoint')], limit=1)
        domain = [('automated', '=', True), ('date_deadline', '=', datetime.today().strftime('%Y-%m-%d')),
                  ('note', '=', message), ('res_model_id', '=', model.id), ('res_id', '=', self.id)]
        activity = activity_obj.sudo().search(domain)
        if activity:
            return activity
        orderpoint_activity_vals = self.prepare_orderpoint_activity_vals()
        orderpoint_activity_vals.update(values)
        activity = activity_obj.create(orderpoint_activity_vals)
        return activity

    def prepare_orderpoint_activity_vals(self):
        """
        This method will prepare activity vals for order point.
        :return:
        """
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        model = self.env['ir.model'].sudo().search([('model', '=', 'stock.warehouse.orderpoint')], limit=1)
        return {
            'activity_type_id': activity_type and activity_type.id,
            'summary': activity_type.summary,
            'automated': True,
            'note': activity_type.default_description,
            'date_deadline': datetime.today().strftime('%Y-%m-%d'),
            'res_model_id': model.id,
            'res_id': self.id,
            'user_id': self.env.user.id
        }
