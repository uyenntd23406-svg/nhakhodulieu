{{ config(materialized='table', schema='gold') }}

select
    f.order_item_id,
    f.order_id,

    l.market,
    l.order_region,
    l.order_country,
    c.customer_segment,
    p.department_name,
    p.category_name,
    p.product_name,
    s.shipping_mode,
    s.order_status,

    f.quantity,
    f.sales_amount,
    f.discount_amount,
    f.discount_rate,
    f.product_unit_price,
    f.profit_ratio,
    f.days_for_shipment_scheduled,

    f.order_month,
    f.order_day,
    f.order_day_of_week,

    f.late_delivery_risk as target_late_delivery_risk

from {{ ref('fct_order_items') }} f
left join {{ ref('dim_location') }} l
    on f.location_key = l.location_key
left join {{ ref('dim_customer') }} c
    on f.customer_key = c.customer_key
left join {{ ref('dim_product') }} p
    on f.product_key = p.product_key
left join {{ ref('dim_shipping') }} s
    on f.shipping_key = s.shipping_key
where f.late_delivery_risk is not null
