{{ config(materialized='table', schema='gold') }}

with shipping as (
    select distinct
        shipping_mode,
        delivery_status,
        order_status
    from {{ ref('int_delivery_metrics') }}
)

select
    row_number() over (
        order by shipping_mode, delivery_status, order_status
    ) as shipping_key,
    shipping_mode,
    delivery_status,
    order_status
from shipping
