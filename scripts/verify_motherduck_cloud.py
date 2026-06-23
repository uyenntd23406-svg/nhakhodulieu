import os
import duckdb

TOKEN = (os.getenv("MOTHERDUCK_TOKEN") or "").strip()
CLOUD_DB = (os.getenv("MOTHERDUCK_DATABASE") or "dataco_warehouse_cloud").strip()

if not TOKEN:
    raise SystemExit("MISSING MOTHERDUCK_TOKEN")

def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'

con = duckdb.connect()
con.execute("INSTALL motherduck")
con.execute("LOAD motherduck")
con.execute(f"SET motherduck_token='{TOKEN}'")
con.execute("ATTACH 'md:'")

objects = [
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

print("=== MOTHERDUCK CLOUD VERIFY ===")
print("Cloud DB:", CLOUD_DB)

print("\n=== CLOUD TABLE ROW COUNTS ===")
for obj in objects:
    schema, table = obj.split(".")
    target = f"{qident(CLOUD_DB)}.{qident(schema)}.{qident(table)}"
    cnt = con.execute(f"SELECT COUNT(*) FROM {target}").fetchone()[0]
    print(f"{CLOUD_DB}.{schema}.{table}: {cnt:,}")

print("\n=== CLOUD KPI SAMPLE ===")
print(con.execute(f"""
SELECT *
FROM {qident(CLOUD_DB)}.gold.mart_supply_chain_kpi
""").fetchdf().to_string(index=False))

print("\n=== CLOUD FACT DATE KEY COVERAGE ===")
print(con.execute(f"""
SELECT
    COUNT(*) AS fact_rows,
    SUM(CASE WHEN order_date_key IS NULL THEN 1 ELSE 0 END) AS null_order_date_key,
    SUM(CASE WHEN shipping_date_key IS NULL THEN 1 ELSE 0 END) AS null_shipping_date_key
FROM {qident(CLOUD_DB)}.gold.fct_order_items
""").fetchdf().to_string(index=False))
