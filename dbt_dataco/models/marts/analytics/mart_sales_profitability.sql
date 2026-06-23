{{ config(materialized='table', schema='gold') }}

select
    f.order_year_month,
    l.market,
    c.customer_segment,
    p.department_name,
    p.category_name,
    p.product_name,

    count(distinct f.order_id) as order_count,
    count(*) as order_item_count,
    sum(f.quantity) as total_quantity,

    sum(f.sales_amount) as total_sales,
    sum(f.profit_amount) as total_profit,
    sum(f.total_cost) as total_cost,

    case
        when sum(f.sales_amount) <> 0
        then sum(f.profit_amount) / sum(f.sales_amount)
        else null
    end as profit_margin,

    avg(f.sales_amount) as avg_sales_per_item,
    avg(f.discount_rate) as avg_discount_rate,
    avg(f.profit_ratio) as avg_profit_ratio

from {{ ref('fct_order_items') }} f
left join {{ ref('dim_location') }} l
    on f.location_key = l.location_key
left join {{ ref('dim_customer') }} c
    on f.customer_key = c.customer_key
left join {{ ref('dim_product') }} p
    on f.product_key = p.product_key

group by
    f.order_year_month,
    l.market,
    c.customer_segment,
    p.department_name,
    p.category_name,
    p.product_name
