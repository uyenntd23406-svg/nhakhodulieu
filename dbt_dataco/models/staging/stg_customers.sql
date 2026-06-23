{{ config(materialized='view', schema='silver') }}

with source_data as (
    select
        cast(customer_id as bigint) as customer_id,
        trim(cast(customer_segment as varchar)) as customer_segment,
        trim(cast(customer_city as varchar)) as customer_city,
        trim(cast(customer_country as varchar)) as customer_country,
        trim(cast(customer_state as varchar)) as customer_state,
        cast(customer_zipcode as double) as customer_zipcode,
        cast(latitude as double) as customer_latitude,
        cast(longitude as double) as customer_longitude,

        row_number() over (
            partition by cast(customer_id as bigint)
            order by cast(customer_id as bigint)
        ) as rn

    from {{ source('bronze', 'orders_raw') }}
    where customer_id is not null
)

select
    customer_id,
    customer_segment,
    customer_city,
    customer_country,
    customer_state,
    customer_zipcode,
    customer_latitude,
    customer_longitude
from source_data
where rn = 1
