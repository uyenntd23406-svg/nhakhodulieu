import duckdb

con = duckdb.connect("warehouse/logistics.duckdb")

def scalar(sql):
    return con.execute(sql).fetchone()[0]

print("=== ROW COUNT RECONCILIATION ===")
bronze = scalar("SELECT COUNT(*) FROM bronze.orders_raw")
stg_orders = scalar("SELECT COUNT(*) FROM silver.stg_orders")
int_metrics = scalar("SELECT COUNT(*) FROM silver.int_delivery_metrics")
fact = scalar("SELECT COUNT(*) FROM gold.fct_order_items")
ml = scalar("SELECT COUNT(*) FROM gold.mart_ml_delivery_risk_features")

print(f"bronze.orders_raw: {bronze:,}")
print(f"silver.stg_orders: {stg_orders:,}")
print(f"silver.int_delivery_metrics: {int_metrics:,}")
print(f"gold.fct_order_items: {fact:,}")
print(f"gold.mart_ml_delivery_risk_features: {ml:,}")
print("grain_rows_equal:", "PASS" if stg_orders == int_metrics == fact == ml else "CHECK")

print("\n=== DIMENSION UNIQUENESS CHECK ===")
checks = [
    ("dim_customer", "customer_key"),
    ("dim_product", "product_key"),
    ("dim_location", "location_key"),
    ("dim_shipping", "shipping_key"),
    ("dim_date", "date_key"),
]

for tbl, key in checks:
    total = scalar(f"SELECT COUNT(*) FROM gold.{tbl}")
    distinct_key = scalar(f"SELECT COUNT(DISTINCT {key}) FROM gold.{tbl}")
    null_key = scalar(f"SELECT SUM(CASE WHEN {key} IS NULL THEN 1 ELSE 0 END) FROM gold.{tbl}")
    status = "PASS" if total == distinct_key and null_key == 0 else "CHECK"
    print(f"{tbl}.{key}: total={total:,}, distinct={distinct_key:,}, null={null_key}, status={status}")

print("\n=== FACT FOREIGN KEY ORPHAN CHECK ===")
queries = {
    "customer_orphan": """
        SELECT COUNT(*)
        FROM gold.fct_order_items f
        LEFT JOIN gold.dim_customer d
            ON f.customer_key = d.customer_key
        WHERE d.customer_key IS NULL
    """,
    "product_orphan": """
        SELECT COUNT(*)
        FROM gold.fct_order_items f
        LEFT JOIN gold.dim_product d
            ON f.product_key = d.product_key
        WHERE d.product_key IS NULL
    """,
    "location_orphan": """
        SELECT COUNT(*)
        FROM gold.fct_order_items f
        LEFT JOIN gold.dim_location d
            ON f.location_key = d.location_key
        WHERE d.location_key IS NULL
    """,
    "shipping_orphan": """
        SELECT COUNT(*)
        FROM gold.fct_order_items f
        LEFT JOIN gold.dim_shipping d
            ON f.shipping_key = d.shipping_key
        WHERE d.shipping_key IS NULL
    """,
}

for name, q in queries.items():
    v = scalar(q)
    print(f"{name}: {v} | {'PASS' if v == 0 else 'CHECK'}")

print("\n=== MART ITEM COUNT RECONCILIATION ===")
mart_delivery_items = scalar("SELECT SUM(order_item_count) FROM gold.mart_delivery_performance")
mart_sales_items = scalar("SELECT SUM(order_item_count) FROM gold.mart_sales_profitability")
mart_exec_items = scalar("SELECT SUM(total_order_items) FROM gold.mart_executive_summary")

print(f"delivery mart item sum: {mart_delivery_items:,} | {'PASS' if mart_delivery_items == fact else 'CHECK'}")
print(f"sales mart item sum: {mart_sales_items:,} | {'PASS' if mart_sales_items == fact else 'CHECK'}")
print(f"executive mart item sum: {mart_exec_items:,} | {'PASS' if mart_exec_items == fact else 'CHECK'}")

print("\n=== KPI RECONCILIATION: mart_supply_chain_kpi vs fact ===")
print(con.execute("""
WITH fact_kpi AS (
    SELECT
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(*) AS total_order_items,
        COUNT(DISTINCT customer_key) AS total_customers,
        COUNT(DISTINCT product_key) AS total_products,
        SUM(sales_amount) AS total_sales,
        SUM(profit_amount) AS total_profit,
        AVG(CAST(is_late_delivery AS DOUBLE)) AS late_delivery_rate
    FROM gold.fct_order_items
),
mart AS (
    SELECT
        total_orders,
        total_order_items,
        total_customers,
        total_products,
        total_sales,
        total_profit,
        late_delivery_rate
    FROM gold.mart_supply_chain_kpi
)
SELECT
    fact_kpi.total_orders AS fact_total_orders,
    mart.total_orders AS mart_total_orders,
    fact_kpi.total_order_items AS fact_total_items,
    mart.total_order_items AS mart_total_items,
    fact_kpi.total_customers AS fact_total_customers,
    mart.total_customers AS mart_total_customers,
    fact_kpi.total_products AS fact_total_products,
    mart.total_products AS mart_total_products,
    ROUND(fact_kpi.total_sales, 4) AS fact_sales,
    ROUND(mart.total_sales, 4) AS mart_sales,
    ROUND(fact_kpi.total_profit, 4) AS fact_profit,
    ROUND(mart.total_profit, 4) AS mart_profit,
    ROUND(fact_kpi.late_delivery_rate, 6) AS fact_late_rate,
    ROUND(mart.late_delivery_rate, 6) AS mart_late_rate
FROM fact_kpi, mart
""").fetchdf().to_string(index=False))
