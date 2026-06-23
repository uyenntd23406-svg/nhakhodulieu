import sys
import os
from dotenv import load_dotenv
import pandas as pd
import duckdb
from validation import validate_data

# Load environment variables from .env
load_dotenv()

CSV_PATH = os.getenv("DATACO_CSV_PATH", "data/DataCoSupplyChainDataset.csv")
DB_PATH = os.getenv("DUCKDB_PATH", "warehouse/logistics.duckdb")
DB_DIR = os.path.dirname(DB_PATH) or "."
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN", "")
CLOUD_DB_NAME = os.getenv("MOTHERDUCK_DB", "logistics_lakehouse")

print("1. Đang trích xuất dữ liệu (Extract)...")
df = pd.read_csv(CSV_PATH, encoding="latin-1", low_memory=False)

print("2. Đang chuẩn hóa tên thuộc tính (Standardize Schema)...")
# Ghi nhận log quá trình đổi tên để đối chiếu
old_columns = list(df.columns[:3]) # Lấy ví dụ 3 cột đầu
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)
new_columns = list(df.columns[:3])
print(f"   Ví dụ đổi tên: {old_columns} -> {new_columns}")

print("3. Đang kiểm định chất lượng dữ liệu (Validate)...")
is_valid, report_path = validate_data(df)

if not is_valid:
    print(f"DỮ LIỆU KHÔNG HỢP LỆ! Pipeline đã bị dừng trước khi Load vào Data Warehouse.")
    print(f"Xem chi tiết lỗi tại: {report_path}")
    sys.exit(1)

print(f"Kiểm định thành công (PASS). Xem báo cáo chi tiết tại: {report_path}")
print("4. Đang nạp dữ liệu vào Bronze Layer (Load Local DuckDB)...")

# Hàm đồng bộ dữ liệu lên MotherDuck Cloud 
def sync_to_motherduck(local_conn):

    if not MOTHERDUCK_TOKEN:
        print("5. MOTHERDUCK_TOKEN chưa được cấu hình → bỏ qua đồng bộ cloud.")
        return

    print("5. Đang đồng bộ dữ liệu lên MotherDuck Cloud...")

    try:

        # Lấy dữ liệu từ Bronze Local
        bronze_df = local_conn.execute("""
            SELECT *
            FROM bronze.orders_raw
        """).df()

        print(
            f"   Đọc được {len(bronze_df):,} dòng từ Local Bronze Layer.")

        # Kết nối MotherDuck
        cloud_conn = duckdb.connect(
            f"md:{CLOUD_DB_NAME}"
            f"?motherduck_token={MOTHERDUCK_TOKEN}")

        cloud_conn.execute("""
            CREATE SCHEMA IF NOT EXISTS bronze
        """)

        # Đăng ký dataframe tạm
        cloud_conn.register("temp_orders", bronze_df)

        # Ghi lên cloud
        cloud_conn.execute("""
            CREATE OR REPLACE TABLE bronze.orders_raw AS
            SELECT *
            FROM temp_orders
        """)

        cloud_count = cloud_conn.execute("""
            SELECT COUNT(*)
            FROM bronze.orders_raw
        """).fetchone()[0]

        print(f"✓ Đồng bộ thành công {cloud_count:,} dòng lên MotherDuck.")

    except Exception as e:

        print(f"Đồng bộ cloud thất bại: {e}")

        print("Dữ liệu Local vẫn an toàn.")

    finally:
        if "cloud_conn" in locals():
            cloud_conn.close()
try:
    # Tạo thư mục warehouse nếu chưa có
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Kết nối tới file DuckDB Local
    conn = duckdb.connect(DB_PATH)

    # Tạo schema bronze
    conn.execute("CREATE SCHEMA IF NOT EXISTS bronze")

    # Đăng ký Pandas DataFrame thành view ảo cho DuckDB
    conn.register("df_view", df)

    # Đẩy dữ liệu vào bảng vật lý bronze.orders_raw
    conn.execute("""
    CREATE OR REPLACE TABLE bronze.orders_raw AS
    SELECT *
    FROM df_view
    """)
    

    print(f"Hoàn tất quá trình Ingestion! Đã nạp thành công {len(df)} dòng vào bảng 'bronze.orders_raw' (Local DuckDB).")
    sync_to_motherduck(conn)



except Exception as e:
    print(f"Lỗi trong quá trình nạp dữ liệu vào kho: {e}")
    sys.exit(1)
finally:
    if 'conn' in locals():
        conn.close()