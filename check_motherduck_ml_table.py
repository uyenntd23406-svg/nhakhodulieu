import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

TOKEN = (os.getenv("MOTHERDUCK_TOKEN") or "").strip().strip('"').strip("'")
CLOUD_DB = (os.getenv("MOTHERDUCK_DATABASE") or "dataco_warehouse_cloud").strip()

SCHEMA = "gold"
TABLE = "mart_ml_delivery_risk_features"

if not TOKEN:
    raise SystemExit("Thiếu MOTHERDUCK_TOKEN trong file .env")

def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'

print("Đang kết nối MotherDuck...")
print("Cloud database:", CLOUD_DB)

con = duckdb.connect()
con.execute("INSTALL motherduck")
con.execute("LOAD motherduck")
con.execute(f"SET motherduck_token='{TOKEN}'")
con.execute("ATTACH 'md:'")

full_table = f"{qident(CLOUD_DB)}.{qident(SCHEMA)}.{qident(TABLE)}"

print("\n1. Kiểm tra danh sách database:")
print(con.execute("SHOW DATABASES").fetchdf())

print("\n2. Kiểm tra toàn bộ bảng đang thấy được:")
all_tables = con.execute("SHOW ALL TABLES").fetchdf()
print(all_tables)

print("\n3. Lọc các bảng thuộc database cloud và schema gold:")
try:
    gold_tables = all_tables[
        (all_tables["database"] == CLOUD_DB) &
        (all_tables["schema"] == SCHEMA)
    ]
    print(gold_tables)
except Exception:
    print("Không lọc được theo cột database/schema, in toàn bộ bảng ở bước 2 để kiểm tra thủ công.")

print("\n4. Kiểm tra số dòng bảng ML:")
print(con.execute(f"""
    SELECT COUNT(*) AS n_rows
    FROM {full_table}
""").fetchdf())

print("\n5. Kiểm tra phân phối target:")
print(con.execute(f"""
    SELECT
        target_late_delivery_risk,
        COUNT(*) AS n,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
    FROM {full_table}
    GROUP BY target_late_delivery_risk
    ORDER BY target_late_delivery_risk
""").fetchdf())

print("\n6. Xem thử 5 dòng đầu:")
sample = con.execute(f"""
    SELECT *
    FROM {full_table}
    LIMIT 5
""").fetchdf()

print(sample)

print("\n7. Danh sách cột:")
print(list(sample.columns))

con.close()
print("\nKết nối và đọc bảng ML thành công.")