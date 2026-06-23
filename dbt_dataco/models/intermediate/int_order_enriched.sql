{{ config(materialized='view', schema='silver') }}

select
    o.order_id,
    o.order_item_id,
    o.order_customer_id,
    o.product_card_id,
    o.order_item_cardprod_id,

    o.order_date,
    o.shipping_date,
    o.order_year_month,

    o.transaction_type,
    o.market,
    o.order_region,
    o.order_country,
    o.order_city,
    o.order_state,
    o.order_zipcode,

    o.shipping_mode,
    o.delivery_status,
    o.order_status,
    o.late_delivery_risk,

    o.days_for_shipping_real,
    o.days_for_shipment_scheduled,
    o.delivery_delay_days,

    o.sales_per_customer,
    o.sales,
    o.order_item_total,
    o.benefit_per_order,
    o.order_profit_per_order,
    o.order_item_discount,
    o.order_item_discount_rate,
    o.order_item_product_price,
    o.order_item_profit_ratio,
    o.order_item_quantity,

    c.customer_id,
    c.customer_segment,
    c.customer_city,
    c.customer_country,
    c.customer_state,
    c.customer_zipcode,
    c.customer_latitude,
    c.customer_longitude,

    p.product_category_id,
    p.product_name,
    p.product_price,
    p.product_status,
    p.category_id,
    p.category_name,
    p.department_id,
    p.department_name,
    p.product_description,
    p.product_image

from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c
    on o.order_customer_id = c.customer_id
left join {{ ref('stg_products') }} p
    on o.product_card_id = p.product_card_id
