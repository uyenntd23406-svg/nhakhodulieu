from pathlib import Path
import sys
import duckdb

# Fix Unicode output on Windows PowerShell/cp1252 terminals.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = Path("warehouse/logistics.duckdb")
EVIDENCE_DIR = Path("reports/evidence_final")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_CSV = EVIDENCE_DIR / "36a_silver_stg_orders_feedback_sample.csv"

if not DB_PATH.exists():
    raise SystemExit(f"Database not found: {DB_PATH.resolve()}")

con = duckdb.connect(str(DB_PATH), read_only=True)

def print_section(title):
    print()
    print("=" * 90)
    print(title)
    print("=" * 90)

def show_sql(title, sql):
    print_section(title)
    df = con.execute(sql).fetchdf()
    print(df.to_string(index=False))
    return df

print_section("VERIFY SILVER.STG_ORDERS - FEEDBACK CHECK")
print("Database:", DB_PATH.resolve())
print("Target table/view: silver.stg_orders")

show_sql(
    "1. KIỂM TRA VIEW silver.stg_orders CÓ TỒN TẠI KHÔNG",
    """
    SELECT
        table_schema,
        table_name,
        table_type
    FROM information_schema.tables
    WHERE table_schema = 'silver'
      AND table_name = 'stg_orders'
    """
)

show_sql(
    "2. KIỂM TRA SỐ DÒNG VÀ TÍNH DUY NHẤT CỦA order_item_id",
    """
    SELECT
        COUNT(*) AS total_rows,
        COUNT(DISTINCT order_item_id) AS distinct_order_item_id,
        COUNT(*) - COUNT(DISTINCT order_item_id) AS duplicated_order_item_id
    FROM silver.stg_orders
    """
)

show_sql(
    "3. KIỂM TRA NULL Ở CÁC CỘT QUAN TRỌNG",
    """
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
    """
)

show_sql(
    "4. KIỂM TRA MIỀN THỜI GIAN SAU KHI PARSE DATE",
    """
    SELECT
        MIN(order_date) AS min_order_date,
        MAX(order_date) AS max_order_date,
        MIN(shipping_date) AS min_shipping_date,
        MAX(shipping_date) AS max_shipping_date,
        COUNT(DISTINCT order_year_month) AS distinct_order_year_month
    FROM silver.stg_orders
    """
)

show_sql(
    "5. PHÂN BỐ MARKET",
    """
    SELECT
        market,
        COUNT(*) AS row_count
    FROM silver.stg_orders
    GROUP BY market
    ORDER BY row_count DESC
    """
)

show_sql(
    "6. PHÂN BỐ SHIPPING_MODE",
    """
    SELECT
        shipping_mode,
        COUNT(*) AS row_count
    FROM silver.stg_orders
    GROUP BY shipping_mode
    ORDER BY row_count DESC
    """
)

show_sql(
    "7. PHÂN BỐ DELIVERY_STATUS",
    """
    SELECT
        delivery_status,
        COUNT(*) AS row_count
    FROM silver.stg_orders
    GROUP BY delivery_status
    ORDER BY row_count DESC
    """
)

show_sql(
    "8. PHÂN BỐ LATE_DELIVERY_RISK",
    """
    SELECT
        late_delivery_risk,
        COUNT(*) AS row_count
    FROM silver.stg_orders
    GROUP BY late_delivery_risk
    ORDER BY late_delivery_risk
    """
)

show_sql(
    "9. KIỂM TRA KHOẢNG GIÁ TRỊ CÁC CỘT VẬN CHUYỂN VÀ TÀI CHÍNH",
    """
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
    """
)

sample_sql = """
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

sample_df = show_sql(
    "10. BẢNG DATA MẪU silver.stg_orders - 10 DÒNG ĐẦU THEO order_item_id",
    sample_sql
)

sample_df.to_csv(SAMPLE_CSV, index=False, encoding="utf-8-sig")

print_section("EXPORT SAMPLE CSV")
print("Saved sample CSV:", SAMPLE_CSV.resolve())

print_section("KẾT LUẬN VERIFY silver.stg_orders")
print("PASS nếu các điều kiện sau đúng:")
print("- total_rows = 180,519")
print("- duplicated_order_item_id = 0")
print("- các cột khóa và cột phân tích quan trọng không bị null bất thường")
print("- order_date và shipping_date parse được, có min/max hợp lệ")
print("- market, shipping_mode, delivery_status, late_delivery_risk có phân bố hợp lệ")
print("- sample CSV đã được export để chèn vào báo cáo hoặc gửi Lead kiểm tra")

