from odoo import api, fields, models, _
from .forcasting import forcasting_details


class ForcastingReportPurchase(models.Model):
    _name = "purchase.forcasting.report"

    forcasting_price = fields.Float("Total")
    forcasting_date = fields.Date("Order Date")
    name = fields.Char("Name")
    qty_ordered = fields.Float("Qty Ordered")
    qty_received = fields.Float("Qty Received")
    qty_billed = fields.Float('Qty Billed', readonly=True)

    def purchase_forcasting_data(self):
        cr = self.env.cr

        cr.execute("""delete from purchase_forcasting_report""")

        cr.execute("""
        SELECT date_trunc('month', generate_series(dt_order, dt_order + INTERVAL '12 months', '1 month')) AS predicits_dates
        from (select max(date_order::TIMESTAMP::DATE) + INTERVAL '1 month' as dt_order from purchase_order) as purchase_order_info
        """)

        predicts_dates = list(map(lambda data: data[0], cr.fetchall()))

        qry_price = """
            select month_pur_dates,sum(sum_total) from (select month_pur_dates,CASE 
            WHEN EXTRACT(year FROM date_trunc('month',date_order)::TIMESTAMP::DATE) = EXTRACT(year FROM date_trunc('month',month_pur_dates)) 
            and EXTRACT(month FROM date_trunc('month',date_order)::TIMESTAMP::DATE)=EXTRACT(month FROM date_trunc('month',month_pur_dates)) 
            THEN sum(amount_total) 
            ELSE sum(0.0)
            END AS sum_total
            from(select generate_series(min_dateorder::date, max_dateorder::date, '1 month')::date as month_pur_dates       
            from (select min(date_order ::TIMESTAMP::DATE ) as min_dateorder,
            max(date_order ::TIMESTAMP::DATE) as max_dateorder 
            from purchase_order) as pur_info) as pur_dates , purchase_order
            group by month_pur_dates,date_trunc('month',date_order)::TIMESTAMP::DATE) as pur_info
            group by month_pur_dates
            order by month_pur_dates
        """
        cr.execute(qry_price)
        res = cr.fetchall()
        get_res_price = forcasting_details(res, predicts_dates)

        qry_ordered = """
            select month_pur_dates,sum(sum_total) from (select month_pur_dates,CASE 
            WHEN EXTRACT(year FROM date_trunc('month',date_order)::TIMESTAMP::DATE) = EXTRACT(year FROM date_trunc('month',month_pur_dates)) 
            and EXTRACT(month FROM date_trunc('month',date_order)::TIMESTAMP::DATE)=EXTRACT(month FROM date_trunc('month',month_pur_dates)) 
            THEN sum(product_qty) 
            ELSE sum(0.0)
            END AS sum_total
            from(select generate_series(min_dateorder::date, max_dateorder::date, '1 month')::date as month_pur_dates       
            from (select min(date_order ::TIMESTAMP::DATE ) as min_dateorder,
            max(date_order ::TIMESTAMP::DATE) as max_dateorder 
            from purchase_order) as pur_info) as pur_dates , 
            (SELECT date_trunc('month', date_order) AS date_order,sum(product_qty) as product_qty 
            FROM purchase_order as po full join purchase_order_line as pol On pol.order_id = po.id 
            WHERE date_order is not null
            GROUP BY date_trunc('month', date_order)
            ORDER BY date_trunc('month', date_order)) as pur_info
            group by month_pur_dates,date_trunc('month',date_order)::TIMESTAMP::DATE) as pur_info
            group by month_pur_dates
            order by month_pur_dates
        """
        cr.execute(qry_ordered)
        res = cr.fetchall()
        get_res_qty = forcasting_details(res, predicts_dates)

        qry_received = """
            select month_pur_dates,sum(sum_total) from (select month_pur_dates,CASE 
            WHEN EXTRACT(year FROM date_trunc('month',date_order)::TIMESTAMP::DATE) = EXTRACT(year FROM date_trunc('month',month_pur_dates)) 
            and EXTRACT(month FROM date_trunc('month',date_order)::TIMESTAMP::DATE)=EXTRACT(month FROM date_trunc('month',month_pur_dates)) 
            THEN sum(qty_received) 
            ELSE sum(0.0)
            END AS sum_total
            from(select generate_series(min_dateorder::date, max_dateorder::date, '1 month')::date as month_pur_dates       
            from (select min(date_order ::TIMESTAMP::DATE ) as min_dateorder,
            max(date_order ::TIMESTAMP::DATE) as max_dateorder 
            from purchase_order) as pur_info) as pur_dates , 
            (SELECT date_trunc('month', date_order) AS date_order,sum(qty_received) as qty_received 
            FROM purchase_order as po full join purchase_order_line as pol On pol.order_id = po.id 
            WHERE date_order is not null
            GROUP BY date_trunc('month', date_order)
            ORDER BY date_trunc('month', date_order)) as pur_info
            group by month_pur_dates,date_trunc('month',date_order)::TIMESTAMP::DATE) as pur_info
            group by month_pur_dates
            order by month_pur_dates
        """
        cr.execute(qry_received)
        res = cr.fetchall()
        get_res_received = forcasting_details(res, predicts_dates)

        qry_invoiced = """
            select month_pur_dates,sum(sum_total) from (select month_pur_dates,CASE 
            WHEN EXTRACT(year FROM date_trunc('month',date_order)::TIMESTAMP::DATE) = EXTRACT(year FROM date_trunc('month',month_pur_dates)) 
            and EXTRACT(month FROM date_trunc('month',date_order)::TIMESTAMP::DATE)=EXTRACT(month FROM date_trunc('month',month_pur_dates)) 
            THEN sum(qty_invoiced) 
            ELSE sum(0.0)
            END AS sum_total
            from(select generate_series(min_dateorder::date, max_dateorder::date, '1 month')::date as month_pur_dates       
            from (select min(date_order ::TIMESTAMP::DATE ) as min_dateorder,
            max(date_order ::TIMESTAMP::DATE) as max_dateorder 
            from purchase_order) as pur_info) as pur_dates , 
            (SELECT date_trunc('month', date_order) AS date_order,sum(qty_invoiced) as qty_invoiced 
            FROM purchase_order as po full join purchase_order_line as pol On pol.order_id = po.id 
            WHERE date_order is not null
            GROUP BY date_trunc('month', date_order)
            ORDER BY date_trunc('month', date_order)) as pur_info
            group by month_pur_dates,date_trunc('month',date_order)::TIMESTAMP::DATE) as pur_info
            group by month_pur_dates
            order by month_pur_dates
        """
        cr.execute(qry_invoiced)
        res = cr.fetchall()
        get_res_invoiced = forcasting_details(res, predicts_dates)

        Obj = self.env['purchase.forcasting.report']
        for x, y in get_res_price.items():
            info = dict()
            info['name'] = x
            info['forcasting_date'] = x
            if y < 0.0:
                info['forcasting_price'] = 0.0
            else:
                info['forcasting_price'] = y
            qty_ordered = get_res_qty[x]
            info['qty_ordered'] = 0.0 if qty_ordered < 0.0 else qty_ordered
            qty_received = get_res_received[x]
            info['qty_received'] = 0.0 if qty_received < 0.0 else qty_received
            qty_billed = get_res_invoiced[x]
            info['qty_billed'] = 0.0 if qty_billed < 0.0 else qty_billed
            Obj.create(info)
