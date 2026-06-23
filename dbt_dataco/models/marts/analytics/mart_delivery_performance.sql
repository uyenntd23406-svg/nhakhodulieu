{{ config(materialized='table', schema='gold') }}

select
    f.order_year_month,
    l.market,
    l.order_region,
    l.order_country,
    s.shipping_mode,
    s.delivery_status,

    count(distinct f.order_id) as order_count,
    count(*) as order_item_count,

    sum(f.is_late_delivery) as late_item_count,
    sum(f.is_on_time_delivery) as on_time_item_count,
    sum(f.is_advance_shipping) as advance_shipping_item_count,
    sum(f.is_shipping_canceled) as canceled_item_count,

    avg(cast(f.is_late_delivery as double)) as late_delivery_rate,
    avg(f.days_for_shipping_real) as avg_real_shipping_days,
    avg(f.days_for_shipment_scheduled) as avg_scheduled_shipping_days,
    avg(f.shipping_variance) as avg_shipping_variance,

    sum(f.sales_amount) as total_sales,
    sum(f.profit_amount) as total_profit

from {{ ref('fct_order_items') }} f
left join {{ ref('dim_location') }} l
    on f.location_key = l.location_key
left join {{ ref('dim_shipping') }} s
    on f.shipping_key = s.shipping_key

group by
    f.order_year_month,
    l.market,
    l.order_region,
    l.order_country,
    s.shipping_mode,
    s.delivery_status
