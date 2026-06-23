{{ config(materialized='table', schema='gold') }}

select
    count(distinct order_id) as total_orders,
    count(*) as total_order_items,
    count(distinct customer_key) as total_customers,
    count(distinct product_key) as total_products,

    sum(sales_amount) as total_sales,
    sum(profit_amount) as total_profit,
    sum(total_cost) as total_cost,

    case
        when sum(sales_amount) <> 0
        then sum(profit_amount) / sum(sales_amount)
        else null
    end as profit_margin,

    sum(is_late_delivery) as late_order_items,
    avg(cast(is_late_delivery as double)) as late_delivery_rate,

    avg(days_for_shipping_real) as avg_shipping_days_real,
    avg(days_for_shipment_scheduled) as avg_shipping_days_scheduled,
    avg(shipping_variance) as avg_shipping_variance

from {{ ref('fct_order_items') }}
