import duckdb

DB_PATH = "warehouse/logistics.duckdb"
con = duckdb.connect(DB_PATH)

models = [
    "bronze.orders_raw",

    "silver.stg_orders",
    "silver.stg_customers",
    "silver.stg_products",
    "silver.int_order_enriched",
    "silver.int_delivery_metrics",

    "gold.dim_date",
    "gold.dim_customer",
    "gold.dim_product",
    "gold.dim_location",
    "gold.dim_shipping",
    "gold.fct_order_items",

    "gold.mart_supply_chain_kpi",
    "gold.mart_delivery_performance",
    "gold.mart_sales_profitability",
    "gold.mart_ml_delivery_risk_features",
    "gold.mart_executive_summary",
]

print("=== TABLES / VIEWS BY LAYER ===")
print(con.execute("""
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema IN ('bronze', 'silver', 'gold')
ORDER BY table_schema, table_name
""").fetchdf().to_string(index=False))

print("\n=== ROW COUNTS ===")
for m in models:
    try:
        cnt = con.execute(f"SELECT COUNT(*) FROM {m}").fetchone()[0]
        print(f"{m}: {cnt:,}")
    except Exception as e:
        print(f"{m}: ERROR - {e}")

print("\n=== SILVER SAMPLE: stg_orders ===")
print(con.execute("""
SELECT
    order_item_id,
    order_id,
    order_date,
    shipping_date,
    order_year_month,
    market,
    shipping_mode,
    delivery_status,
    late_delivery_risk,
    sales_per_customer,
    order_item_total
FROM silver.stg_orders
LIMIT 10
""").fetchdf().to_string(index=False))

print("\n=== SILVER SAMPLE: int_delivery_metrics ===")
print(con.execute("""
SELECT
    order_item_id,
    order_id,
    order_year_month,
    market,
    shipping_mode,
    delivery_status,
    days_for_shipping_real,
    days_for_shipment_scheduled,
    shipping_variance,
    is_late_delivery,
    gross_profit_margin,
    total_cost
FROM silver.int_delivery_metrics
LIMIT 10
""").fetchdf().to_string(index=False))

print("\n=== GOLD SAMPLE: fct_order_items ===")
print(con.execute("""
SELECT
    order_item_id,
    order_id,
    order_date_key,
    shipping_date_key,
    customer_key,
    product_key,
    location_key,
    shipping_key,
    sales_amount,
    profit_amount,
    late_delivery_risk,
    shipping_variance
FROM gold.fct_order_items
LIMIT 10
""").fetchdf().to_string(index=False))

print("\n=== MART SAMPLE: mart_supply_chain_kpi ===")
print(con.execute("""
SELECT *
FROM gold.mart_supply_chain_kpi
""").fetchdf().to_string(index=False))

print("\n=== MART SAMPLE: mart_delivery_performance ===")
print(con.execute("""
SELECT *
FROM gold.mart_delivery_performance
LIMIT 10
""").fetchdf().to_string(index=False))

print("\n=== DATE KEY COVERAGE ===")
print(con.execute("""
SELECT
    COUNT(*) AS fact_rows,
    SUM(CASE WHEN order_date_key IS NULL THEN 1 ELSE 0 END) AS null_order_date_key,
    SUM(CASE WHEN shipping_date_key IS NULL THEN 1 ELSE 0 END) AS null_shipping_date_key
FROM gold.fct_order_items
""").fetchdf().to_string(index=False))
