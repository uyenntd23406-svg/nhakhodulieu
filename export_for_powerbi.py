import os
import duckdb
import pandas as pd
from dotenv import load_dotenv

# 1. Đọc token từ file .env
load_dotenv()
token = os.getenv("MOTHERDUCK_TOKEN")
if not token:
    raise ValueError("Không tìm thấy MOTHERDUCK_TOKEN trong file .env")

# 2. Kết nối tới MotherDuck và chọn đúng schema
conn = duckdb.connect(f"md:?motherduck_token={token}")
conn.execute("USE dataco_warehouse_cloud.gold;")

# 3. Danh sách bảng export
tables = [
    ("01_mart_supply_chain_kpi", "mart_supply_chain_kpi"),
    ("02_mart_delivery_performance", "mart_delivery_performance"),
    ("03_mart_sales_profitability", "mart_sales_profitability"),
    ("04_mart_executive_summary", "mart_executive_summary"),
    ("05_fct_order_items", "fct_order_items"),
    ("06_dim_date", "dim_date"),
    ("07_dim_customer", "dim_customer"),
    ("08_dim_product", "dim_product"),
    ("09_dim_location", "dim_location"),
    ("10_dim_shipping", "dim_shipping"),
]

# 4. Tạo thư mục output
output_dir = "powerbi_data"
os.makedirs(output_dir, exist_ok=True)

# 5. Export từng bảng
for file_prefix, table_name in tables:
    print(f"Đang export {table_name}...")
    df = conn.execute(f"SELECT * FROM {table_name}").fetchdf()
    file_path = os.path.join(output_dir, f"{file_prefix}.csv")
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"  -> Đã lưu {len(df)} dòng vào {file_path}")

print("✅ Export hoàn tất! Các file nằm trong thư mục powerbi_data/")