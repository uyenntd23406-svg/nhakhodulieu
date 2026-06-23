{{ config(materialized='view', schema='silver') }}

select
    *,

    cast(days_for_shipping_real - days_for_shipment_scheduled as integer) as shipping_variance,

    case when late_delivery_risk = 1 then 1 else 0 end as is_late_delivery,
    case when delivery_status = 'Shipping on time' then 1 else 0 end as is_on_time_delivery,
    case when delivery_status = 'Advance shipping' then 1 else 0 end as is_advance_shipping,
    case when delivery_status = 'Shipping canceled' then 1 else 0 end as is_shipping_canceled,

    case
        when sales_per_customer is not null and sales_per_customer <> 0
        then order_profit_per_order / sales_per_customer
        else null
    end as gross_profit_margin,

    case
        when sales_per_customer is not null and order_profit_per_order is not null
        then sales_per_customer - order_profit_per_order
        else null
    end as total_cost,

    extract(year from order_date) as order_year,
    extract(month from order_date) as order_month,
    extract(day from order_date) as order_day,
    extract(dow from order_date) as order_day_of_week,

    date_trunc('month', order_date) as order_month_date

from {{ ref('int_order_enriched') }}
