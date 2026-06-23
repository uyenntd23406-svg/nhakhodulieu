{{ config(materialized='table', schema='gold') }}

with base as (
    select *
    from {{ ref('int_delivery_metrics') }}
),

location_dim as (
    select *
    from {{ ref('dim_location') }}
),

shipping_dim as (
    select *
    from {{ ref('dim_shipping') }}
),

date_dim as (
    select *
    from {{ ref('dim_date') }}
)

select
    b.order_item_id,
    b.order_id,

    od.date_key as order_date_key,
    sd.date_key as shipping_date_key,

    b.customer_id as customer_key,
    b.product_card_id as product_key,
    l.location_key,
    s.shipping_key,

    b.transaction_type,
    b.order_year_month,

    b.sales_per_customer as sales_amount,
    b.sales,
    b.order_item_total,
    b.order_profit_per_order as profit_amount,
    b.benefit_per_order,
    b.total_cost,

    b.order_item_discount as discount_amount,
    b.order_item_discount_rate as discount_rate,
    b.order_item_product_price as product_unit_price,
    b.order_item_profit_ratio as profit_ratio,
    b.order_item_quantity as quantity,

    b.days_for_shipping_real,
    b.days_for_shipment_scheduled,
    b.delivery_delay_days,
    b.shipping_variance,

    b.late_delivery_risk,
    b.is_late_delivery,
    b.is_on_time_delivery,
    b.is_advance_shipping,
    b.is_shipping_canceled,
    b.gross_profit_margin,

    b.order_year,
    b.order_month,
    b.order_day,
    b.order_day_of_week,
    b.order_month_date

from base b

left join date_dim od
    on cast(b.order_date as date) = od.date_day

left join date_dim sd
    on cast(b.shipping_date as date) = sd.date_day

left join location_dim l
    on coalesce(b.market, '') = coalesce(l.market, '')
   and coalesce(b.order_region, '') = coalesce(l.order_region, '')
   and coalesce(b.order_country, '') = coalesce(l.order_country, '')
   and coalesce(b.order_city, '') = coalesce(l.order_city, '')
   and coalesce(b.order_state, '') = coalesce(l.order_state, '')
   and coalesce(cast(b.order_zipcode as varchar), '') = coalesce(cast(l.order_zipcode as varchar), '')

left join shipping_dim s
    on coalesce(b.shipping_mode, '') = coalesce(s.shipping_mode, '')
   and coalesce(b.delivery_status, '') = coalesce(s.delivery_status, '')
   and coalesce(b.order_status, '') = coalesce(s.order_status, '')