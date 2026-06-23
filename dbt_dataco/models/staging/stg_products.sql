{{ config(materialized='view', schema='silver') }}

with source_data as (
    select
        cast(product_card_id as bigint) as product_card_id,
        cast(product_category_id as bigint) as product_category_id,
        trim(cast(product_name as varchar)) as product_name,
        cast(product_price as double) as product_price,
        cast(product_status as integer) as product_status,

        cast(category_id as bigint) as category_id,
        trim(cast(category_name as varchar)) as category_name,
        cast(department_id as bigint) as department_id,
        trim(cast(department_name as varchar)) as department_name,

        cast(product_description as double) as product_description,
        cast(product_image as varchar) as product_image,

        row_number() over (
            partition by cast(product_card_id as bigint)
            order by cast(product_card_id as bigint)
        ) as rn

    from {{ source('bronze', 'orders_raw') }}
    where product_card_id is not null
)

select
    product_card_id,
    product_category_id,
    product_name,
    product_price,
    product_status,
    category_id,
    category_name,
    department_id,
    department_name,
    product_description,
    product_image
from source_data
where rn = 1
