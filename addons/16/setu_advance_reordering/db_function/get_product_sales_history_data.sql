DROP FUNCTION IF EXISTS public.get_product_sales_history_data(integer[], integer[], integer[], integer[], date, date);
CREATE OR REPLACE FUNCTION public.get_product_sales_history_data(
    IN company_ids integer[],
    IN product_ids integer[],
    IN category_ids integer[],
    IN warehouse_ids integer[],
    IN start_date date,
    IN end_date date)
  RETURNS TABLE(company_id integer, product_id integer, product_category_id integer, warehouse_id integer, sales_qty numeric, total_orders numeric, ads numeric, max_daily_sale numeric, min_daily_sale numeric) AS
$BODY$
    DECLARE
        day_difference integer := ((end_date::Date-start_date::Date)+1);
        tr_start_date timestamp without time zone := (start_date || ' 00:00:00')::timestamp without time zone;
        tr_end_date timestamp without time zone:= (end_date || ' 23:59:59')::timestamp without time zone;
    BEGIN
        Return Query
        Select
-- 			sd.cmp_id, sd.cmp_name, sd.p_id, sd.prod_name, sd.categ_id, sd.cat_name, sd.wh_id, sd.ware_name,
            sd.cmp_id, sd.p_id, sd.categ_id, sd.wh_id,
            sum(sd.total_sales) as total_sales, sum(sd.total_orders) as total_orders, round(sum(sd.total_sales)/day_difference,2) as ads, max(sd.total_sales) max_daily_sale,
                        min(sd.total_sales) min_daily_sale
                    From (
                Select
-- 				cmp_id, cmp_name, p_id, prod_name, categ_id, cat_name, wh_id, ware_name, T.order_date,
                cmp_id, p_id, categ_id, wh_id, T.order_date,
                sum(T.sales_qty) as total_sales, count(T.order_id) as total_orders
                --,sum(T.sales_qty) as ads, sum(T.sales_qty) max_daily_sale,
                --min(T.sales_qty) min_daily_sale
                From
                (

            SELECT
                foo.cmp_id,
-- 			    foo.cmp_name,
                foo.p_id,
-- 			    foo.prod_name,
                foo.categ_id,
-- 			    foo.cat_name,
                foo.wh_id,
-- 			    foo.ware_name,
                foo.sales_qty,
                foo.order_id,
                foo.order_date
            FROM
            (
                SELECT
                so.company_id as cmp_id,
-- 				cmp.name as cmp_name,
                sol.product_id as p_id,
-- 				pro.default_code as prod_name,
                pt.categ_id,
-- 				cat.complete_name as cat_name,
                so.warehouse_id as wh_id,
-- 				ware.name as ware_name,
                sol.order_id,
                so.date_order as order_date,
                sum(Round(sol.product_uom_qty ,2)) AS sales_qty
-- 				sum(Round(sol.product_uom_qty / u.factor * u2.factor,2)) AS sales_qty
                FROM sale_order_line sol
                JOIN sale_order so ON sol.order_id = so.id
                Inner Join product_product pro ON sol.product_id = pro.id
                Inner Join product_template pt ON pro.product_tmpl_id = pt.id
-- 				Inner Join uom_uom u ON u.id = sol.product_uom
-- 				Inner Join uom_uom u2 ON u2.id = pt.uom_id
-- 				Inner Join res_company cmp on cmp.id = so.company_id
-- 				Inner Join stock_warehouse ware on ware.id = so.warehouse_id
-- 				Inner Join product_category cat on cat.id = pt.categ_id
                WHERE so.state::text = ANY (ARRAY['sale'::character varying::text, 'done'::character varying::text])
                and (coalesce(pro.capping_qty,0) = 0.0 or sol.product_uom_qty <= coalesce(pro.capping_qty,0))
                and so.date_order >= tr_start_date and so.date_order <= tr_end_date
                --company dynamic condition
                and 1 = case when array_length(company_ids,1) >= 1 then
                case when so.company_id = ANY(company_ids) then 1 else 0 end
                else 1 end
                --product dynamic condition
                and 1 = case when array_length(product_ids,1) >= 1 then
                case when sol.product_id = ANY(product_ids) then 1 else 0 end
                else 1 end
                --category dynamic condition
                and 1 = case when array_length(category_ids,1) >= 1 then
                case when pt.categ_id = ANY(category_ids) then 1 else 0 end
                else 1 end
                --warehouse dynamic condition
                and 1 = case when array_length(warehouse_ids,1) >= 1 then
                case when so.warehouse_id = ANY(warehouse_ids) then 1 else 0 end
                else 1 end
-- 			    group by so.company_id, cmp.name, sol.product_id, pro.default_code, pt.categ_id, cat.complete_name, so.warehouse_id, ware.name,
-- 					sol.order_id, so.date_order
            group by so.company_id, sol.product_id, sol.order_id, so.date_order, pt.categ_id, so.warehouse_id

            Union All

            SELECT
                wh.company_id as cmp_id,
                pro.id as p_id,
                pt.categ_id,
                wh.id as wh_id,
                null as order_id,
                start_date as order_date,
                0 AS sales_qty
            FROM product_product pro, product_template pt, stock_warehouse wh
            Where pro.product_tmpl_id = pt.id

                --company dynamic condition
                and 1 = case when array_length(company_ids,1) >= 1 then
                case when wh.company_id = ANY(company_ids) then 1 else 0 end
                else 1 end
                --product dynamic condition
                and 1 = case when array_length(product_ids,1) >= 1 then
                case when pro.id = ANY(product_ids) then 1 else 0 end
                else 1 end
                --category dynamic condition
                and 1 = case when array_length(category_ids,1) >= 1 then
                case when pt.categ_id = ANY(category_ids) then 1 else 0 end
                else 1 end
                --warehouse dynamic condition
                and 1 = case when array_length(warehouse_ids,1) >= 1 then
                case when wh.id = ANY(warehouse_ids) then 1 else 0 end
                else 1 end

            ) foo
                )T
-- 			    group by cmp_id, cmp_name, p_id, prod_name, categ_id, cat_name, wh_id, ware_name,  T.order_date
                group by cmp_id, p_id, categ_id, wh_id,  T.order_date
            )sd
-- 			group by cmp_id, cmp_name, p_id, prod_name, categ_id, cat_name, wh_id, ware_name;
            group by cmp_id, p_id, categ_id, wh_id;
        END;

$BODY$
LANGUAGE plpgsql VOLATILE
COST 100
ROWS 1000;
