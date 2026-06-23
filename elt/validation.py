import os
import json
from datetime import datetime
import great_expectations as gx
from great_expectations.datasource.fluent import PandasDatasource

def validate_data(df):
    """
    Hàm kiểm định chất lượng dữ liệu.
    Nhận đầu vào là Pandas DataFrame đã được chuẩn hóa tên cột.
    Trả về Tuple: (is_valid: bool, report_path: str)
    """
    context = gx.get_context()
    datasource = context.add_or_update_datasource(datasource=PandasDatasource(name="logistics_ds"))
    batch = datasource.read_dataframe(df, asset_name="raw_orders")
    validator = context.get_validator(batch=batch)

    # 1. Schema & Not Null Check
    critical_cols = [
        "order_id", "order_item_id", "market", "shipping_mode",
        "delivery_status", "customer_segment", "sales_per_customer", "late_delivery_risk"
    ]
    for col in critical_cols:
        validator.expect_column_to_exist(col)
        validator.expect_column_values_to_not_be_null(col)

    # 2. Uniqueness Check
    validator.expect_column_values_to_be_unique("order_item_id")

    # 3. Value Set Check
    validator.expect_column_values_to_be_in_set("market", ["Africa", "Europe", "LATAM", "Pacific Asia", "USCA"])
    validator.expect_column_values_to_be_in_set("delivery_status", ["Advance shipping", "Late delivery", "Shipping canceled", "Shipping on time"])
    validator.expect_column_values_to_be_in_set("shipping_mode", ["First Class", "Second Class", "Same Day", "Standard Class"])
    validator.expect_column_values_to_be_in_set("customer_segment", ["Consumer", "Corporate", "Home Office"])

    # 4. Business Rules & Range Check
    validator.expect_column_values_to_be_in_set("late_delivery_risk", [0, 1])
    validator.expect_column_values_to_be_between("days_for_shipping_(real)", min_value=0, max_value=10)
    validator.expect_column_values_to_be_between("days_for_shipment_(scheduled)", min_value=0, max_value=5)
    validator.expect_column_values_to_be_between("sales_per_customer", min_value=0, strict_min=True)
    
    # 5. Row Count Check
    validator.expect_table_row_count_to_be_between(min_value=170000, max_value=200000)

    # Thực thi kiểm tra
    results = validator.validate()
    is_valid = results.success

    # Xuất báo cáo JSON
    os.makedirs("logs", exist_ok=True)
    report_path = f"logs/validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "status": "PASS" if is_valid else "FAIL",
        "total_rules": len(results.results),
        "passed_rules": sum(1 for r in results.results if r.success),
        "details": [
            {
                "rule": getattr(r.expectation_config, "type", getattr(r.expectation_config, "expectation_type", "unknown_rule")), 
                "column": r.expectation_config.kwargs.get("column", "table_level") if hasattr(r.expectation_config, "kwargs") else "table_level", 
                "success": r.success
            } for r in results.results
        ]
    }
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)
        
    return is_valid, report_path