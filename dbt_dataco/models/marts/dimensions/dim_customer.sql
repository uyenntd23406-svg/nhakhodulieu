{{ config(materialized='table', schema='gold') }}

select
    customer_id as customer_key,
    customer_id,
    customer_segment,
    customer_city,
    customer_country,
    customer_state,
    customer_zipcode,
    customer_latitude,
    customer_longitude
from {{ ref('stg_customers') }}
