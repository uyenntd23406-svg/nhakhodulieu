from pathlib import Path

base = Path("reports/evidence_final")

required_files = [
    "09_dbt_lineage_dag.png",
    "19_bronze_current_reaudit.txt",
    "19a_dbt_debug_after_bronze_change.txt",
    "20_dbt_build_after_bronze_change.txt",
    "20a_dbt_docs_generate_after_rebuild.txt",
    "21_verify_layer_integrity.txt",
    "22_verify_data_reconciliation.txt",
    "23_export_lead_samples.txt",
    "24a_motherduck_attach_test.txt",
    "24_cloud_push_dry_run.txt",
    "25_cloud_push_result.txt",
    "25a_verify_motherduck_cloud.txt",
    "27_evidence_final_tree.txt",
]

print("=== FINAL LEAD VERIFICATION CHECK ===")
print("Evidence folder:", base.resolve())
print()

for f in required_files:
    p = base / f
    status = "PASS" if p.exists() and p.stat().st_size > 0 else "MISSING"
    size = p.stat().st_size if p.exists() else 0
    print(f"{status:8} | {f:45} | {size:,} bytes")

print("\n=== SCRIPT CHECK ===")
script_files = [
    "verify_bronze_current.py",
    "verify_layer_integrity.py",
    "verify_data_reconciliation.py",
    "export_lead_samples.py",
    "push_to_motherduck.py",
    "verify_motherduck_cloud.py",
    "final_lead_verification_check.py",
]

for f in script_files:
    p = Path("scripts") / f
    status = "PASS" if p.exists() and p.stat().st_size > 0 else "MISSING"
    size = p.stat().st_size if p.exists() else 0
    print(f"{status:8} | {f:45} | {size:,} bytes")

print("\n=== SAMPLE EXPORT CHECK ===")
sample_dir = base / "samples"

expected_samples = [
    "01_bronze_orders_raw_sample.csv",
    "02_silver_stg_orders_sample.csv",
    "03_silver_stg_customers_sample.csv",
    "04_silver_stg_products_sample.csv",
    "05_silver_int_delivery_metrics_sample.csv",
    "06_gold_fct_order_items_sample.csv",
    "07_gold_dim_customer_sample.csv",
    "08_gold_dim_product_sample.csv",
    "09_gold_dim_location_sample.csv",
    "10_gold_dim_shipping_sample.csv",
    "11_gold_dim_date_sample.csv",
    "12_mart_supply_chain_kpi.csv",
    "13_mart_delivery_performance_sample.csv",
    "14_mart_sales_profitability_sample.csv",
    "15_mart_ml_delivery_risk_features_sample.csv",
    "16_mart_executive_summary_sample.csv",
]

for f in expected_samples:
    p = sample_dir / f
    status = "PASS" if p.exists() and p.stat().st_size > 0 else "MISSING"
    size = p.stat().st_size if p.exists() else 0
    print(f"{status:8} | {f:50} | {size:,} bytes")
