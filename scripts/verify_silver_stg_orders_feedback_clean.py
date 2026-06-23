from pathlib import Path
import duckdb

DB_PATH = Path("warehouse/logistics.duckdb")
EVIDENCE_DIR = Path("reports/evidence_final")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = EVIDENCE_DIR / "36_verify_silver_stg_orders_feedback_clean.txt"
SAMPLE_CSV = EVIDENCE_DIR / "36a_silver_stg_orders_feedback_sample.csv"
SUMMARY_CSV = EVIDENCE_DIR / "36b_silver_stg_orders_feedback_summary.csv"

if not DB_PATH.exists():
    raise SystemExit(f"Database not found: {DB_PATH.resolve()}")

con = duckdb.connect(str(DB_PATH), read_only=True)

queries = {
"01_view_exists": """
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'silver'
  AND table_name = 'stg_orders'
""",

"02_row_count_unique": """
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_item_id) AS distinct_order_item_id,
    COUNT(*) - COUNT(DISTINCT order_item_id) AS duplicated_order_item_id
FROM silver.stg_orders
""",

"03_null_check": """
SELECT
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS null_order_id,
    SUM(CASE WHEN order_item_id IS NULL THEN 1 ELSE 0 END) AS null_order_item_id,
    SUM(CASE WHEN order_customer_id IS NULL THEN 1 ELSE 0 END) AS null_order_customer_id,
    SUM(CASE WHEN product_card_id IS NULL THEN 1 ELSE 0 END) AS null_product_card_id,
    SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS null_order_date,
    SUM(CASE WHEN shipping_date IS NULL THEN 1 ELSE 0 END) AS null_shipping_date,
    SUM(CASE WHEN market IS NULL OR trim(market) = '' THEN 1 ELSE 0 END) AS null_market,
    SUM(CASE WHEN shipping_mode IS NULL OR trim(shipping_mode) = '' THEN 1 ELSE 0 END) AS null_shipping_mode,
    SUM(CASE WHEN delivery_status IS NULL OR trim(delivery_status) = '' THEN 1 ELSE 0 END) AS null_delivery_status,
    SUM(CASE WHEN late_delivery_risk IS NULL THEN 1 ELSE 0 END) AS null_late_delivery_risk
FROM silver.stg_orders
""",

"04_date_range": """
SELECT
    MIN(order_date) AS min_order_date,
    MAX(order_date) AS max_order_date,
    MIN(shipping_date) AS min_shipping_date,
    MAX(shipping_date) AS max_shipping_date,
    COUNT(DISTINCT order_year_month) AS distinct_order_year_month
FROM silver.stg_orders
""",

"05_market_distribution": """
SELECT
    market,
    COUNT(*) AS row_count
FROM silver.stg_orders
GROUP BY market
ORDER BY row_count DESC
""",

"06_shipping_mode_distribution": """
SELECT
    shipping_mode,
    COUNT(*) AS row_count
FROM silver.stg_orders
GROUP BY shipping_mode
ORDER BY row_count DESC
""",

"07_delivery_status_distribution": """
SELECT
    delivery_status,
    COUNT(*) AS row_count
FROM silver.stg_orders
GROUP BY delivery_status
ORDER BY row_count DESC
""",

"08_late_delivery_risk_distribution": """
SELECT
    late_delivery_risk,
    COUNT(*) AS row_count
FROM silver.stg_orders
GROUP BY late_delivery_risk
ORDER BY late_delivery_risk
""",

"09_range_check": """
SELECT
    MIN(days_for_shipping_real) AS min_days_real,
    MAX(days_for_shipping_real) AS max_days_real,
    MIN(days_for_shipment_scheduled) AS min_days_scheduled,
    MAX(days_for_shipment_scheduled) AS max_days_scheduled,
    MIN(delivery_delay_days) AS min_delivery_delay,
    MAX(delivery_delay_days) AS max_delivery_delay,
    MIN(sales) AS min_sales,
    MAX(sales) AS max_sales,
    MIN(order_item_total) AS min_order_item_total,
    MAX(order_item_total) AS max_order_item_total,
    MIN(order_item_quantity) AS min_quantity,
    MAX(order_item_quantity) AS max_quantity
FROM silver.stg_orders
""",

"10_sample_rows": """
SELECT
    order_id,
    order_item_id,
    order_customer_id,
    product_card_id,
    order_date,
    shipping_date,
    order_year_month,
    market,
    order_region,
    order_country,
    shipping_mode,
    delivery_status,
    order_status,
    late_delivery_risk,
    days_for_shipping_real,
    days_for_shipment_scheduled,
    delivery_delay_days,
    sales,
    order_item_total,
    order_profit_per_order,
    order_item_quantity
FROM silver.stg_orders
ORDER BY order_item_id
LIMIT 10
"""
}

summary_rows = []

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("VERIFY SILVER.STG_ORDERS FEEDBACK CHECK CLEAN VERSION\n")
    f.write(f"Database: {DB_PATH.resolve()}\n")
    f.write("Target: silver.stg_orders\n\n")

    for name, sql in queries.items():
        df = con.execute(sql).fetchdf()

        f.write("=" * 100 + "\n")
        f.write(name + "\n")
        f.write("=" * 100 + "\n")
        f.write(df.to_string(index=False))
        f.write("\n\n")

        if name == "10_sample_rows":
            df.to_csv(SAMPLE_CSV, index=False, encoding="utf-8-sig")

# Build compact summary for report
row_df = con.execute(queries["02_row_count_unique"]).fetchdf()
null_df = con.execute(queries["03_null_check"]).fetchdf()
date_df = con.execute(queries["04_date_range"]).fetchdf()
range_df = con.execute(queries["09_range_check"]).fetchdf()

summary_rows.append({
    "check_group": "row_count_unique",
    "metric": "total_rows",
    "value": int(row_df.loc[0, "total_rows"]),
    "status": "PASS" if int(row_df.loc[0, "total_rows"]) == 180519 else "CHECK"
})
summary_rows.append({
    "check_group": "row_count_unique",
    "metric": "duplicated_order_item_id",
    "value": int(row_df.loc[0, "duplicated_order_item_id"]),
    "status": "PASS" if int(row_df.loc[0, "duplicated_order_item_id"]) == 0 else "CHECK"
})

for col in null_df.columns:
    value = int(null_df.loc[0, col])
    summary_rows.append({
        "check_group": "null_check",
        "metric": col,
        "value": value,
        "status": "PASS" if value == 0 else "CHECK"
    })

summary_rows.append({
    "check_group": "date_range",
    "metric": "min_order_date",
    "value": str(date_df.loc[0, "min_order_date"]),
    "status": "INFO"
})
summary_rows.append({
    "check_group": "date_range",
    "metric": "max_order_date",
    "value": str(date_df.loc[0, "max_order_date"]),
    "status": "INFO"
})
summary_rows.append({
    "check_group": "date_range",
    "metric": "min_shipping_date",
    "value": str(date_df.loc[0, "min_shipping_date"]),
    "status": "INFO"
})
summary_rows.append({
    "check_group": "date_range",
    "metric": "max_shipping_date",
    "value": str(date_df.loc[0, "max_shipping_date"]),
    "status": "INFO"
})
summary_rows.append({
    "check_group": "date_range",
    "metric": "distinct_order_year_month",
    "value": int(date_df.loc[0, "distinct_order_year_month"]),
    "status": "INFO"
})

for col in range_df.columns:
    summary_rows.append({
        "check_group": "range_check",
        "metric": col,
        "value": str(range_df.loc[0, col]),
        "status": "INFO"
    })

summary = duckdb.query("SELECT * FROM summary_rows").fetchdf() if False else None

import pandas as pd
pd.DataFrame(summary_rows).to_csv(SUMMARY_CSV, index=False, encoding="utf-8-sig")

print("DONE")
print(f"Log file: {LOG_PATH}")
print(f"Sample CSV: {SAMPLE_CSV}")
print(f"Summary CSV: {SUMMARY_CSV}")
print("Key result: silver.stg_orders verified. Check the log and CSV files.")
