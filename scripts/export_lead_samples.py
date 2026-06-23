import duckdb
from pathlib import Path

con = duckdb.connect("warehouse/logistics.duckdb")
out_dir = Path("reports/evidence_final/samples")
out_dir.mkdir(parents=True, exist_ok=True)

exports = {
    "01_bronze_orders_raw_sample.csv": "SELECT * FROM bronze.orders_raw LIMIT 100",

    "02_silver_stg_orders_sample.csv": "SELECT * FROM silver.stg_orders LIMIT 100",
    "03_silver_stg_customers_sample.csv": "SELECT * FROM silver.stg_customers LIMIT 100",
    "04_silver_stg_products_sample.csv": "SELECT * FROM silver.stg_products LIMIT 100",
    "05_silver_int_delivery_metrics_sample.csv": "SELECT * FROM silver.int_delivery_metrics LIMIT 100",

    "06_gold_fct_order_items_sample.csv": "SELECT * FROM gold.fct_order_items LIMIT 100",
    "07_gold_dim_customer_sample.csv": "SELECT * FROM gold.dim_customer LIMIT 100",
    "08_gold_dim_product_sample.csv": "SELECT * FROM gold.dim_product LIMIT 100",
    "09_gold_dim_location_sample.csv": "SELECT * FROM gold.dim_location LIMIT 100",
    "10_gold_dim_shipping_sample.csv": "SELECT * FROM gold.dim_shipping LIMIT 100",
    "11_gold_dim_date_sample.csv": "SELECT * FROM gold.dim_date LIMIT 100",

    "12_mart_supply_chain_kpi.csv": "SELECT * FROM gold.mart_supply_chain_kpi",
    "13_mart_delivery_performance_sample.csv": "SELECT * FROM gold.mart_delivery_performance LIMIT 100",
    "14_mart_sales_profitability_sample.csv": "SELECT * FROM gold.mart_sales_profitability LIMIT 100",
    "15_mart_ml_delivery_risk_features_sample.csv": "SELECT * FROM gold.mart_ml_delivery_risk_features LIMIT 100",
    "16_mart_executive_summary_sample.csv": "SELECT * FROM gold.mart_executive_summary LIMIT 100",
}

for file_name, sql in exports.items():
    path = out_dir / file_name
    df = con.execute(sql).fetchdf()
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"EXPORTED | {file_name} | rows={len(df)} | path={path}")
