DROP FUNCTION IF EXISTS public.update_product_purchase_history(integer[], integer[], date, date, integer);
CREATE OR REPLACE FUNCTION public.update_product_purchase_history(
    product_ids integer[],
    warehouse_ids integer[],
    date_start date,
    date_end date,
    uid integer)
  RETURNS void AS
$BODY$
    DECLARE
--        purchase_data record := ();
        temprow record;
        tr_date_start timestamp without time zone := (date_start || ' 00:00:00')::timestamp without time zone;
        tr_date_end timestamp without time zone:= (date_end || ' 23:59:59')::timestamp without time zone;
    BEGIN
        for temprow in SELECT
                            l.product_id as product_id,
                            spt.warehouse_id as warehouse_id,
                            po.partner_id as partner_id,
                            op.id as orderpoint_id,
                            po.id AS order_id,
                            sum(l.product_qty) as qty_ordered,
                    --                     round(sum(l.product_qty / line_uom.factor * product_uom.factor),2) AS qty_ordered,
                            po.currency_id as currency_id,
                            l.price_unit as price_unit,
                            po.date_order as date_order,
                            round((date_part('epoch'::text, age(l.date_planned, po.date_order)) / (24 * 60 * 60))::numeric,2)+1::double precision AS lead_time,
                            uid as create_uid,
                            now()::date as create_date,
                            uid as write_uid,
                            now()::date as write_date
                        FROM purchase_order_line l
                            Inner JOIN purchase_order po ON l.order_id = po.id
                            Inner JOIN product_product p ON l.product_id = p.id
                    --                     LEFT JOIN product_template t ON p.product_tmpl_id = t.id
                    --                     LEFT JOIN uom_uom line_uom ON line_uom.id = l.product_uom
                    --                     LEFT JOIN uom_uom product_uom ON product_uom.id = t.uom_id
                            Inner JOIN stock_picking_type spt ON spt.id = po.picking_type_id
                            Inner JOIN stock_warehouse_orderpoint op on op.product_id = l.product_id and op.warehouse_id = spt.warehouse_id
                        where
                        --product dynamic condition
                        1 = case when array_length(product_ids,1) >= 1 then
                            case when l.product_id = ANY(product_ids) then 1 else 0 end
                            else 1 end
                        --warehouse dynamic condition
                        and 1 = case when array_length(warehouse_ids,1) >= 1 then
                            case when spt.warehouse_id = ANY(warehouse_ids) then 1 else 0 end
                            else 1 end
                        and po.date_order >= tr_date_start and po.date_order <= tr_date_end and
                        po.state::text = ANY (ARRAY['purchase'::character varying::text, 'done'::character varying::text])
                        GROUP BY
                            po.partner_id, l.product_id, l.price_unit, l.date_planned,
                            po.date_order, po.id, spt.warehouse_id, op.id
            LOOP
                IF EXISTS (select * from product_purchase_history pph where pph.product_id = temprow.product_id and pph.warehouse_id = temprow.warehouse_id and pph.partner_id = temprow.partner_id
                    and pph.purchase_id = temprow.order_id) THEN
                    UPDATE product_purchase_history as pph SET po_qty = temprow.qty_ordered, currency_id = temprow.currency_id, purchase_price = temprow.price_unit,
                    po_date = temprow.date_order, lead_time = temprow.lead_time, write_date = temprow.write_date, write_uid = temprow.write_uid --, orderpoint_id = swo.id
                    from stock_warehouse_orderpoint as swo
                    WHERE swo.id = pph.orderpoint_id and swo.product_id = temprow.product_id and swo.warehouse_id = temprow.warehouse_id --and psh.orderpoint_id = temprow.orderpoint_id
                    and pph.partner_id = temprow.partner_id
                    and pph.purchase_id = temprow.order_id;
                    --and  psh.start_date = date_start and psh.end_date = date_end;
                ELSE
                    Insert into product_purchase_history
                    (
                        product_id, warehouse_id, partner_id, orderpoint_id, purchase_id, po_qty, currency_id, purchase_price, po_date, lead_time,
                        create_uid, create_date, write_uid, write_date
                    )
                    select temprow.product_id, temprow.warehouse_id, temprow.partner_id, temprow.orderpoint_id, temprow.order_id, temprow.qty_ordered, temprow.currency_id, temprow.price_unit, temprow.date_order, temprow.lead_time,
                        temprow.create_uid, temprow.create_date, temprow.write_uid, temprow.write_date;
                END IF;
            END LOOP;
    END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
