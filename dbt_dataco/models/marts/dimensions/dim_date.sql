{{ config(materialized='table', schema='gold') }}

with dates as (
    select distinct
        cast(order_date as date) as date_day
    from {{ ref('int_delivery_metrics') }}
    where order_date is not null

    union

    select distinct
        cast(shipping_date as date) as date_day
    from {{ ref('int_delivery_metrics') }}
    where shipping_date is not null
)

select
    cast(strftime(date_day, '%Y%m%d') as integer) as date_key,
    date_day,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    extract(quarter from date_day) as quarter,
    extract(dow from date_day) as day_of_week,
    strftime(date_day, '%Y-%m') as year_month,
    strftime(date_day, '%B') as month_name
from dates
