from pathlib import Path
import re
import duckdb

DB_PATH = Path("../warehouse/logistics.duckdb")
EVIDENCE_DIR = Path("../reports/evidence_final")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = EVIDENCE_DIR / "38c_normalize_bronze_column_names.txt"

def normalize_col(name: str) -> str:
    s = name.strip()
    s = s.lower()
    s = s.replace(" ", "_")
    s = s.replace("-", "_")
    s = s.replace("/", "_")
    s = s.replace(".", "_")
    s = re.sub(r"__+", "_", s)
    return s

if not DB_PATH.exists():
    raise SystemExit(f"Database not found: {DB_PATH.resolve()}")

con = duckdb.connect(str(DB_PATH), read_only=False)

exists = con.execute("""
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_schema = 'bronze'
      AND table_name = 'orders_raw'
""").fetchone()[0]

if exists == 0:
    raise SystemExit("bronze.orders_raw does not exist. Restore Bronze first.")

cols_df = con.execute("""
    SELECT column_name, data_type, ordinal_position
    FROM information_schema.columns
    WHERE table_schema = 'bronze'
      AND table_name = 'orders_raw'
    ORDER BY ordinal_position
""").fetchdf()

original_cols = cols_df["column_name"].tolist()

seen = {}
pairs = []

for col in original_cols:
    new_col = normalize_col(col)

    if new_col in seen:
        seen[new_col] += 1
        new_col = f"{new_col}_{seen[new_col]}"
    else:
        seen[new_col] = 1

    pairs.append((col, new_col))

select_list = ",\n    ".join([f'"{old}" AS "{new}"' for old, new in pairs])

con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
con.execute("DROP TABLE IF EXISTS bronze.orders_raw_normalized")

con.execute(f"""
    CREATE TABLE bronze.orders_raw_normalized AS
    SELECT
        {select_list}
    FROM bronze.orders_raw
""")

old_count = con.execute("SELECT COUNT(*) FROM bronze.orders_raw").fetchone()[0]
new_count = con.execute("SELECT COUNT(*) FROM bronze.orders_raw_normalized").fetchone()[0]

con.execute("DROP TABLE bronze.orders_raw")
con.execute("ALTER TABLE bronze.orders_raw_normalized RENAME TO orders_raw")

final_cols_df = con.execute("""
    SELECT column_name, data_type, ordinal_position
    FROM information_schema.columns
    WHERE table_schema = 'bronze'
      AND table_name = 'orders_raw'
    ORDER BY ordinal_position
""").fetchdf()

required_cols = [
    "customer_id",
    "product_card_id",
    "product_category_id",
    "product_name",
    "order_id",
    "order_item_id",
    "order_item_cardprod_id",
    "order_date_(dateorders)",
    "shipping_date_(dateorders)",
    "market",
    "shipping_mode",
    "delivery_status",
    "late_delivery_risk"
]

final_cols = set(final_cols_df["column_name"].tolist())
missing = [c for c in required_cols if c not in final_cols]

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("NORMALIZE BRONZE COLUMN NAMES\n")
    f.write(f"Database: {DB_PATH.resolve()}\n\n")
    f.write(f"Old row count: {old_count:,}\n")
    f.write(f"New row count: {new_count:,}\n\n")

    f.write("Column mapping:\n")
    for old, new in pairs:
        f.write(f"- {old} -> {new}\n")

    f.write("\nRequired columns check:\n")
    if missing:
        f.write("MISSING:\n")
        for c in missing:
            f.write(f"- {c}\n")
    else:
        f.write("PASS: all required columns exist.\n")

    f.write("\nFinal first 50 columns:\n")
    f.write(final_cols_df.head(50).to_string(index=False))
    f.write("\n")

con.close()

print("DONE normalize bronze.orders_raw")
print("Old row count:", old_count)
print("New row count:", new_count)
print("Missing required columns:", missing)
print("Log:", LOG_PATH)
