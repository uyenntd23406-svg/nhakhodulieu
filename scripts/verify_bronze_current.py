import duckdb
from pathlib import Path

DB_PATH = "warehouse/logistics.duckdb"
con = duckdb.connect(DB_PATH)

print("=== DATABASE CHECK ===")
print("DB exists:", Path(DB_PATH).exists())
print("DB size MB:", round(Path(DB_PATH).stat().st_size / 1024 / 1024, 2))

print("\n=== SCHEMAS ===")
print(con.execute("""
SELECT schema_name
FROM information_schema.schemata
ORDER BY schema_name
""").fetchdf().to_string(index=False))

print("\n=== TABLES / VIEWS IN BRONZE/SILVER/GOLD ===")
print(con.execute("""
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema IN ('bronze', 'silver', 'gold')
ORDER BY table_schema, table_name
""").fetchdf().to_string(index=False))

print("\n=== BRONZE ROW COUNT ===")
print(con.execute("""
SELECT COUNT(*) AS bronze_rows
FROM bronze.orders_raw
""").fetchdf().to_string(index=False))

print("\n=== BRONZE DESCRIBE ===")
print(con.execute("""
DESCRIBE bronze.orders_raw
""").fetchdf().to_string(index=False))

print("\n=== BRONZE SAMPLE 5 ROWS ===")
print(con.execute("""
SELECT *
FROM bronze.orders_raw
LIMIT 5
""").fetchdf().to_string(index=False))

print("\n=== REQUIRED COLUMN CHECK ===")
required = [
    "order_id",
    "order_item_id",
    "order_customer_id",
    "product_card_id",
    "customer_id",
    "customer_segment",
    "product_name",
    "market",
    "shipping_mode",
    "delivery_status",
    "late_delivery_risk",
    "sales_per_customer",
    "order_item_total",
    "order_date_(dateorders)",
    "shipping_date_(dateorders)",
    "days_for_shipping_(real)",
    "days_for_shipment_(scheduled)"
]

cols = set(con.execute("DESCRIBE bronze.orders_raw").fetchdf()["column_name"].tolist())

for c in required:
    print(f"{c}: {'PASS' if c in cols else 'MISSING'}")

print("\n=== DATE RAW SAMPLE ===")
date_cols = [c for c in ["order_date_(dateorders)", "shipping_date_(dateorders)"] if c in cols]
if len(date_cols) == 2:
    print(con.execute("""
    SELECT
        "order_date_(dateorders)" AS order_date_raw,
        "shipping_date_(dateorders)" AS shipping_date_raw
    FROM bronze.orders_raw
    LIMIT 20
    """).fetchdf().to_string(index=False))
else:
    print("DATE COLUMNS MISSING - cần kiểm tra lại tên cột ngày trong Bronze.")
