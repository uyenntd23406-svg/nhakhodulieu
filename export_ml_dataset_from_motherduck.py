import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

TOKEN = (os.getenv("MOTHERDUCK_TOKEN") or "").strip().strip('"').strip("'")

if not TOKEN:
    raise SystemExit("Thiếu MOTHERDUCK_TOKEN trong file .env")

con = duckdb.connect()
con.execute("INSTALL motherduck")
con.execute("LOAD motherduck")
con.execute(f"SET motherduck_token='{TOKEN}'")
con.execute("ATTACH 'md:'")

print("Đang tải bảng ML từ MotherDuck...")

df = con.execute("""
    SELECT *
    FROM "dataco_warehouse_cloud"."gold"."mart_ml_delivery_risk_features"
""").fetchdf()

print("Shape:", df.shape)

df.to_csv(
    "mart_ml_delivery_risk_features.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Đã export thành công: mart_ml_delivery_risk_features.csv")

con.close()