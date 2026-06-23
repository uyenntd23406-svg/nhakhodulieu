{{ config(materialized='view', schema='silver') }}

with source_data as (
    select
        *,
        coalesce(
            try_strptime(trim(cast("order_date_(dateorders)" as varchar)), '%m/%d/%Y %H:%M'),
            try_strptime(trim(cast("order_date_(dateorders)" as varchar)), '%m/%d/%Y %H:%M:%S'),
            try_cast(trim(cast("order_date_(dateorders)" as varchar)) as timestamp)
        ) as parsed_order_date,

        coalesce(
            try_strptime(trim(cast("shipping_date_(dateorders)" as varchar)), '%m/%d/%Y %H:%M'),
            try_strptime(trim(cast("shipping_date_(dateorders)" as varchar)), '%m/%d/%Y %H:%M:%S'),
            try_cast(trim(cast("shipping_date_(dateorders)" as varchar)) as timestamp)
        ) as parsed_shipping_date

    from {{ source('bronze', 'orders_raw') }}
)

select
    cast(order_id as bigint) as order_id,
    cast(order_item_id as bigint) as order_item_id,
    cast(order_customer_id as bigint) as order_customer_id,
    cast(product_card_id as bigint) as product_card_id,
    cast(order_item_cardprod_id as bigint) as order_item_cardprod_id,

    parsed_order_date as order_date,
    parsed_shipping_date as shipping_date,
    strftime(parsed_order_date, '%Y-%m') as order_year_month,

    trim(cast(type as varchar)) as transaction_type,
    trim(cast(market as varchar)) as market,
    trim(cast(order_region as varchar)) as order_region,
    trim(cast(order_country as varchar)) as order_country,
    trim(cast(order_city as varchar)) as order_city,
    trim(cast(order_state as varchar)) as order_state,
    cast(order_zipcode as double) as order_zipcode,

    trim(cast(shipping_mode as varchar)) as shipping_mode,
    trim(cast(delivery_status as varchar)) as delivery_status,
    trim(cast(order_status as varchar)) as order_status,
    cast(late_delivery_risk as integer) as late_delivery_risk,

    cast("days_for_shipping_(real)" as integer) as days_for_shipping_real,
    cast("days_for_shipment_(scheduled)" as integer) as days_for_shipment_scheduled,

    cast("days_for_shipping_(real)" as integer)
      - cast("days_for_shipment_(scheduled)" as integer) as delivery_delay_days,

    cast(sales_per_customer as double) as sales_per_customer,
    cast(sales as double) as sales,
    cast(order_item_total as double) as order_item_total,
    cast(benefit_per_order as double) as benefit_per_order,
    cast(order_profit_per_order as double) as order_profit_per_order,

    cast(order_item_discount as double) as order_item_discount,
    cast(order_item_discount_rate as double) as order_item_discount_rate,
    cast(order_item_product_price as double) as order_item_product_price,
    cast(order_item_profit_ratio as double) as order_item_profit_ratio,
    cast(order_item_quantity as integer) as order_item_quantity

from source_data
