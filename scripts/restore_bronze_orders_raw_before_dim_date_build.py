from pathlib import Path
import duckdb

DB_PATH = Path("warehouse/logistics.duckdb")
EVIDENCE_DIR = Path("reports/evidence_final")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = EVIDENCE_DIR / "38b_restore_bronze_orders_raw_before_dim_date_build.txt"

# Tìm các file dữ liệu khả nghi trong project
candidate_patterns = [
    "**/*DataCo*Supply*Chain*.csv",
    "**/*DataCo*.csv",
    "**/*dataco*.csv",
    "**/*supply*chain*.csv",
    "**/orders_raw*.csv",
    "**/orders*.csv",
    "**/*.parquet"
]

candidates = []
for pattern in candidate_patterns:
    candidates.extend(Path(".").glob(pattern))

# Loại file trong reports/evidence/sample để tránh nạp nhầm sample output
filtered = []
for p in candidates:
    s = str(p).replace("\\", "/").lower()
    if "reports/" in s or "evidence" in s or "sample" in s:
        continue
    if p.is_file():
        filtered.append(p)

# Ưu tiên CSV có DataCo/SupplyChain hoặc file lớn
filtered = sorted(
    set(filtered),
    key=lambda x: (("dataco" not in x.name.lower()), -x.stat().st_size)
)

with open(LOG_PATH, "w", encoding="utf-8") as log:
    log.write("RESTORE BRONZE.ORDERS_RAW BEFORE DBT BUILD\n")
    log.write(f"Database: {DB_PATH.resolve()}\n\n")

    if not DB_PATH.exists():
        raise SystemExit(f"Database not found: {DB_PATH.resolve()}")

    log.write("Candidate source files:\n")
    for p in filtered[:20]:
        log.write(f"- {p} | {p.stat().st_size:,} bytes\n")

    if not filtered:
        raise SystemExit(
            "No candidate raw data file found. Put the original DataCo CSV under data/raw or project root, then rerun."
        )

    source_file = filtered[0]
    log.write(f"\nSelected source file: {source_file}\n")

    con = duckdb.connect(str(DB_PATH), read_only=False)

    con.execute("CREATE SCHEMA IF NOT EXISTS bronze")

    # Nạp CSV hoặc Parquet
    if source_file.suffix.lower() == ".csv":
        # all_varchar=true để giữ nguyên dữ liệu gốc hơn ở Bronze;
        # dbt staging sẽ ép kiểu sau.
        con.execute(f"""
            CREATE OR REPLACE TABLE bronze.orders_raw AS
            SELECT *
            FROM read_csv_auto('{source_file.as_posix()}', all_varchar=false, ignore_errors=true)
        """)
    elif source_file.suffix.lower() == ".parquet":
        con.execute(f"""
            CREATE OR REPLACE TABLE bronze.orders_raw AS
            SELECT *
            FROM read_parquet('{source_file.as_posix()}')
        """)
    else:
        raise SystemExit(f"Unsupported source file: {source_file}")

    row_count = con.execute("SELECT COUNT(*) FROM bronze.orders_raw").fetchone()[0]
    col_count = con.execute("""
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = 'bronze'
          AND table_name = 'orders_raw'
    """).fetchone()[0]

    log.write(f"\nCreated bronze.orders_raw\n")
    log.write(f"Row count: {row_count:,}\n")
    log.write(f"Column count: {col_count:,}\n")

    log.write("\nFirst 30 columns:\n")
    cols = con.execute("""
        SELECT
            column_name,
            data_type,
            ordinal_position
        FROM information_schema.columns
        WHERE table_schema = 'bronze'
          AND table_name = 'orders_raw'
        ORDER BY ordinal_position
        LIMIT 30
    """).fetchdf()
    log.write(cols.to_string(index=False))
    log.write("\n")

    con.close()

print("DONE restore bronze.orders_raw")
print("Log:", LOG_PATH)
