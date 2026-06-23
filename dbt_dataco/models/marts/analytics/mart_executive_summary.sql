{{ config(materialized='table', schema='gold') }}

with base as (
    select
        f.order_year_month,
        l.market,

        count(distinct f.order_id) as total_orders,
        count(*) as total_order_items,
        count(distinct f.customer_key) as total_customers,

        sum(f.sales_amount) as total_sales,
        sum(f.profit_amount) as total_profit,
        sum(f.total_cost) as total_cost,

        avg(cast(f.is_late_delivery as double)) as late_delivery_rate,
        avg(f.days_for_shipping_real) as avg_shipping_days,
        avg(f.shipping_variance) as avg_shipping_variance

    from {{ ref('fct_order_items') }} f
    left join {{ ref('dim_location') }} l
        on f.location_key = l.location_key

    group by
        f.order_year_month,
        l.market
)

select
    *,
    case
        when late_delivery_rate >= 0.60 then 'High delivery risk'
        when late_delivery_rate >= 0.45 then 'Medium delivery risk'
        else 'Low delivery risk'
    end as delivery_risk_level,

    case
        when total_profit < 0 then 'Negative profit'
        when total_sales is null or total_sales = 0 then 'No sales'
        else 'Normal'
    end as business_health_flag

from base
