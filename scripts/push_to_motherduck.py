import os
import sys
import duckdb

EXECUTE = "--execute" in sys.argv

LOCAL_DB = "warehouse/logistics.duckdb"
CLOUD_DB = (os.getenv("MOTHERDUCK_DATABASE") or "dataco_warehouse_cloud").strip()
TOKEN = (os.getenv("MOTHERDUCK_TOKEN") or "").strip().strip('"').strip("'")

if not TOKEN:
    raise SystemExit(
        "MISSING MOTHERDUCK_TOKEN. Set env var first."
    )

if len(TOKEN) < 30:
    raise SystemExit("MOTHERDUCK_TOKEN looks too short. Please check token value.")

def qident(name: str) -> str:
    # Quote identifier safely for database/schema/table names
    return '"' + name.replace('"', '""') + '"'

con = duckdb.connect(LOCAL_DB)

print("=== LOAD MOTHERDUCK EXTENSION ===")
con.execute("INSTALL motherduck")
con.execute("LOAD motherduck")

print("=== CONNECT MOTHERDUCK WORKSPACE ===")
print("Cloud DB:", CLOUD_DB)
print("Execute mode:", EXECUTE)

# Không print token ra log
con.execute(f"SET motherduck_token='{TOKEN}'")

# Quan trọng: attach workspace trước, không attach database chưa tồn tại
con.execute("ATTACH 'md:'")

print("\n=== ENSURE CLOUD DATABASE EXISTS ===")
if EXECUTE:
    con.execute(f"CREATE DATABASE IF NOT EXISTS {qident(CLOUD_DB)}")
    print(f"CREATE DATABASE IF NOT EXISTS {CLOUD_DB}: DONE")
else:
    print(f"DRY-RUN | would CREATE DATABASE IF NOT EXISTS {CLOUD_DB}")

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

print("\n=== CLOUD PUSH PLAN ===")

for obj in objects:
    schema, table = obj.split(".")
    local_count = con.execute(f"SELECT COUNT(*) FROM {obj}").fetchone()[0]

    target_schema = f"{qident(CLOUD_DB)}.{qident(schema)}"
    target_table = f"{qident(CLOUD_DB)}.{qident(schema)}.{qident(table)}"

    print(f"PLAN | {obj:45} | local_rows={local_count:,}")

    if EXECUTE:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {target_schema}")
        con.execute(f"""
            CREATE OR REPLACE TABLE {target_table} AS
            SELECT * FROM {obj}
        """)

        cloud_count = con.execute(
            f"SELECT COUNT(*) FROM {target_table}"
        ).fetchone()[0]

        status = "PASS" if cloud_count == local_count else "CHECK"
        print(
            f"PUSHED | {CLOUD_DB}.{schema}.{table:35} "
            f"| cloud_rows={cloud_count:,} | {status}"
        )

print("\n=== CLOUD PUSH DONE ===")
if EXECUTE:
    print("Execute mode completed. Data was written/replaced on cloud.")
else:
    print("Dry-run only. No data was written to cloud.")
