# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from .forcasting import forcasting_details


class ForcastingReport(models.Model):
    _name = "forcasting.report"


class SaleForcastingReport(models.Model):
    _name = "sale.forcasting.report"

    forcasting_price = fields.Float("Total")
    forcasting_date = fields.Date("Order Date")
    name = fields.Char("Name")
    qty_ordered = fields.Float("Qty Ordered")
    qty_received = fields.Float("Qty Delivered")
    qty_billed = fields.Float('Qty Billed', readonly=True)

    def sale_forcasting_data(self):
        cr = self.env.cr
        # Delete Data
        cr.execute("""delete from sale_forcasting_report""")

        cr.execute("""
        SELECT date_trunc('month', generate_series(dt_order, dt_order + INTERVAL '11 months', '1 month')) AS predictions_dates
        
        from (select date_trunc('month', max(date_order::TIMESTAMP::DATE)  + interval '1 month')::date as dt_order from sale_order) as sale_order_info
        """)

        predicts_dates = list(map(lambda data: data[0], cr.fetchall()))

        query_total = """
            select month_sale_dates,sum(sum_total) from (select month_sale_dates,CASE 
            WHEN EXTRACT(year FROM date_trunc('month',date_order)::TIMESTAMP::DATE) = EXTRACT(year FROM date_trunc('month',month_sale_dates)) 
            and EXTRACT(month FROM date_trunc('month',date_order)::TIMESTAMP::DATE)=EXTRACT(month FROM date_trunc('month',month_sale_dates)) 
            THEN sum(amount_total) 
            ELSE sum(0.0)
            END AS sum_total
            from(select generate_series(min_dateorder::date, max_dateorder::date, '1 month')::date as month_sale_dates       
            from (select min(date_order ::TIMESTAMP::DATE ) as min_dateorder,
            max(date_order ::TIMESTAMP::DATE) as max_dateorder 
            from sale_order) as sale_info) as sale_dates , sale_order
            group by month_sale_dates,date_trunc('month',date_order)::TIMESTAMP::DATE) as sale_info
            group by month_sale_dates order by month_sale_dates
        """
        cr.execute(query_total)
        get_res = forcasting_details(cr.fetchall(), predicts_dates)

        # Order QTY Prediction
        res_qty_ordered = """
            select month_sale_dates,sum(sum_total) from (select month_sale_dates,CASE 
            WHEN EXTRACT(year FROM date_trunc('month',date_order)::TIMESTAMP::DATE) = EXTRACT(year FROM date_trunc('month',month_sale_dates)) 
            and EXTRACT(month FROM date_trunc('month',date_order)::TIMESTAMP::DATE)=EXTRACT(month FROM date_trunc('month',month_sale_dates)) 
            THEN sum(product_uom_qty) 
            ELSE sum(0.0)
            END AS sum_total
            from(select generate_series(min_dateorder::date, max_dateorder::date, '1 month')::date as month_sale_dates       
            from (select min(date_order ::TIMESTAMP::DATE ) as min_dateorder,
            max(date_order ::TIMESTAMP::DATE) as max_dateorder 
            from sale_order) as sale_info) as sale_dates , 
            (SELECT date_trunc('month', date_order) AS date_order,sum(product_uom_qty) as product_uom_qty 
            FROM sale_order as po full join sale_order_line as pol On pol.order_id = po.id 
            WHERE date_order is not null
            GROUP BY date_trunc('month', date_order)
            ORDER BY date_trunc('month', date_order)) as sale_info
            group by month_sale_dates,date_trunc('month',date_order)::TIMESTAMP::DATE) as sale_info
            group by month_sale_dates order by month_sale_dates
        """
        cr.execute(res_qty_ordered)
        get_res_qty = forcasting_details(cr.fetchall(), predicts_dates)

        # Received QTY Prediction
        res_qty_delivered = """
            select month_sale_dates,sum(sum_total) from (select month_sale_dates,CASE 
            WHEN EXTRACT(year FROM date_trunc('month',date_order)::TIMESTAMP::DATE) = EXTRACT(year FROM date_trunc('month',month_sale_dates)) 
            and EXTRACT(month FROM date_trunc('month',date_order)::TIMESTAMP::DATE)=EXTRACT(month FROM date_trunc('month',month_sale_dates)) 
            THEN sum(qty_delivered) 
            ELSE sum(0.0)
            END AS sum_total
            from(select generate_series(min_dateorder::date, max_dateorder::date, '1 month')::date as month_sale_dates       
            from (select min(date_order ::TIMESTAMP::DATE ) as min_dateorder,
            max(date_order ::TIMESTAMP::DATE) as max_dateorder 
            from sale_order) as sale_info) as sale_dates , 
            (SELECT date_trunc('month', date_order) AS date_order,sum(qty_delivered) as qty_delivered 
            FROM sale_order as po full join sale_order_line as pol On pol.order_id = po.id 
            WHERE date_order is not null
            GROUP BY date_trunc('month', date_order)
            ORDER BY date_trunc('month', date_order)) as sale_info
            group by month_sale_dates,date_trunc('month',date_order)::TIMESTAMP::DATE) as sale_info
            group by month_sale_dates order by month_sale_dates
        """
        cr.execute(res_qty_delivered)
        get_res_delivered = forcasting_details(
            cr.fetchall(), predicts_dates)

        # Invoiced QTY Prediction
        res_qty_invoiced = """
            select month_sale_dates,sum(sum_total) from (select month_sale_dates,CASE 
            WHEN EXTRACT(year FROM date_trunc('month',date_order)::TIMESTAMP::DATE) = EXTRACT(year FROM date_trunc('month',month_sale_dates)) 
            and EXTRACT(month FROM date_trunc('month',date_order)::TIMESTAMP::DATE)=EXTRACT(month FROM date_trunc('month',month_sale_dates)) 
            THEN sum(qty_invoiced) 
            ELSE sum(0.0)
            END AS sum_total
            from(select generate_series(min_dateorder::date, max_dateorder::date, '1 month')::date as month_sale_dates       
            from (select min(date_order ::TIMESTAMP::DATE ) as min_dateorder,
            max(date_order ::TIMESTAMP::DATE) as max_dateorder 
            from sale_order) as sale_info) as sale_dates , 
            (SELECT date_trunc('month', date_order) AS date_order,sum(qty_invoiced) as qty_invoiced 
            FROM sale_order as po full join sale_order_line as pol On pol.order_id = po.id 
            WHERE date_order is not null
            GROUP BY date_trunc('month', date_order)
            ORDER BY date_trunc('month', date_order)) as sale_info
            group by month_sale_dates,date_trunc('month',date_order)::TIMESTAMP::DATE) as sale_info
            group by month_sale_dates order by month_sale_dates
        """
        cr.execute(res_qty_invoiced)
        get_res_invoiced = forcasting_details(
            cr.fetchall(), predicts_dates)

        # # get_res = forcasting_details(res)
        Obj = self.env['sale.forcasting.report']
        for x, y in get_res.items():
            info = dict()
            info['name'] = x
            info['forcasting_date'] = x
            if y < 0.0:
                info['forcasting_price'] = 0.0
            else:
                info['forcasting_price'] = y
            qty_ordered = get_res_qty[x]
            info['qty_ordered'] = 0.0 if qty_ordered < 0.0 else qty_ordered
            qty_received = get_res_delivered[x]
            info['qty_received'] = 0.0 if qty_received < 0.0 else qty_received
            qty_billed = get_res_invoiced[x]
            info['qty_billed'] = 0.0 if qty_billed < 0.0 else qty_billed
            Obj.create(info)
