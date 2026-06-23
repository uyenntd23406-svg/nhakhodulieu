{{ config(materialized='table', schema='gold') }}

with locations as (
    select distinct
        market,
        order_region,
        order_country,
        order_city,
        order_state,
        order_zipcode
    from {{ ref('int_delivery_metrics') }}
)

select
    row_number() over (
        order by market, order_region, order_country, order_city, order_state, order_zipcode
    ) as location_key,
    market,
    order_region,
    order_country,
    order_city,
    order_state,
    order_zipcode
from locations
