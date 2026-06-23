# Data Warehouse & dbt Transformation - DataCo Supply Chain

## 1. Mục tiêu

Thư mục này triển khai Data Warehouse layer cho bài toán phân tích hiệu suất vận hành logistics dựa trên DataCo Supply Chain Dataset. Pipeline tiếp nối từ Bronze Layer đã được tạo bởi ELT pipeline, sau đó sử dụng dbt Core + DuckDB để xây dựng Silver models, Gold Star Schema và Analytics Marts phục vụ Dashboard, Machine Learning và GenAI reporting.

## 2. Kiến trúc dữ liệu

Luồng dữ liệu chính:

Bronze Layer:
- bronze.orders_raw

Silver Layer:
- silver.stg_orders
- silver.stg_customers
- silver.stg_products
- silver.int_order_enriched
- silver.int_delivery_metrics

Gold Layer - Star Schema:
- gold.dim_date
- gold.dim_customer
- gold.dim_product
- gold.dim_location
- gold.dim_shipping
- gold.fct_order_items

Gold Layer - Analytics Marts:
- gold.mart_supply_chain_kpi
- gold.mart_delivery_performance
- gold.mart_sales_profitability
- gold.mart_ml_delivery_risk_features
- gold.mart_executive_summary

## 3. Kết quả thực nghiệm

Kết quả sau khi chạy dbt:

- dbt build: PASS=64, ERROR=0
- dbt test: PASS=48, ERROR=0
- Bronze rows: 180,519
- Fact rows: 180,519
- Date dimension rows: 1,133
- ML feature mart rows: 180,519
- Executive summary mart rows: 61

## 4. Evidence

Evidence chính nằm trong:

- reports/evidence/
- reports/evidence_final/

Các file quan trọng:

- 07_dbt_build_full_final.txt
- 09_dbt_lineage_dag.png
- 10_verify_date_fix.txt
- 11_verify_gold_marts_final.txt
- 12_final_evidence_check_v2.txt

## 5. Lệnh chạy lại

Cài dependencies:

python -m pip install -r requirements.txt
python -m pip install dbt-core dbt-duckdb duckdb pandas pyarrow

Chạy dbt:

cd dbt_dataco
dbt debug --profiles-dir .
dbt build --profiles-dir .
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir . --port 8088

Verify:

cd ..
python scripts/verify_date_fix.py
python scripts/verify_gold_marts.py
