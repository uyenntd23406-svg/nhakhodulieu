{{ config(materialized='table', schema='gold') }}

select
    product_card_id as product_key,
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
from {{ ref('stg_products') }}
