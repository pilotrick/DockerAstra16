DROP FUNCTION IF EXISTS public.update_product_sales_history(integer[], integer[], integer[], integer[], date, date, integer);
CREATE OR REPLACE FUNCTION public.update_product_sales_history(
    company_ids integer[],
    product_ids integer[],
    category_ids integer[],
    warehouse_ids integer[],
    date_start date,
    date_end date,
    uid integer)
  RETURNS void AS
$BODY$
    DECLARE
        temprow RECORD;
    BEGIN
        FOR temprow IN Select * from get_product_sales_history_data(company_ids,product_ids,category_ids,warehouse_ids,date_start,date_end)
            LOOP
                IF EXISTS (select * from product_sales_history psh where psh.product_id = temprow.product_id and psh.warehouse_id = temprow.warehouse_id and psh.start_date = date_start and psh.end_date = date_end) THEN
                    UPDATE product_sales_history as psh SET sales_qty = temprow.sales_qty, average_daily_sale = temprow.ads, max_daily_sale_qty = temprow.max_daily_sale,
                    min_daily_sale_qty = temprow.min_daily_sale, total_orders = temprow.total_orders, write_date = now()::date, write_uid = uid --, orderpoint_id = swo.id
                    from stock_warehouse_orderpoint as swo
                    WHERE swo.id = psh.orderpoint_id and swo.product_id = temprow.product_id and swo.warehouse_id = temprow.warehouse_id --and psh.orderpoint_id = temprow.orderpoint_id
                    and  psh.start_date = date_start and psh.end_date = date_end;
                Else
                    Insert into product_sales_history
                    (product_id, warehouse_id, orderpoint_id, sales_qty, average_daily_sale, max_daily_sale_qty,
                    min_daily_sale_qty, start_date, end_date, duration, total_orders, create_date, write_date, create_uid, write_uid)
                    Select sd.product_id, sd.warehouse_id, op.id, sd.sales_qty, sd.ads, sd.max_daily_sale,
                    sd.min_daily_sale, date_start, date_end, (date_end-date_start)+1 ,sd.total_orders, now()::date, now()::date, uid, uid
                    From
                    (
                        select temprow.product_id,temprow.warehouse_id, temprow.sales_qty, temprow.ads, temprow.max_daily_sale, temprow.min_daily_sale, temprow.total_orders
                    )sd
                        Inner Join stock_warehouse_orderpoint op on op.product_id = sd.product_id and op.warehouse_id = sd.warehouse_id;
                END IF;
            END LOOP;
    END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;