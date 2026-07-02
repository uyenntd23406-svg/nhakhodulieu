# dashboard.py
# DataCo Supply Chain Intelligence Dashboard
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import requests
import math
from dotenv import load_dotenv
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 1. PAGE CONFIG
# ─────────────────────────────────────────────────────────────
load_dotenv()
TOKEN    = os.getenv("MOTHERDUCK_TOKEN")
DATABASE = os.getenv("MOTHERDUCK_DATABASE", "dataco_warehouse_cloud")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

st.set_page_config(
    page_title="DataCo Logistics Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# 2. CSS – Tối ưu thông thoáng, rõ ràng
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #0d1a35 100%);
    border-right: 1px solid #1a2840;
}
[data-testid="stSidebar"] * { color: #c8d6e8 !important; }
[data-testid="stSidebar"] label { color: #5a7899 !important; font-size:0.75rem; text-transform:uppercase; letter-spacing:.08em; }
[data-testid="stSidebar"] .stMarkdown h3 { color:#4ab3f0 !important; font-size:0.85rem; letter-spacing:.09em; text-transform:uppercase; margin-bottom:4px; }
[data-testid="stSidebar"] hr { border-color:#1a2840; }

.stApp { background:#f0f4f9; }

/* ── Page header ── */
.page-header {
    background: linear-gradient(135deg, #060d1f 0%, #0d2045 50%, #0a3562 100%);
    border-radius: 18px;
    padding: 36px 48px;
    margin-bottom: 32px;
    border: 1px solid #1a3860;
    position: relative; overflow: hidden;
}
.page-header::before {
    content:""; position:absolute; left:-20%; top:-50%; width:60%; height:200%;
    background: radial-gradient(ellipse, rgba(74,179,240,.06) 0%, transparent 65%);
}
.page-header::after {
    content:""; position:absolute; right:0; top:0; bottom:0; width:50%;
    background: radial-gradient(ellipse at right center, rgba(30,120,220,.12) 0%, transparent 70%);
}
.page-header h1 { color:#f0f8ff; font-size:2.15rem; font-weight:800; margin:0 0 8px; letter-spacing:-.02em; position:relative;z-index:1; }
.page-header p  { color:#7aabcc; font-size:0.97rem; margin:0; position:relative;z-index:1; }
.ph-eyebrow { font-size:0.7rem; color:#3d7aad; text-transform:uppercase; letter-spacing:.12em; font-weight:700; margin-bottom:7px; position:relative;z-index:1; }
.ph-badges { margin-top:14px; display:flex; gap:10px; flex-wrap:wrap; position:relative;z-index:1; }
.ph-badge { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.1); border-radius:999px; padding:4px 14px; font-size:0.72rem; color:#8ac8e8; }
.ph-badge.ml { background:rgba(124,58,237,.15); border-color:rgba(124,58,237,.3); color:#a78bfa; }

/* ── Section headers ── */
.sec-eyebrow { font-size:0.7rem; color:#8499b0; text-transform:uppercase; letter-spacing:.12em; font-weight:700; margin-bottom:2px; }
.sec-title   { font-size:1.1rem; font-weight:700; color:#0b1425; margin-bottom:20px; }

/* ── KPI cards ── */
.kpi-card { background:#fff; border-radius:14px; padding:18px 18px 16px; border:1px solid #dde6f0; position:relative; overflow:hidden; box-shadow:0 2px 8px rgba(15,23,42,.05); min-height:132px; display:flex; flex-direction:column; justify-content:space-between; margin-bottom:12px; }
.kpi-card::before { content:""; position:absolute; top:0; left:0; right:0; height:4px; }
.kc-blue::before   { background:linear-gradient(90deg,#1a6fdc,#38b2f6); }
.kc-purple::before { background:linear-gradient(90deg,#7c3aed,#a78bfa); }
.kc-green::before  { background:linear-gradient(90deg,#059669,#34d399); }
.kc-amber::before  { background:linear-gradient(90deg,#d97706,#fbbf24); }
.kc-red::before    { background:linear-gradient(90deg,#dc2626,#f87171); }
.kc-violet::before { background:linear-gradient(90deg,#6d28d9,#8b5cf6); }
.kpi-eyebrow { font-size:0.7rem; color:#8a9fb0; text-transform:uppercase; letter-spacing:.08em; font-weight:600; margin-bottom:6px; }
.kpi-value   { font-size:1.9rem; font-weight:800; color:#0b1425; line-height:1.2; margin-bottom:6px; }
.kpi-sub     { font-size:0.75rem; color:#9aabbc; }
.kpi-carousel-controls { display:flex; align-items:center; justify-content:center; gap:16px; margin-top:14px; }
.kpi-carousel-btn { background:#fff; border:1px solid #d6d9e6; border-radius:12px; min-width:38px; min-height:38px; padding:0 0.75rem; font-size:1.1rem; color:#1f2937; cursor:pointer; box-shadow:0 2px 6px rgba(15,23,42,.08); transition: all .18s ease; }
.kpi-carousel-btn:hover { background:#f8fafc; transform: translateY(-1px); }
.kpi-carousel-dots { display:flex; gap:8px; }
.kpi-carousel-dot { width:10px; height:10px; border-radius:50%; background:#cbd5e1; border:1px solid transparent; }
.kpi-carousel-dot.active { background:#1e40af; border-color:#1e40af; }
.kpi-carousel-btn:focus { outline:none; box-shadow:0 0 0 3px rgba(59,130,246,.18); }

.badge       { display:inline-block; padding:2px 10px; border-radius:999px; font-size:0.7rem; font-weight:700; }
.bg-green  { background:#dcfce7; color:#15803d; }
.bg-amber  { background:#fef3c7; color:#b45309; }
.bg-red    { background:#fee2e2; color:#b91c1c; }
.bg-purple { background:#f5f3ff; color:#6d28d9; }
.bg-blue   { background:#eff6ff; color:#1d4ed8; }

/* ── ML Risk badges ── */
.risk-very-high { background:#fee2e2; color:#b91c1c; border:1px solid #fca5a5; }
.risk-high      { background:#fff3cd; color:#92400e; border:1px solid #fcd34d; }
.risk-medium    { background:#fef3c7; color:#b45309; border:1px solid #fde68a; }
.risk-watch     { background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; }
.risk-low       { background:#f0fdf4; color:#15803d; border:1px solid #86efac; }

/* ── Chart wrapper ── */
.chart-wrap {
    background:#fff;
    border-radius:14px;
    border:1px solid #dde6f0;
    padding:12px 10px 6px;
    box-shadow:0 2px 6px rgba(0,0,0,.04);
    margin-bottom:8px;
}

/* ── ML Metric cards ── */
.ml-metric { background:#fff; border-radius:12px; border:1px solid #dde6f0; padding:18px 20px; text-align:center; }
.ml-metric-val { font-size:2.0rem; font-weight:800; line-height:1.2; margin-bottom:4px; }
.ml-metric-label { font-size:0.75rem; color:#6a85a0; text-transform:uppercase; letter-spacing:.07em; font-weight:600; }
.ml-metric-desc { font-size:0.7rem; color:#8a9fb0; margin-top:4px; }

/* ── SHAP bar ── */
.shap-row { display:flex; align-items:center; gap:12px; margin-bottom:8px; padding:10px 14px; background:#fafbfc; border-radius:8px; border:1px solid #eef2f8; }
.shap-feat { font-size:0.8rem; font-weight:600; color:#0b1425; min-width:200px; flex:1; }
.shap-bar-wrap { flex:2; height:14px; background:#eef2f8; border-radius:6px; overflow:hidden; }
.shap-bar-pos { height:100%; background:linear-gradient(90deg,#dc2626,#f87171); border-radius:6px; }
.shap-bar-neg { height:100%; background:linear-gradient(90deg,#059669,#34d399); border-radius:6px; }
.shap-val { font-size:0.8rem; font-weight:700; min-width:60px; text-align:right; }

/* ── Insight cards ── */
.insight-card { background:#fff; border:1px solid #dde6f0; border-radius:12px; padding:16px 18px; margin-bottom:12px; box-shadow:0 2px 4px rgba(0,0,0,.04); }
.i-title  { font-size:0.85rem; font-weight:700; color:#0b1425; margin-bottom:4px; }
.i-body   { font-size:0.78rem; color:#4a6077; line-height:1.6; }
.i-rec    { margin-top:8px; padding:8px 12px; background:#f4f7fb; border-radius:6px; font-size:0.75rem; color:#3a5068; border-left:3px solid #1e6fdc; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap:6px; background:#e8eef6; border-radius:12px; padding:4px; }
.stTabs [data-baseweb="tab"] { border-radius:10px; font-size:0.85rem; font-weight:600; color:#556b82; padding:8px 16px; }
.stTabs [aria-selected="true"] { background:#fff !important; color:#0b1425 !important; box-shadow:0 2px 6px rgba(0,0,0,.08); }

/* ── Dividers & Footer ── */
.dash-hr { border:none; border-top:1px solid #dde6f0; margin:28px 0; }
.dash-footer { text-align:center; font-size:0.7rem; color:#9ab0c4; padding:22px 0 8px; }

/* ── Dataframe (tables) ── */
[data-testid="stDataFrame"] { border-radius:10px; border:1px solid #dde6f0; overflow:hidden; }

/* ── Điều chỉnh spacing chung ── */
.block-container { padding-top:2rem; padding-bottom:2rem; }

/* Risk level card */
.risk-card { border-radius:12px; padding:16px 12px; text-align:center; }
.risk-card .risk-label { font-size:0.85rem; font-weight:700; margin:4px 0; }
.risk-card .risk-range { font-size:0.75rem; font-weight:600; color:#0b1425; margin-bottom:8px; }
.risk-card .risk-desc { font-size:0.7rem; color:#4a6077; text-align:left; line-height:1.6; }

/* Chatbot */
.chat-scroll-area { max-height: 560px; overflow-y: auto; padding: 20px 8px; }
.msg-bubble { padding: 13px 18px; border-radius: 18px; line-height: 1.75; max-width: 85%; }
.msg-bubble.user { background: linear-gradient(135deg, #1a6fdc, #7c3aed); color: #fff; align-self: flex-end; }
.msg-bubble.bot { background: #fff; border: 1px solid #e2e8f0; color: #0f172a; align-self: flex-start; }
.chat-container { display: flex; flex-direction: column; gap: 12px; }
.chat-row { display: flex; }
.chat-row.user { justify-content: flex-end; }
.chat-row.bot { justify-content: flex-start; }

/* API Status */
.api-status { font-size: 0.76rem; display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; font-weight: 600; }
.api-status.ok { background: #dcfce7; color: #15803d; }
.api-status.err { background: #fee2e2; color: #b91c1c; }
.status-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.api-status.ok .status-dot { background: #16a34a; animation: pulse 2s infinite; }
.api-status.err .status-dot { background: #dc2626; }

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(22, 163, 74, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
}

.retry-banner { background: #fffbeb; border: 1px solid #fef08a; color: #854d0e; padding: 10px 14px; border-radius: 8px; font-size: 0.8rem; margin-bottom: 14px; }
.export-btn { background: #fff; border: 1px solid #dde6f0; color: #4a5568; padding: 6px 12px; border-radius: 8px; font-size: 0.76rem; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.export-btn:hover { background: #f7fafc; border-color: #cbd5e0; }

.fb-row { display: flex; gap: 6px; margin-top: 6px; margin-left: 44px; }
.fb-btn { background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 2px 8px; font-size: 0.7rem; color: #64748b; cursor: pointer; }
.fb-btn:hover { background: #f1f5f9; color: #0f172a; }
.fb-btn.active-up { background: #dcfce7; border-color: #86efac; color: #15803d; }
.fb-btn.active-down { background: #fee2e2; border-color: #fca5a5; color: #b91c1c; }

.followup-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; margin-left: 44px; }
.followup-chip { background: #f0f7ff; border: 1px solid #bfdbfe; border-radius: 999px; padding: 5px 14px; font-size: 0.74rem; color: #1d4ed8; cursor: pointer; transition: all .15s; }
.followup-chip:hover { background: #dbeafe; border-color: #93c5fd; }

.typing-indicator { display: flex; align-items: center; gap: 10px; padding: 10px 0; margin-bottom: 12px; }
.typing-dots { display: flex; gap: 5px; }
.typing-dot { width: 8px; height: 8px; border-radius: 50%; background: #7c3aed; opacity: .4; animation: typingPulse 1.4s infinite ease-in-out; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingPulse {
    0%, 100% { transform: translateY(0); opacity: .4; }
    50% { transform: translateY(-4px); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 3. TOKEN CHECK
# ─────────────────────────────────────────────────────────────
if not TOKEN:
    st.error(" **MOTHERDUCK_TOKEN** chưa cấu hình. Tạo file `.env` và thêm token.")
    st.stop()

# ─────────────────────────────────────────────────────────────
# 4. DATA LOADING  (CHỈ ĐỌC TỪ TẦNG GOLD / MART — không đụng silver/bronze)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner="Đang tải dữ liệu từ Gold Layer (MotherDuck)…")
def load_all_data():
    try:
        con = duckdb.connect()
        con.execute("INSTALL motherduck")
        con.execute("LOAD motherduck")
        con.execute(f"SET motherduck_token='{TOKEN}'")
        con.execute("ATTACH 'md:'")
        DB = DATABASE

        df_kpi = con.execute(f'SELECT * FROM "{DB}"."gold"."mart_supply_chain_kpi"').fetchdf()

        df_dp = con.execute(f"""
            SELECT order_year_month, market, shipping_mode, delivery_status,
                   order_count, order_item_count, late_delivery_rate,
                   avg_real_shipping_days, avg_scheduled_shipping_days,
                   avg_shipping_variance, total_sales, total_profit,
                   late_item_count, on_time_item_count, advance_shipping_item_count, canceled_item_count
            FROM "{DB}"."gold"."mart_delivery_performance"
            ORDER BY order_year_month
        """).fetchdf()
        df_dp["order_date"] = pd.to_datetime(df_dp["order_year_month"] + "-01")

        df_sp = con.execute(f"""
            SELECT order_year_month, market, customer_segment,
                   department_name, category_name, product_name,
                   order_count, order_item_count, total_quantity,
                   total_sales, total_profit, total_cost,
                   profit_margin, avg_discount_rate, avg_profit_ratio, avg_sales_per_item
            FROM "{DB}"."gold"."mart_sales_profitability"
            ORDER BY order_year_month
        """).fetchdf()
        df_sp["order_date"] = pd.to_datetime(df_sp["order_year_month"] + "-01")

        df_ex = con.execute(f"""
            SELECT order_year_month, market,
                   total_orders, total_order_items, total_customers,
                   total_sales, total_profit, total_cost,
                   late_delivery_rate, avg_shipping_days, avg_shipping_variance,
                   delivery_risk_level, business_health_flag
            FROM "{DB}"."gold"."mart_executive_summary"
            ORDER BY order_year_month
        """).fetchdf()
        df_ex["order_date"] = pd.to_datetime(df_ex["order_year_month"] + "-01")

        df_ml = con.execute(f"""
            SELECT order_id, order_item_id, market, order_region, order_country, customer_segment,
                   department_name, category_name, shipping_mode, order_status,
                   quantity, sales_amount, discount_rate, product_unit_price,
                   profit_ratio, days_for_shipment_scheduled,
                   order_month, order_day, order_day_of_week,
                   target_late_delivery_risk
            FROM "{DB}"."gold"."mart_ml_delivery_risk_features"
        """).fetchdf()

        con.close()
        return df_kpi, df_dp, df_sp, df_ex, df_ml
    except Exception as e:
        st.error(f" Lỗi kết nối MotherDuck: {e}")
        st.stop()

df_kpi, df_dp, df_sp, df_ex, df_ml = load_all_data()

# ─────────────────────────────────────────────────────────────
# 5. SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### DataCo Global")
    st.markdown("<small style='color:#3a6080'>Logistics Intelligence · v4.5</small>", unsafe_allow_html=True)
    st.markdown("<small style='color:#2a4860'>Gold Layer · Kimball · ML Ready</small>", unsafe_allow_html=True)
    st.markdown("---")

    ml_count = len(df_ml)
    markets = ["Tất cả"] + sorted(df_dp["market"].dropna().unique().tolist())
    sel_market = st.selectbox("Thị trường", markets)

    min_d = df_dp["order_date"].min().date()
    max_d = df_dp["order_date"].max().date()
    date_range = st.date_input("Khoảng thời gian", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    modes = ["Tất cả"] + sorted(df_dp["shipping_mode"].dropna().unique().tolist())
    sel_mode = st.selectbox("Phương thức vận chuyển", modes)

    segs = ["Tất cả"] + sorted(df_sp["customer_segment"].dropna().unique().tolist())
    sel_seg = st.selectbox("Phân khúc khách hàng", segs)

    if not (isinstance(date_range, tuple) and len(date_range) == 2):
        st.caption("⚠️ Hãy chọn đủ **2 mốc** (từ ngày → đến ngày) để áp dụng lọc thời gian.")

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:0.72rem; color:#3a5878; line-height:1.9'>
    <b style='color:#4a7898'>Nguồn dữ liệu</b><br>
    MotherDuck Cloud · DuckDB<br>
    dbt Core PASS=64<br>
    {len(df_dp):,} bản ghi mart delivery<br>
    5 thị trường · 5 marts<br>
    <span style='color:#6d28d9'>ML mart rows: {ml_count:,}</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 6. FILTER HELPER
# ─────────────────────────────────────────────────────────────
def filt(df, date_col="order_date", market_col="market", mode_col=None, seg_col=None):
    d = df.copy()
    if isinstance(date_range, tuple) and len(date_range) == 2:
        s, e = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        d = d[(d[date_col] >= s) & (d[date_col] <= e)]
    if sel_market != "Tất cả" and market_col in d.columns:
        d = d[d[market_col] == sel_market]
    if sel_mode != "Tất cả" and mode_col and mode_col in d.columns:
        d = d[d[mode_col] == sel_mode]
    if sel_seg != "Tất cả" and seg_col and seg_col in d.columns:
        d = d[d[seg_col] == sel_seg]
    return d

dp = filt(df_dp, mode_col="shipping_mode")
sp = filt(df_sp, seg_col="customer_segment")
ex = filt(df_ex)
ml = df_ml.copy()
if sel_market != "Tất cả":
    ml = ml[ml["market"] == sel_market]
if sel_mode != "Tất cả":
    ml = ml[ml["shipping_mode"] == sel_mode]
if sel_seg != "Tất cả":
    ml = ml[ml["customer_segment"] == sel_seg]

if "order_id" in ml.columns and not ml.empty:
    ml = (
        ml.groupby("order_id", dropna=False, as_index=False)
          .agg(
              order_item_id=("order_item_id", "first"),
              market=("market", "first"),
              order_region=("order_region", "first"),
              order_country=("order_country", "first"),
              customer_segment=("customer_segment", "first"),
              department_name=("department_name", "first"),
              category_name=("category_name", "first"),
              shipping_mode=("shipping_mode", "first"),
              order_status=("order_status", "first"),
              quantity=("quantity", "sum"),
              sales_amount=("sales_amount", "sum"),
              discount_rate=("discount_rate", "mean"),
              product_unit_price=("product_unit_price", "first"),
              profit_ratio=("profit_ratio", "mean"),
              days_for_shipment_scheduled=("days_for_shipment_scheduled", "mean"),
              order_month=("order_month", "first"),
              order_day=("order_day", "first"),
              order_day_of_week=("order_day_of_week", "first"),
              target_late_delivery_risk=("target_late_delivery_risk", "max"),
          )
    )
else:
    ml = ml.copy()

# ─────────────────────────────────────────────────────────────
# 7. KPI COMPUTATION
# ─────────────────────────────────────────────────────────────
if "target_late_delivery_risk" in ml.columns:
    ml["target_late_delivery_risk"] = ml["target_late_delivery_risk"].astype(float).fillna(0.0)

def safe_sum(df, col, default=0):
    return df[col].sum() if not df.empty and col in df.columns else default

total_sales   = safe_sum(ex, "total_sales")
total_orders  = safe_sum(ex, "total_orders")
total_cust    = ex["total_customers"].sum() if not ex.empty else 0
total_profit  = safe_sum(ex, "total_profit")
total_cost    = safe_sum(ex, "total_cost")
profit_margin = total_profit / total_sales if total_sales > 0 else 0
avg_late      = ex["late_delivery_rate"].mean() if not ex.empty else 0
avg_ship_days = ex["avg_shipping_days"].mean() if not ex.empty else 0
avg_ship_var  = ex["avg_shipping_variance"].mean() if not ex.empty else 0

ml_total      = len(ml)
ml_risk_count = ml["target_late_delivery_risk"].sum() if not ml.empty else 0
ml_risk_rate  = ml["target_late_delivery_risk"].mean() if not ml.empty else 0
ml_model_score = None

risk_feature_rows = []
if not ml.empty:
    overall_risk = ml_risk_rate
    for feature in ["customer_segment", "shipping_mode", "department_name", "category_name", "order_month", "order_day_of_week"]:
        if feature in ml.columns:
            summary = ml.groupby(feature, as_index=False)["target_late_delivery_risk"].mean()
            if not summary.empty:
                risk_gap = float(summary["target_late_delivery_risk"].max() - overall_risk)
                risk_feature_rows.append({
                    "feature": feature,
                    "risk_gap": risk_gap,
                    "risk_rate": float(summary["target_late_delivery_risk"].mean()),
                })

risk_feature_df = pd.DataFrame(risk_feature_rows).sort_values("risk_gap", ascending=False).head(8) if risk_feature_rows else pd.DataFrame(columns=["feature", "risk_gap", "risk_rate"])

shipping_summary = (
    dp.groupby("shipping_mode", as_index=False)["late_delivery_rate"].mean().sort_values("late_delivery_rate", ascending=False)
    if not dp.empty else pd.DataFrame(columns=["shipping_mode", "late_delivery_rate"])
)
top_shipping_mode = shipping_summary["shipping_mode"].iloc[0] if not shipping_summary.empty else "N/A"
top_shipping_rate = float(shipping_summary["late_delivery_rate"].iloc[0]) if not shipping_summary.empty else 0.0

if not sp.empty and "customer_segment" in sp.columns:
    seg_summary = (
        sp.groupby("customer_segment", as_index=False).apply(
            lambda x: pd.Series({
                "profit_margin": x["total_profit"].sum() / x["total_sales"].sum() if x["total_sales"].sum() > 0 else 0,
                "avg_discount": x["avg_discount_rate"].mean(),
                "total_sales": x["total_sales"].sum(),
            })
        ).reset_index(drop=True)
    )
else:
    seg_summary = pd.DataFrame(columns=["customer_segment", "profit_margin", "avg_discount", "total_sales"])

if not seg_summary.empty and "customer_segment" in seg_summary.columns:
    top_margin_segment = seg_summary.sort_values("profit_margin", ascending=False).iloc[0]["customer_segment"]
    top_discount_segment = seg_summary.sort_values("avg_discount", ascending=False).iloc[0]["customer_segment"]
else:
    top_margin_segment = "N/A"
    top_discount_segment = "N/A"

market_summary = (
    ex.groupby("market", as_index=False).agg(total_sales=("total_sales","sum"), late_rate=("late_delivery_rate","mean"))
    if not ex.empty else pd.DataFrame(columns=["market", "total_sales", "late_rate"])
)
if not market_summary.empty:
    top_revenue_market = market_summary.sort_values("total_sales", ascending=False).iloc[0]["market"]
    lowest_late_market = market_summary.sort_values("late_rate", ascending=True).iloc[0]["market"]
else:
    top_revenue_market = "N/A"
    lowest_late_market = "N/A"

def fmt_M(v):
    if v >= 1e6: return f"${v/1e6:.2f}M"
    if v >= 1e3: return f"${v/1e3:.1f}K"
    return f"${v:,.0f}"
def pct(v): return f"{v:.1%}"

late_cls = "bg-red" if avg_late > 0.55 else ("bg-amber" if avg_late > 0.40 else "bg-green")
late_lbl = "Cao" if avg_late > 0.55 else ("TB" if avg_late > 0.40 else "Tốt")
var_cls  = "bg-amber" if avg_ship_var > 0 else "bg-green"
var_lbl  = f"+{avg_ship_var:.1f}d" if avg_ship_var > 0 else f"{avg_ship_var:.1f}d"

overview_row = df_kpi.iloc[0] if not df_kpi.empty else None

def get_overview_value(col, default=0.0):
    # Return the raw value from the mart row when present; do not compute or
    # fall back to other data sources. If the mart does not provide the
    # column, return None so the UI can indicate missing data explicitly.
    if overview_row is None or col not in overview_row.index:
        return None
    return overview_row[col] if pd.notna(overview_row[col]) else None

# The dashboard must display the KPI values exactly as they exist in the
# mart `mart_supply_chain_kpi`. Do not calculate or substitute values from
# other marts. If the mart does not contain the column, show "N/A".
# NOTE: kiểm tra lại tên cột "avg_shipping_days_real" / "avg_shipping_days_scheduled"
# so với dbt schema thật của mart_supply_chain_kpi — mart_delivery_performance dùng
# thứ tự "avg_real_shipping_days" / "avg_scheduled_shipping_days" (ngược lại). Nếu
# schema thật khác tên này, 2 dòng KPI tương ứng sẽ hiển thị "N/A".
requested_cols = [
    ("total_orders", "Tổng đơn hàng", "Đơn hàng tổng thể", "kc-blue", lambda v: f"{int(v):,.0f}"),
    ("total_order_items", "Tổng dòng đơn hàng", "Số mục hàng trong đơn", "kc-purple", lambda v: f"{int(v):,.0f}"),
    ("total_customers", "Khách hàng", "Khách hàng hoạt động", "kc-green", lambda v: f"{int(v):,.0f}"),
    ("total_products", "Sản phẩm", "Sản phẩm có trong mart", "kc-amber", lambda v: f"{int(v):,.0f}"),
    ("total_sales", "Doanh thu", "Tổng doanh thu", "kc-red", lambda v: fmt_M(v)),
    ("total_profit", "Lợi nhuận", "Tổng lợi nhuận", "kc-violet", lambda v: fmt_M(v)),
    ("total_cost", "Chi phí", "Tổng chi phí vận hành", "kc-blue", lambda v: fmt_M(v)),
    ("profit_margin", "Profit margin", "Tỷ suất lợi nhuận", "kc-green", lambda v: pct(v)),
    ("late_order_items", "Mục hàng trễ", "Số mục hàng giao trễ", "kc-amber", lambda v: f"{int(v):,.0f}"),
    ("late_delivery_rate", "Late rate", "Tỷ lệ đơn hàng trễ", "kc-red", lambda v: pct(v)),
    ("avg_shipping_days_real", "Ngày giao thực tế", "Thời gian vận chuyển thực tế", "kc-purple", lambda v: f"{v:.2f} ngày"),
    ("avg_shipping_days_scheduled", "Ngày giao cam kết", "SLA dự kiến", "kc-blue", lambda v: f"{v:.2f} ngày"),
    ("avg_shipping_variance", "Ship variance", "Độ lệch so với lịch", "kc-violet", lambda v: f"{v:.2f}d"),
]

overview_metrics = []
for col, label, subtitle, cls, formatter in requested_cols:
    val = get_overview_value(col)
    if val is None:
        display_val = "N/A"
    else:
        try:
            display_val = formatter(val)
        except Exception:
            display_val = str(val)
    overview_metrics.append((label, display_val, subtitle, cls))

# ─────────────────────────────────────────────────────────────
# 8. PLOTLY THEME – TẤT CẢ CHỮ MÀU ĐEN (#000000)
# ─────────────────────────────────────────────────────────────
BASE_MARGIN = dict(l=10, r=10, t=64, b=14)
BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="#000000"),
    margin=BASE_MARGIN,
    hoverlabel=dict(bgcolor="#0b1425", font_color="#f0f8ff", font_size=12.5),
)
LEGEND_DEFAULT = dict(bgcolor="rgba(0,0,0,0)", borderwidth=0, font=dict(size=11, color="#000000"))

XBASE = dict(showgrid=False, zeroline=False, tickfont=dict(size=11, color="#000000"))
YBASE = dict(showgrid=True, gridcolor="#edf1f7", zeroline=False, tickfont=dict(size=11, color="#000000"))
TITLE = lambda t: dict(text=t, font=dict(size=14, color="#000000", weight=700), x=0, xanchor="left", pad=dict(l=4))

PAL   = ["#1a6fdc","#7c3aed","#059669","#d97706","#dc2626","#0891b2","#db2777","#65a30d"]
SEQ_RISK = [[0,"#dcfce7"],[0.35,"#fef9c3"],[0.65,"#fee2e2"],[1,"#7f1d1d"]]

# ─────────────────────────────────────────────────────────────
# 9. PAGE HEADER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
  <div class="ph-eyebrow">DataCo Global · Gold Layer · dbt + DuckDB + MotherDuck · XGBoost ML</div>
  <h1>Logistics Intelligence Dashboard</h1>
  <p>Phân tích hiệu suất vận hành · Star Schema Kimball · Predictive Analytics · SHAP Explainability</p>
  <div class="ph-badges">
    <span class="ph-badge">{total_orders:,.0f} đơn hàng</span>
    <span class="ph-badge">5 thị trường</span>
    <span class="ph-badge">dbt PASS=64</span>
    <span class="ph-badge">Cloud Synced</span>
    <span class="ph-badge ml">ML risk rate: {pct(ml_risk_rate)}</span>
    <span class="ph-badge ml">Gold mart: {ml_total:,} orders</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 10. KPI ROW
# ─────────────────────────────────────────────────────────────
st.markdown('<p class="sec-eyebrow">mart_supply_chain_kpi · Gold Layer</p>'
            '<p class="sec-title">Chỉ số tổng quan từ tầng mart_supply_chain_kpi</p>', unsafe_allow_html=True)
st.caption("Tất cả chỉ số dưới đây được lấy trực tiếp từ mart_supply_chain_kpi để đảm bảo tính nhất quán với tầng gold.")

slide_size = 3
slide_count = max(1, math.ceil(len(overview_metrics) / slide_size))
if 'kpi_slide' not in st.session_state:
    st.session_state.kpi_slide = 0

current_slide = st.session_state.kpi_slide % slide_count
slide_metrics = overview_metrics[current_slide * slide_size:(current_slide + 1) * slide_size]

cols = st.columns(3, gap="small")
for idx, (label, value, sub, cls) in enumerate(slide_metrics):
    with cols[idx]:
        st.markdown(f"""
        <div class="kpi-card {cls}">
          <div class="kpi-eyebrow">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 6, 1], gap="small")
with ctrl_col1:
    if st.button("←", key="kpi_prev", help="Chuyển sang slide trước", use_container_width=True):
        st.session_state.kpi_slide = (st.session_state.kpi_slide - 1) % slide_count
        st.rerun()
with ctrl_col3:
    if st.button("→", key="kpi_next", help="Chuyển sang slide tiếp theo", use_container_width=True):
        st.session_state.kpi_slide = (st.session_state.kpi_slide + 1) % slide_count
        st.rerun()
with ctrl_col2:
    dot_html = "".join(
        f'<span class="kpi-carousel-dot {"active" if i == current_slide else ""}" title="Slide {i + 1}"></span>'
        for i in range(slide_count)
    )
    st.markdown(f"<div class='kpi-carousel-controls'><div class='kpi-carousel-dots'>{dot_html}</div></div>", unsafe_allow_html=True)

st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 11. MAIN TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Hiệu suất Giao hàng",
    "Doanh thu và Lợi nhuận",
    "Phân tích Thị trường",
    "Executive Summary",
    "ML và Dự báo Rủi ro",
    "Insights và Khuyến nghị",
    "Chatbot",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 ─ DELIVERY PERFORMANCE
# ══════════════════════════════════════════════════════════════
with tab1:
    if dp.empty:
        st.warning(" Không có dữ liệu với bộ lọc hiện tại.")
    else:
        st.markdown('<p class="sec-eyebrow">mart_delivery_performance</p>'
                    '<p class="sec-title">Xu hướng & So sánh tỷ lệ giao trễ</p>', unsafe_allow_html=True)

        col_l, col_r = st.columns(2, gap="large")
        with col_l:
            df_trend = dp.groupby(["order_year_month","market"], as_index=False)["late_delivery_rate"].mean()
            fig = px.line(df_trend, x="order_year_month", y="late_delivery_rate",
                          color="market", markers=True, color_discrete_sequence=PAL,
                          labels={"order_year_month":"Tháng","late_delivery_rate":"Tỷ lệ trễ","market":"Thị trường"})
            fig.update_traces(line_width=2.5, marker_size=6)
            fig.add_hline(y=0.55, line_dash="dot", line_color="#dc2626",
                          annotation_text="Ngưỡng cảnh báo 55%", annotation_position="right")
            fig.update_layout(**BASE, title=TITLE("Xu hướng tỷ lệ giao trễ theo tháng"),
                              hovermode="x unified", xaxis=XBASE, yaxis={**YBASE,"tickformat":".0%"},
                              height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            df_m = dp.groupby("shipping_mode", as_index=False)["late_delivery_rate"].mean().sort_values("late_delivery_rate", ascending=False)
            colors = ["#dc2626" if r>0.75 else ("#f97316" if r>0.55 else ("#d97706" if r>0.40 else "#059669")) for r in df_m["late_delivery_rate"]]
            fig = go.Figure(go.Bar(
                x=df_m["shipping_mode"], y=df_m["late_delivery_rate"],
                marker_color=colors,
                text=[f"{r:.1%}" for r in df_m["late_delivery_rate"]],
                textposition="outside",
                textfont=dict(size=13, color="#000000"),
                hovertemplate="<b>%{x}</b><br>Tỷ lệ trễ: %{y:.1%}<extra></extra>",
            ))
            fig.add_hline(y=0.55, line_dash="dot", line_color="#dc2626",
                          annotation_text="Ngưỡng 55%", annotation_position="right")
            fig.update_layout(**BASE, title=TITLE("Tỷ lệ trễ theo phương thức vận chuyển"),
                              xaxis=XBASE, yaxis={**YBASE,"tickformat":".0%","range":[0,1.15]},
                              height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)
        st.markdown('<p class="sec-eyebrow">Delivery Status · SLA Performance</p>'
                    '<p class="sec-title">Trạng thái giao hàng & Bản đồ nhiệt rủi ro</p>', unsafe_allow_html=True)

        col_l2, col_r2 = st.columns(2, gap="large")
        with col_l2:
            df_ds = dp.groupby("delivery_status", as_index=False)["order_count"].sum()
            status_colors = {
                "Late delivery":"#dc2626",
                "Shipping on time":"#059669",
                "Advance shipping":"#1a6fdc",
                "Shipping canceled":"#d97706"
            }
            fig = go.Figure(go.Pie(
                labels=df_ds["delivery_status"], values=df_ds["order_count"],
                hole=0.52,
                marker=dict(colors=[status_colors.get(s,"#7a95b0") for s in df_ds["delivery_status"]],
                            line=dict(color="#fff",width=2.5)),
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>%{value:,} đơn — %{percent}<extra></extra>",
            ))
            fig.update_layout(**BASE, title=TITLE("Phân bổ trạng thái giao hàng"), showlegend=False, height=380)
            st.plotly_chart(fig, use_container_width=True)

        with col_r2:
            df_hm = dp.groupby(["market","shipping_mode"], as_index=False)["late_delivery_rate"].mean()
            pvt = df_hm.pivot(index="market", columns="shipping_mode", values="late_delivery_rate").fillna(0)
            fig = go.Figure(go.Heatmap(
                z=pvt.values, x=pvt.columns.tolist(), y=pvt.index.tolist(),
                colorscale=SEQ_RISK, zmin=0, zmax=1,
                text=[[f"{v:.0%}" for v in row] for row in pvt.values],
                texttemplate="%{text}",
                textfont=dict(size=13, color="#000000"),
                hovertemplate="Market: <b>%{y}</b><br>Mode: <b>%{x}</b><br>Late rate: %{z:.1%}<extra></extra>",
                colorbar=dict(tickformat=".0%", thickness=14, title="Trễ"),
            ))
            fig.update_layout(**BASE, title=TITLE("Bản đồ nhiệt: Tỷ lệ trễ × Market × Shipping Mode"),
                              xaxis=XBASE, yaxis={**YBASE,"showgrid":False}, height=380)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)
        st.markdown('<p class="sec-eyebrow">SLA Compliance · shipping_variance</p>'
                    '<p class="sec-title">Thời gian giao hàng thực tế vs Kế hoạch</p>', unsafe_allow_html=True)

        df_sla = dp.groupby("order_year_month", as_index=False).agg(
            avg_real=("avg_real_shipping_days","mean"),
            avg_sched=("avg_scheduled_shipping_days","mean"),
        )
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_sla["order_year_month"], y=df_sla["avg_real"],
                                 name="Thực tế (ngày)", line=dict(color="#1a6fdc",width=2.8),
                                 mode="lines+markers", marker_size=5,
                                 hovertemplate="<b>%{x}</b><br>Thực tế: %{y:.2f} ngày<extra></extra>"))
        fig.add_trace(go.Scatter(x=df_sla["order_year_month"], y=df_sla["avg_sched"],
                                 name="Cam kết SLA", line=dict(color="#dc2626",width=2.0,dash="dot"),
                                 mode="lines",
                                 hovertemplate="<b>%{x}</b><br>SLA: %{y:.2f} ngày<extra></extra>"))
        fig.add_trace(go.Bar(x=df_sla["order_year_month"],
                             y=df_sla["avg_real"] - df_sla["avg_sched"],
                             name="Lệch (real - SLA)",
                             marker_color=["#dc2626" if (r-s)>0 else "#059669"
                                           for r,s in zip(df_sla["avg_real"],df_sla["avg_sched"])],
                             opacity=0.4, yaxis="y2",
                             hovertemplate="<b>%{x}</b><br>Lệch: %{y:+.2f} ngày<extra></extra>"))
        fig.update_layout(**BASE, title=TITLE("Số ngày giao hàng thực tế vs cam kết SLA (cột = độ lệch)"),
                          xaxis=XBASE,
                          yaxis={**YBASE,"title":"Ngày"},
                          yaxis2=dict(overlaying="y",side="right",showgrid=False,
                                      title="Lệch (ngày)", zeroline=True, zerolinecolor="#dde6f0"),
                          hovermode="x unified",
                          legend=dict(x=0,y=1.05,orientation="h", font=dict(color="#000000")),
                          height=420)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)
        st.markdown('<p class="sec-eyebrow">SLA Scorecard tổng hợp</p>', unsafe_allow_html=True)
        df_sla_tbl = dp.groupby("shipping_mode", as_index=False).agg(
            orders=("order_count","sum"),
            late_rate=("late_delivery_rate","mean"),
            avg_real=("avg_real_shipping_days","mean"),
            avg_sched=("avg_scheduled_shipping_days","mean"),
            avg_var=("avg_shipping_variance","mean"),
        )
        df_sla_tbl["SLA Status"] = df_sla_tbl["late_rate"].apply(
            lambda x: "Nguy hiểm" if x>0.75 else ("Cần cải thiện" if x>0.50 else "Ổn định"))
        df_sla_tbl["late_rate"] = df_sla_tbl["late_rate"].map("{:.1%}".format)
        df_sla_tbl["avg_real"]  = df_sla_tbl["avg_real"].map("{:.2f}".format)
        df_sla_tbl["avg_sched"] = df_sla_tbl["avg_sched"].map("{:.2f}".format)
        df_sla_tbl["avg_var"]   = df_sla_tbl["avg_var"].map("{:+.2f}d".format)
        df_sla_tbl.columns      = ["Shipping Mode","Đơn hàng","Tỷ lệ trễ","Ngày thực tế","Ngày SLA","Variance","Đánh giá SLA"]
        st.dataframe(df_sla_tbl.set_index("Shipping Mode"), use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 ─ SALES & PROFITABILITY
# ══════════════════════════════════════════════════════════════
with tab2:
    if sp.empty:
        st.warning(" Không có dữ liệu với bộ lọc hiện tại.")
    else:
        st.markdown('<p class="sec-eyebrow">mart_sales_profitability · Gold Layer</p>'
                    '<p class="sec-title">Doanh thu · Lợi nhuận · Chi phí · Chiết khấu</p>', unsafe_allow_html=True)

        col_l, col_r = st.columns(2, gap="large")
        with col_l:
            df_st = sp.groupby(["order_year_month","market"], as_index=False)["total_sales"].sum()
            fig = px.area(df_st, x="order_year_month", y="total_sales", color="market",
                          color_discrete_sequence=PAL,
                          labels={"order_year_month":"Tháng","total_sales":"Doanh thu (USD)","market":"TT"})
            fig.update_layout(**BASE, title=TITLE("Doanh thu theo tháng — phân theo thị trường"),
                              xaxis=XBASE, yaxis={**YBASE,"tickprefix":"$","tickformat":",.0f"},
                              hovermode="x unified", height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            df_seg = sp.groupby("customer_segment", as_index=False).apply(
                lambda x: pd.Series({
                    "profit_margin": x["total_profit"].sum()/x["total_sales"].sum() if x["total_sales"].sum()>0 else 0,
                    "avg_discount": x["avg_discount_rate"].mean(),
                    "total_sales": x["total_sales"].sum(),
                })
            ).reset_index(drop=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_seg["customer_segment"], y=df_seg["profit_margin"],
                                 name="Profit Margin", marker_color="#059669",
                                 text=[f"{v:.1%}" for v in df_seg["profit_margin"]],
                                 textposition="outside",
                                 textfont=dict(size=12, color="#000000")))
            fig.add_trace(go.Bar(x=df_seg["customer_segment"], y=df_seg["avg_discount"],
                                 name="Avg Discount Rate", marker_color="#d97706",
                                 text=[f"{v:.1%}" for v in df_seg["avg_discount"]],
                                 textposition="outside",
                                 textfont=dict(size=12, color="#000000")))
            # FIX: đặt range y động có khoảng đệm để label "outside" không bị cắt
            max_seg_val = max(
                float(df_seg["profit_margin"].max()) if not df_seg.empty else 0.1,
                float(df_seg["avg_discount"].max()) if not df_seg.empty else 0.1,
            )
            fig.update_layout(**BASE, title=TITLE("Profit Margin vs Discount Rate theo Customer Segment"),
                              xaxis=XBASE,
                              yaxis={**YBASE,"tickformat":".0%","range":[0, max(max_seg_val*1.35, 0.1)]},
                              barmode="group", height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)
        col_l2, col_r2 = st.columns(2, gap="large")

        with col_l2:
            df_tree = sp.groupby(["department_name","category_name"], as_index=False)["total_sales"].sum()
            df_tree = df_tree[df_tree["total_sales"]>0]
            fig = px.treemap(df_tree, path=["department_name","category_name"], values="total_sales",
                             color="total_sales", color_continuous_scale="Blues",
                             hover_data={"total_sales":":.0f"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="Inter, sans-serif", size=11, color="#000000"),
                              margin=dict(l=8,r=8,t=42,b=8),
                              title=TITLE("Cơ cấu doanh thu: Department → Category (Treemap)"),
                              hoverlabel=dict(bgcolor="#0b1425",font_color="#f0f8ff",font_size=11.5),
                              height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col_r2:
            df_scat = sp.groupby("category_name", as_index=False).apply(
                lambda x: pd.Series({
                    "profit_margin": x["total_profit"].sum()/x["total_sales"].sum() if x["total_sales"].sum()>0 else 0,
                    "avg_discount": x["avg_discount_rate"].mean(),
                    "total_sales": x["total_sales"].sum(),
                })
            ).reset_index(drop=True)
            fig = px.scatter(df_scat, x="avg_discount", y="profit_margin",
                             size="total_sales", color="category_name",
                             hover_name="category_name",
                             labels={"avg_discount":"Tỷ lệ chiết khấu","profit_margin":"Profit Margin"},
                             color_discrete_sequence=PAL)
            fig.update_layout(**BASE, title=TITLE("Discount Rate vs Profit Margin theo Category"),
                              xaxis={**XBASE,"tickformat":".0%"},
                              yaxis={**YBASE,"tickformat":".0%"}, showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)
        st.markdown('<p class="sec-eyebrow">dim_product · mart_sales_profitability</p>'
                    '<p class="sec-title">Top 15 sản phẩm theo doanh thu & lợi nhuận</p>', unsafe_allow_html=True)

        df_prod = sp.groupby("product_name", as_index=False).agg(
            total_sales=("total_sales","sum"), total_profit=("total_profit","sum")
        ).sort_values("total_sales", ascending=False).head(15)
        df_prod["profit_margin"] = df_prod["total_profit"]/df_prod["total_sales"]
        fig = go.Figure()
        fig.add_trace(go.Bar(y=df_prod["product_name"], x=df_prod["total_sales"],
                             name="Doanh thu", orientation="h", marker_color="#1a6fdc",
                             hovertemplate="<b>%{y}</b><br>Doanh thu: $%{x:,.0f}<extra></extra>"))
        fig.add_trace(go.Bar(y=df_prod["product_name"], x=df_prod["total_profit"],
                             name="Lợi nhuận", orientation="h", marker_color="#059669",
                             hovertemplate="<b>%{y}</b><br>Lợi nhuận: $%{x:,.0f}<extra></extra>"))
        fig.update_layout(**BASE, title=TITLE("Top 15 sản phẩm theo doanh thu"), barmode="overlay",
                          xaxis={**XBASE,"tickprefix":"$","tickformat":",.0f"},
                          yaxis={**YBASE,"showgrid":False}, height=480)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 ─ MARKET ANALYSIS
# ══════════════════════════════════════════════════════════════
with tab3:
    if ex.empty:
        st.warning(" Không có dữ liệu với bộ lọc hiện tại.")
    else:
        st.markdown('<p class="sec-eyebrow">mart_executive_summary · dim_location</p>'
                    '<p class="sec-title">Phân tích so sánh theo thị trường</p>', unsafe_allow_html=True)

        col_l, col_r = st.columns(2, gap="large")
        with col_l:
            df_mkt = ex.groupby("market", as_index=False)["total_sales"].sum().sort_values("total_sales",ascending=False)
            fig = go.Figure(go.Pie(
                labels=df_mkt["market"], values=df_mkt["total_sales"],
                hole=0.52, marker=dict(colors=PAL, line=dict(color="#fff",width=2.5)),
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
            ))
            fig.update_layout(**BASE, title=TITLE("Tỷ trọng doanh thu theo thị trường"), height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            df_radar = ex.groupby("market", as_index=False).apply(lambda x: pd.Series({
                "late_rate": x["late_delivery_rate"].mean(),
                "profit_margin": x["total_profit"].sum()/x["total_sales"].sum() if x["total_sales"].sum()>0 else 0,
                "avg_ship_var": x["avg_shipping_variance"].mean(),
            })).reset_index(drop=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_radar["market"], y=df_radar["late_rate"],
                                 name="Late Rate", marker_color="#dc2626",
                                 text=[f"{v:.1%}" for v in df_radar["late_rate"]],
                                 textposition="outside",
                                 textfont=dict(size=12, color="#000000")))
            fig.add_trace(go.Bar(x=df_radar["market"], y=df_radar["profit_margin"],
                                 name="Profit Margin", marker_color="#059669",
                                 text=[f"{v:.1%}" for v in df_radar["profit_margin"]],
                                 textposition="outside",
                                 textfont=dict(size=12, color="#000000")))
            # FIX: range y động có khoảng đệm để label "outside" không bị cắt
            max_radar_val = max(
                float(df_radar["late_rate"].max()) if not df_radar.empty else 0.1,
                float(df_radar["profit_margin"].max()) if not df_radar.empty else 0.1,
            )
            fig.update_layout(**BASE, title=TITLE("Late Rate vs Profit Margin theo thị trường"),
                              xaxis=XBASE,
                              yaxis={**YBASE,"tickformat":".0%","range":[0, max(max_radar_val*1.35, 0.1)]},
                              barmode="group", height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)
        df_risk = ex.groupby(["market","delivery_risk_level"], as_index=False)["total_orders"].sum()
        fig = px.bar(df_risk, x="market", y="total_orders", color="delivery_risk_level",
                     color_discrete_map={"High delivery risk":"#dc2626","Medium delivery risk":"#d97706","Low delivery risk":"#059669"},
                     labels={"market":"Thị trường","total_orders":"Đơn hàng","delivery_risk_level":"Risk Level"},
                     barmode="stack")
        fig.update_layout(**BASE, title=TITLE("Phân bổ mức độ rủi ro giao hàng theo thị trường (delivery_risk_level)"),
                          xaxis=XBASE, yaxis={**YBASE,"tickformat":",.0f"}, height=380)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)
        st.markdown('<p class="sec-eyebrow">Bảng tóm tắt theo thị trường</p>', unsafe_allow_html=True)
        df_tbl = ex.groupby("market", as_index=False).agg(
            total_orders=("total_orders","sum"), total_customers=("total_customers","sum"),
            total_sales=("total_sales","sum"), total_profit=("total_profit","sum"),
            late_rate=("late_delivery_rate","mean"), avg_ship_var=("avg_shipping_variance","mean"),
        )
        df_tbl["profit_margin"] = df_tbl["total_profit"]/df_tbl["total_sales"]
        df_tbl["SLA Status"]    = df_tbl["late_rate"].apply(
            lambda x: "Cao" if x>0.58 else ("TB" if x>0.50 else "Tốt"))
        df_tbl["total_sales"]   = df_tbl["total_sales"].map("${:,.0f}".format)
        df_tbl["total_profit"]  = df_tbl["total_profit"].map("${:,.0f}".format)
        df_tbl["profit_margin"] = df_tbl["profit_margin"].map("{:.1%}".format)
        df_tbl["late_rate"]     = df_tbl["late_rate"].map("{:.1%}".format)
        df_tbl["avg_ship_var"]  = df_tbl["avg_ship_var"].map("{:+.2f}d".format)
        df_tbl.columns = ["Thị trường","Đơn hàng","Khách hàng","Doanh thu","Lợi nhuận","Late Rate","Ship Variance","Profit Margin","Đánh giá"]
        st.dataframe(df_tbl.set_index("Thị trường"), use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 ─ EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════
with tab4:
    if ex.empty:
        st.warning(" Không có dữ liệu.")
    else:
        st.markdown('<p class="sec-eyebrow">mart_executive_summary · business_health_flag · delivery_risk_level</p>'
                    '<p class="sec-title">Tổng hợp điều hành — Bảng chỉ số KPI theo tháng</p>', unsafe_allow_html=True)

        df_rev = ex.groupby("order_year_month", as_index=False).agg(
            total_sales=("total_sales","sum"),
            total_profit=("total_profit","sum"),
            total_cost=("total_cost","sum"),
            late_delivery_rate=("late_delivery_rate","mean"),
            avg_shipping_variance=("avg_shipping_variance","mean"),
        )
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_rev["order_year_month"], y=df_rev["total_sales"],
                                 name="Doanh thu", fill="tozeroy", line=dict(color="#1a6fdc",width=2.5),
                                 fillcolor="rgba(26,111,220,.08)"))
        fig.add_trace(go.Scatter(x=df_rev["order_year_month"], y=df_rev["total_profit"],
                                 name="Lợi nhuận", fill="tozeroy", line=dict(color="#059669",width=2.5),
                                 fillcolor="rgba(5,150,105,.08)"))
        fig.add_trace(go.Scatter(x=df_rev["order_year_month"], y=df_rev["total_cost"],
                                 name="Chi phí", line=dict(color="#d97706",width=2.0,dash="dot")))
        fig.update_layout(**BASE, title=TITLE("Doanh thu · Lợi nhuận · Chi phí theo tháng"),
                          xaxis=XBASE, yaxis={**YBASE,"tickprefix":"$","tickformat":",.0f"},
                          hovermode="x unified", height=380)
        st.plotly_chart(fig, use_container_width=True)

        col_l, col_r = st.columns(2, gap="large")
        with col_l:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_rev["order_year_month"], y=df_rev["late_delivery_rate"],
                                     name="Late Rate", line=dict(color="#dc2626",width=2.5), yaxis="y"))
            fig.add_trace(go.Bar(x=df_rev["order_year_month"], y=df_rev["avg_shipping_variance"],
                                 name="Ship Variance (ngày)", marker_color="rgba(217,119,6,.3)", yaxis="y2"))
            fig.add_hline(y=0.55, line_dash="dot", line_color="#dc2626",
                          annotation_text="Ngưỡng 55%", annotation_position="right", yref="y")
            fig.update_layout(**BASE, title=TITLE("Late Rate & Shipping Variance theo tháng"),
                              xaxis=XBASE,
                              yaxis=dict(showgrid=True,gridcolor="#edf1f7",tickformat=".0%",title="Late Rate"),
                              yaxis2=dict(overlaying="y",side="right",showgrid=False,title="Variance (ngày)"),
                              legend=dict(x=0,y=1.1,orientation="h", font=dict(color="#000000")), height=380)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            df_flag = ex.groupby("business_health_flag", as_index=False)["total_orders"].sum()
            clr = {"Normal":"#059669","Negative profit":"#dc2626","No sales":"#d97706"}
            fig = go.Figure(go.Pie(
                labels=df_flag["business_health_flag"], values=df_flag["total_orders"],
                hole=0.5,
                marker=dict(colors=[clr.get(l,"#7a95b0") for l in df_flag["business_health_flag"]],
                            line=dict(color="#fff",width=2.5)),
                textinfo="percent+label",
            ))
            fig.update_layout(**BASE, title=TITLE("business_health_flag — Tình trạng kinh doanh"), height=380)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)
        st.markdown('<p class="sec-eyebrow">Monthly KPI Scorecard (24 tháng gần nhất)</p>', unsafe_allow_html=True)
        df_score = ex.groupby("order_year_month", as_index=False).agg(
            orders=("total_orders","sum"), customers=("total_customers","sum"),
            sales=("total_sales","sum"), profit=("total_profit","sum"),
            late=("late_delivery_rate","mean"), var=("avg_shipping_variance","mean"),
        ).sort_values("order_year_month", ascending=False).head(24)
        df_score["margin"] = df_score["profit"]/df_score["sales"]
        df_score["Tình trạng"] = df_score.apply(
            lambda r: "Rủi ro" if r["late"]>0.58 else ("Cần theo dõi" if r["late"]>0.50 else "Ổn định"), axis=1)
        df_score["sales"]  = df_score["sales"].map("${:,.0f}".format)
        df_score["profit"] = df_score["profit"].map("${:,.0f}".format)
        df_score["margin"] = df_score["margin"].map("{:.1%}".format)
        df_score["late"]   = df_score["late"].map("{:.1%}".format)
        df_score["var"]    = df_score["var"].map("{:+.2f}d".format)
        df_score.columns   = ["Tháng","Đơn hàng","Khách hàng","Doanh thu","Lợi nhuận","Late Rate","Ship Variance","Margin","Tình trạng"]
        st.dataframe(df_score.set_index("Tháng"), use_container_width=True, height=450)

# ══════════════════════════════════════════════════════════════
# TAB 5 ─ ML & PREDICTIVE ANALYTICS
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="sec-eyebrow">mart_ml_delivery_risk_features · Gold Layer</p>'
                '<p class="sec-title">Machine Learning — Dự báo rủi ro giao hàng trễ</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:#f0f4f9;border:1px solid #dde6f0;border-radius:12px;padding:18px 22px;margin-bottom:28px;'>
        <div style='display:flex;gap:24px;flex-wrap:wrap;align-items:center;'>
            <div><span style='font-weight:700;font-size:1.2rem;color:#0b1425;'>Gold Mart ML Features</span>
                  <span style='background:#6d28d9;color:#fff;padding:2px 12px;border-radius:999px;font-size:0.7rem;font-weight:700;margin-left:8px;'>Orders: {ml_total:,}</span></div>
            <div style='color:#4a6077;font-size:0.85rem;'>Dự báo rủi ro giao hàng trễ từ dữ liệu đơn hàng trong mart_ml_delivery_risk_features</div>
            <span class='badge bg-blue'>From mart data</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_m1, col_m2, col_m3 = st.columns(3, gap="medium")
    with col_m1:
        st.markdown(f"""
        <div class="ml-metric">
            <div class="ml-metric-val" style='color:#7c3aed;'>{ml_total:,.0f}</div>
            <div class="ml-metric-label">Tổng số đơn hàng</div>
            <div class="ml-metric-desc">Đơn hàng có đủ feature</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="ml-metric">
            <div class="ml-metric-val" style='color:#dc2626;'>{ml_risk_count:,.0f}</div>
            <div class="ml-metric-label">Đơn hàng rủi ro cao</div>
            <div class="ml-metric-desc">target_late_delivery_risk = 1</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"""
        <div class="ml-metric">
            <div class="ml-metric-val" style='color:#059669;'>{(1-ml_risk_rate):.1%}</div>
            <div class="ml-metric-label">Tỷ lệ an toàn</div>
            <div class="ml-metric-desc">Không có rủi ro trễ</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)

    col_l, col_r = st.columns(2, gap="large")
    with col_l:
        st.markdown('<p class="sec-eyebrow">Phân phối rủi ro theo biến số</p>'
                    '<p class="sec-title">Tỷ lệ rủi ro theo phân khúc khách hàng</p>', unsafe_allow_html=True)

        df_risk_seg = (
            ml.groupby("customer_segment", as_index=False)["target_late_delivery_risk"]
              .mean()
              .sort_values("target_late_delivery_risk", ascending=False)
        )
        fig = px.bar(
            df_risk_seg,
            x="customer_segment",
            y="target_late_delivery_risk",
            color="target_late_delivery_risk",
            color_continuous_scale=[[0, "#059669"], [0.45, "#d97706"], [1, "#dc2626"]],
            labels={"customer_segment": "Phân khúc khách hàng", "target_late_delivery_risk": "Tỷ lệ rủi ro"},
            text=[f"{v:.1%}" for v in df_risk_seg["target_late_delivery_risk"]],
            text_auto=True,
        )
        # FIX: range y động thay cho [0, 0.8] cố định — tránh cắt label khi giá trị gần trần
        max_seg_risk = float(df_risk_seg["target_late_delivery_risk"].max()) if not df_risk_seg.empty else 0.1
        fig.update_layout(**BASE)
        fig.update_layout(title=TITLE("Tỷ lệ rủi ro theo phân khúc khách hàng"), xaxis=XBASE,
                          yaxis={**YBASE, "tickformat": ".0%", "range": [0, max(max_seg_risk*1.3, 0.1)]},
                          height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<p class="sec-eyebrow">Phân phối rủi ro theo phương thức vận chuyển</p>'
                    '<p class="sec-title">Địa phương nào có rủi ro cao nhất?</p>', unsafe_allow_html=True)

        df_risk_mode = (
            ml.groupby("shipping_mode", as_index=False)["target_late_delivery_risk"]
              .mean()
              .sort_values("target_late_delivery_risk", ascending=False)
        )
        colors_mode = ["#dc2626" if r > 0.7 else "#f97316" if r > 0.5 else "#059669" for r in df_risk_mode["target_late_delivery_risk"]]
        fig = go.Figure(go.Bar(
            x=df_risk_mode["shipping_mode"],
            y=df_risk_mode["target_late_delivery_risk"],
            marker_color=colors_mode,
            text=[f"{v:.1%}" for v in df_risk_mode["target_late_delivery_risk"]],
            textposition="outside",
            textfont=dict(size=12, color="#000000"),
            hovertemplate="<b>%{x}</b><br>Rủi ro: %{y:.1%}<extra></extra>",
        ))
        # FIX: range y động thay cho [0, 0.8] cố định — tránh cắt label khi giá trị gần trần
        max_mode_risk = float(df_risk_mode["target_late_delivery_risk"].max()) if not df_risk_mode.empty else 0.1
        fig.update_layout(**BASE)
        fig.update_layout(title=TITLE("Tỷ lệ rủi ro theo phương thức vận chuyển"), xaxis=XBASE,
                          yaxis={**YBASE, "tickformat": ".0%", "range": [0, max(max_mode_risk*1.3, 0.1)]},
                          height=380)
        st.plotly_chart(fig, use_container_width=True)

    # ── FIX/BỔ SUNG: Khối "risk band cards" — trước đây CSS .risk-card /
    # .risk-very-high/high/medium/watch/low được định nghĩa nhưng KHÔNG hề
    # được sử dụng ở bất kỳ đâu trong code. Khối dưới đây tận dụng đúng các
    # class đó, và chỉ dùng số liệu tỷ lệ rủi ro trung bình THẬT đã tính từ
    # mart_ml_delivery_risk_features (df_risk_mode ở trên) — không tự bịa
    # hay tính điểm dự báo mới.
    st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)
    st.markdown('<p class="sec-eyebrow">Phân loại mức độ rủi ro · shipping_mode</p>'
                '<p class="sec-title">Xếp hạng rủi ro theo phương thức vận chuyển (dữ liệu thực từ mart)</p>', unsafe_allow_html=True)

    def risk_band(rate):
        if rate > 0.70: return "risk-very-high", "Rất cao"
        if rate > 0.55: return "risk-high", "Cao"
        if rate > 0.40: return "risk-medium", "Trung bình"
        if rate > 0.25: return "risk-watch", "Cần theo dõi"
        return "risk-low", "Thấp"

    if not df_risk_mode.empty:
        risk_cols = st.columns(len(df_risk_mode), gap="small")
        for i, (_, row) in enumerate(df_risk_mode.iterrows()):
            band_cls, band_lbl = risk_band(row["target_late_delivery_risk"])
            with risk_cols[i]:
                st.markdown(f"""
                <div class="risk-card {band_cls}">
                    <div class="risk-label">{band_lbl}</div>
                    <div class="risk-range">{row['shipping_mode']}</div>
                    <div class="risk-desc">Tỷ lệ rủi ro trung bình: <b>{row['target_late_delivery_risk']:.1%}</b><br>Nguồn: mart_ml_delivery_risk_features</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Không có đủ dữ liệu trong mart để phân loại mức độ rủi ro.")

    st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)

    st.markdown('<p class="sec-eyebrow">Risk drivers from mart data</p>'
                '<p class="sec-title">Top 8 yếu tố có mức độ phân biệt rủi ro cao nhất</p>', unsafe_allow_html=True)

    if not risk_feature_df.empty:
        for _, row in risk_feature_df.iterrows():
            pct_val = min(100.0, max(8.0, float(row["risk_gap"]) * 100.0))
            cls = "shap-bar-pos" if row["risk_gap"] >= 0 else "shap-bar-neg"
            label = "↑ rủi ro" if row["risk_gap"] >= 0 else "↓ rủi ro"
            st.markdown(f"""
            <div class="shap-row">
                <div class="shap-feat">{row['feature']}</div>
                <div class="shap-bar-wrap"><div class="{cls}" style="width:{pct_val:.1f}%;"></div></div>
                <div class="shap-val">{pct_val:.1f}%</div>
                <div style='font-size:0.7rem;color:#4a6077;min-width:60px;'>{label}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Không có đủ dữ liệu trong mart để tính mức độ phân biệt rủi ro cho các biến hiện tại.")

    if not risk_feature_df.empty:
        top_feature = risk_feature_df.iloc[0]["feature"]
        st.markdown(f"""
        <div style='background:#f0f4f9;border-radius:8px;padding:16px 20px;margin-top:16px;border-left:4px solid #7c3aed;'>
            <div style='font-size:0.75rem;color:#4a6077;line-height:1.8;'>
                <b style='color:#0b1425;'>Mart interpretation:</b>
                Biến <b>{top_feature}</b> cho thấy mức khác biệt rủi ro lớn nhất giữa các nhóm trong bảng <b>mart_ml_delivery_risk_features</b>.
                Các giá trị dưới đây được tính trực tiếp từ tỷ lệ rủi ro trung bình của từng nhóm trong mart.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 6 ─ INSIGHTS & RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<p class="sec-eyebrow">Gold Layer Insights · Business Intelligence</p>'
                '<p class="sec-title">Phân tích và khuyến nghị chiến lược</p>', unsafe_allow_html=True)

    col_i1, col_i2 = st.columns(2, gap="large")
    with col_i1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="i-title"> Hiệu suất giao hàng</div>
            <div class="i-body">
                Tỷ lệ giao hàng trễ trung bình là <b>{avg_late:.1%}</b> – đang ở mức <b>{late_lbl}</b>.
                Phương thức <b>{top_shipping_mode}</b> có tỷ lệ trễ cao nhất (<b>{top_shipping_rate:.1%}</b>).
            </div>
            <div class="i-rec">
                  <b>Khuyến nghị:</b> Ưu tiên cải thiện quy trình vận chuyển cho <b>{top_shipping_mode}</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <div class="i-title"> Tối ưu chiết khấu</div>
            <div class="i-body">
                Phân khúc <b>{top_margin_segment}</b> có profit margin cao nhất, trong khi <b>{top_discount_segment}</b> có chiết khấu trung bình cao nhất.
            </div>
            <div class="i-rec">
                  <b>Khuyến nghị:</b> Tái cấu trúc chính sách discount cho <b>{top_discount_segment}</b> để tối ưu lợi nhuận.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_i2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="i-title"> Phân tích thị trường</div>
            <div class="i-body">
                Thị trường <b>{top_revenue_market}</b> có doanh thu cao nhất, trong khi <b>{lowest_late_market}</b> có tỷ lệ trễ thấp nhất theo mart executive summary.
            </div>
            <div class="i-rec">
                  <b>Khuyến nghị:</b> Áp dụng mô hình vận hành của <b>{lowest_late_market}</b> cho <b>{top_revenue_market}</b> để tăng hiệu quả.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <div class="i-title"> ML Risk Prediction</div>
            <div class="i-body">
                Bảng <b>mart_ml_delivery_risk_features</b> hiện có <b>{ml_total:,}</b> hàng và <b>{ml_risk_count:,}</b> hàng thuộc nhóm rủi ro cao.
                Yếu tố phân biệt rủi ro lớn nhất hiện tại là <b>{risk_feature_df.iloc[0]['feature'] if not risk_feature_df.empty else 'N/A'}</b>.
            </div>
            <div class="i-rec">
                <b>Khuyến nghị:</b> Tích hợp dữ liệu ML mart này vào quy trình đặt hàng để cảnh báo rủi ro sớm.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)

    st.markdown('<p class="sec-eyebrow">Ma trận ưu tiên hành động</p>'
                '<p class="sec-title">Ma trận ưu tiên hành động</p>', unsafe_allow_html=True)
    
    priority_data = (
        dp.groupby(["market", "shipping_mode"], as_index=False)
          .agg(
              Tỷ_lệ_trễ=("late_delivery_rate", "mean"),
              Doanh_thu=("total_sales", "sum"),
              Đơn_hàng=("order_count", "sum"),
          )
          .assign(Khu_vực=lambda d: d["market"] + " - " + d["shipping_mode"])
          .sort_values(["Tỷ_lệ_trễ", "Doanh_thu"], ascending=[False, False])
          .head(8)
    )
    
    fig = px.scatter(priority_data, x="Tỷ_lệ_trễ", y="Doanh_thu",
                     size="Doanh_thu", color="Khu_vực",
                     hover_name="Khu_vực",
                     text="Khu_vực",
                     labels={"Tỷ_lệ_trễ":"Tỷ lệ giao hàng trễ", "Doanh_thu":"Doanh thu (USD)"},
                     color_discrete_sequence=PAL)
    fig.add_hline(y=4000000, line_dash="dash", line_color="#64748b", opacity=0.5)
    fig.add_vline(x=0.35, line_dash="dash", line_color="#64748b", opacity=0.5)
    fig.add_annotation(x=0.15, y=5500000, text=" Ưu tiên cao", showarrow=False,
                       font=dict(size=12, color="#059669", weight=700), yref="y")
    fig.add_annotation(x=0.50, y=2000000, text="🔍 Cần xem xét", showarrow=False,
                       font=dict(size=12, color="#d97706", weight=700), yref="y")
    fig.update_traces(textposition="top center", textfont=dict(size=10), marker=dict(line=dict(width=1, color="#ffffff")))
    fig.update_layout(**BASE, title=TITLE("Ma trận ưu tiên: Tỷ lệ trễ vs Doanh thu"),
                      xaxis={**XBASE,"tickformat":".0%","range":[0,0.6]},
                      yaxis={**YBASE,"tickprefix":"$","tickformat":",.0f"},
                      height=480, showlegend=True,
                      legend=dict(x=0.5, y=1.12, xanchor="center", orientation="h", bgcolor="rgba(255,255,255,0.8)"))
    st.plotly_chart(fig, use_container_width=True)

    risk_feature_label = risk_feature_df.iloc[0]["feature"] if not risk_feature_df.empty else "N/A"
    st.markdown(f"""
    <div style='background:#fff;border:1px solid #dde6f0;border-radius:12px;padding:20px 24px;margin-top:16px;'>
        <div style='font-weight:700;color:#0b1425;font-size:1rem;margin-bottom:12px;'>Kế hoạch hành động</div>
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:0.82rem;color:#4a6077;line-height:1.8;'>
            <div style='background:#f0fdf4;padding:12px 16px;border-radius:8px;border-left:3px solid #059669;'>
                <b style='color:#0b1425;'>Khẩn cấp:</b><br>
                Tối ưu {top_shipping_mode} tại {top_revenue_market}<br>
                <span style='font-size:0.7rem;color:#6a85a0;'>Tỷ lệ trễ hiện tại: {top_shipping_rate:.1%}</span>
            </div>
            <div style='background:#fffbeb;padding:12px 16px;border-radius:8px;border-left:3px solid #d97706;'>
                <b style='color:#0b1425;'>Quan trọng:</b><br>
                Điều chỉnh policy discount cho {top_discount_segment}<br>
                <span style='font-size:0.7rem;color:#6a85a0;'>Tập trung vào phân khúc có discount cao</span>
            </div>
            <div style='background:#eff6ff;padding:12px 16px;border-radius:8px;border-left:3px solid #1a6fdc;'>
                <b style='color:#0b1425;'>Chiến lược:</b><br>
                Mở rộng dữ liệu ML mart cho các thị trường khác<br>
                <span style='font-size:0.7rem;color:#6a85a0;'>Tăng chất lượng dự báo rủi ro</span>
            </div>
            <div style='background:#f5f3ff;padding:12px 16px;border-radius:8px;border-left:3px solid #7c3aed;'>
                <b style='color:#0b1425;'>Phân tích:</b><br>
                Theo dõi biến {risk_feature_label} trong mart<br>
                <span style='font-size:0.7rem;color:#6a85a0;'>Giữ nguyên nguồn dữ liệu từ mart</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Helper function cho datetime
# ─────────────────────────────────────────────────────────────
def get_datetime_now():
    return datetime.now().strftime("%Y%m%d_%H%M")

def extract_followups(response_text: str) -> tuple[str, list[str]]:
    import re
    followups = []
    clean_text = response_text
    pattern = r"\s*\*\*Câu hỏi tiếp theo có thể hỏi:\*\*\s*(.*?)$"
    match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
    if match:
        clean_text = response_text[:match.start()].rstrip()
        followup_block = match.group(1).strip()
        items = re.split(r'\n|;|•|-\s|\d+\.\s', followup_block)
        followups = [it.strip().strip('"\'') for it in items if len(it.strip()) > 10][:3]
    return clean_text, followups

def call_groq_with_retry(messages: list, api_key: str, max_retries: int = 2) -> tuple[str, bool, str]:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 1024,
        "stream": False,
    }
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"], True, ""
            elif resp.status_code == 401:
                return " **Lỗi xác thực**: API key không hợp lệ hoặc đã hết hạn. Vui lòng kiểm tra lại `GROQ_API_KEY` tại [console.groq.com](https://console.groq.com).", False, "auth"
            elif resp.status_code == 429:
                if attempt == max_retries: 
                    return " **Rate Limit**: Đã đạt giới hạn số lần gọi API (gọi quá nhiều token/phút). Hãy đợi 1 phút rồi thử lại.", False, "rate_limit"
            elif resp.status_code >= 500:
                if attempt == max_retries: 
                    return " Lỗi hệ thống từ máy chủ Groq. Vui lòng thử lại sau.", False, "server"
        except requests.exceptions.Timeout:
            if attempt == max_retries: 
                return " Kết nối quá hạn (Timeout). Máy chủ Groq không phản hồi kịp.", False, "timeout"
        except Exception as e:
            if attempt == max_retries: 
                return f"❌ Lỗi không xác định: {str(e)}", False, "unknown"
    return "❌ Lỗi xử lý yêu cầu.", False, "unknown"

# ══════════════════════════════════════════════════════════════
# TAB 7 ─ AI CHATBOT (Groq + LLaMA 3)
# ══════════════════════════════════════════════════════════════
with tab7:
    # ── Session states initialization
    if "chatbot_messages" not in st.session_state:
        st.session_state["chatbot_messages"] = []
    if "chatbot_feedback" not in st.session_state:
        st.session_state["chatbot_feedback"] = {}
    if "chatbot_last_error" not in st.session_state:
        st.session_state["chatbot_last_error"] = ""
    if "chatbot_retry_count" not in st.session_state:
        st.session_state["chatbot_retry_count"] = 0

    # ── Header Trợ lý ảo
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4c1d95 0%, #1e3a8a 100%); border-radius:14px; padding:24px 28px; margin-bottom:24px; border:1px solid #4338ca; box-shadow:0 4px 12px rgba(76,29,149,0.15)'>
      <div style='display:flex; align-items:center; gap:16px'>
        <div style='background:rgba(255,255,255,0.12); width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.05rem; font-weight:700; border:1px solid rgba(255,255,255,0.2); color:#f0f8ff'>AI</div>
        <div>
          <b style='color:#f0f8ff;font-size:0.95rem'>Trợ lý logistics thông minh</b><br>
          Được cung cấp ngữ cảnh đầy đủ từ <b style='color:#4ab3f0'>Gold Layer</b> — KPI tổng quan, hiệu suất giao hàng, doanh thu theo thị trường và kết quả ML dự báo rủi ro. Đặt câu hỏi bằng <b>tiếng Việt hoặc tiếng Anh</b>.<br>
          <span style='color:#a78bfa'>Groq LLaMA-3.3-70B · Phản hồi theo ngữ cảnh · Retry tự động</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Quick Prompt Buttons
    st.markdown('<p class="sec-eyebrow">Câu hỏi gợi ý nhanh</p>', unsafe_allow_html=True)
    qcol1, qcol2, qcol3 = st.columns(3, gap="small")
    quick_prompts = [
        ("Mặt hàng cần nhập thêm", "Dựa trên dữ liệu doanh thu tháng này, hãy cho biết 3 mặt hàng cần nhập thêm và giải thích lý do."),
        ("Phân tích rủi ro giao trễ", "Phân tích nguyên nhân chính gây ra tỷ lệ giao trễ cao và đề xuất 3 hành động cải thiện cụ thể."),
        ("Tối ưu lợi nhuận", "Thị trường nào đang có profit margin thấp nhất và cần được ưu tiên cải thiện? Đề xuất chiến lược."),
        ("Đơn hàng rủi ro cao", "Phương thức vận chuyển nào có tỷ lệ rủi ro giao trễ cao nhất? Tại sao và cần làm gì?"),
        ("Tóm tắt KPI tháng", "Hãy tóm tắt hiệu suất vận hành tháng gần nhất dưới góc độ COO: doanh thu, lợi nhuận, late rate."),
        ("So sánh thị trường", "So sánh hiệu suất giữa các thị trường và xác định thị trường nào tối ưu nhất về chi phí."),
    ]
    
    for idx, (lbl, prt) in enumerate(quick_prompts):
        target_col = qcol1 if idx < 2 else (qcol2 if idx < 4 else qcol3)
        if target_col.button(lbl, use_container_width=True, key=f"qp_{idx}"):
            st.session_state["chatbot_input_prefill"] = prt
            st.rerun()

    # ── Context Builder
    ctx_parts = []
    if isinstance(date_range, tuple) and len(date_range) == 2:
        date_label = f"{date_range[0]} → {date_range[1]}"
    else:
        date_label = str(date_range)

    ctx_parts.append(f"""=== THÔNG TIN TỔNG QUAN HỆ THỐNG (BỘ LỌC HIỆN TẠI) ===
- Thị trường lựa chọn: {sel_market}
- Khoảng thời gian: {date_label}
- Phương thức vận chuyển: {sel_mode}
- Phân khúc khách hàng: {sel_seg}
- Tổng doanh thu: {fmt_M(total_sales)}
- Tổng đơn hàng: {total_orders:,.0f}
- Profit Margin: {pct(profit_margin)}
- Tỷ lệ giao trễ trung bình: {pct(avg_late)}
- Shipping Variance trung bình: {avg_ship_var:+.2f} ngày
- ML Risk Rate: {pct(ml_risk_rate)} ({ml_risk_count:,.0f}/{ml_total:,.0f} đơn có rủi ro)""")

    if not sp.empty:
        top_prod = sp.groupby("product_name", as_index=False)["total_sales"].sum()\
                     .sort_values("total_sales", ascending=False).head(5)
        top_list = "; ".join(f"{r['product_name']} (${r['total_sales']:,.0f})" for _, r in top_prod.iterrows())
        ctx_parts.append(f"=== TOP 5 SẢN PHẨM DOANH THU CAO NHẤT ===\n{top_list}")

        cat_stats = sp.groupby("category_name", as_index=False).agg(
            total_sales=("total_sales","sum"),
            total_profit=("total_profit","sum"),
            avg_discount=("avg_discount_rate","mean"),
            total_qty=("total_quantity","sum"),
        ).sort_values("total_sales")
        low_list = "; ".join(
            f"{r['category_name']} (doanh thu ${r['total_sales']:,.0f}, qty {r['total_qty']:,.0f})"
            for _, r in cat_stats.head(3).iterrows())
        ctx_parts.append(f"=== DANH MỤC SẢN PHẨM DOANH THU THẤP NHẤT ===\n{low_list}")

    system_context = "\n\n".join(ctx_parts)

    system_prompt = f"""Bạn là Trợ lý AI chuyên gia phân tích chuỗi cung ứng và logistics cao cấp của tập đoàn quốc tế DataCo Global.
    Bạn đang hỗ trợ Ban giám đốc (CEO, COO) và Quản lý Logistics đưa ra quyết định dựa trên dữ liệu từ Gold Layer trong Data Warehouse (qua MotherDuck).

    NGỮ CẢNH DỮ LIỆU HIỆN TẠI TRÊN DASHBOARD (ĐÃ ĐƯỢC TỔNG HỢP THEO BỘ LỌC CỦA NGƯỜI DÙNG):
    {system_context}

    QUY TẮC PHẢN HỒI:
    1. Luôn dẫn chiếu đến mart/table cụ thể khi đề cập số liệu.
    2. Trả lời bằng cùng ngôn ngữ với câu hỏi (Tiếng Việt hoặc Tiếng Anh).
    3. Luôn kết thúc với 1-2 khuyến nghị hành động cụ thể.
    4. Nhấn mạnh đây là hỗ trợ quyết định, không phải quyết định tự động.
    5. Giữ phong thái chuyên nghiệp, súc tích, dễ hiểu cho người dùng nghiệp vụ.
    6. Cuối mỗi response, thêm dòng "**Câu hỏi tiếp theo có thể hỏi:** [gợi ý 2-3 câu hỏi follow-up ngắn liên quan]" """

    # ── Chat layout
    chat_col, config_col = st.columns([3, 1], gap="large")

    with config_col:
        st.markdown("""
        <div style='background:#fff;border:1px solid #dde6f0;border-radius:14px; padding:18px 18px 14px;position:sticky;top:80px'>
          <div style='font-size:0.82rem;font-weight:700;color:#0b1425;margin-bottom:14px'>⚙️ Cấu hình</div>
        """, unsafe_allow_html=True)
        
        if GROQ_API_KEY and GROQ_API_KEY.startswith("gsk_"):
            st.success(" Groq API Key đã được cấu hình")
            st.caption("Key được lấy từ file `.env`")
        else:
            st.error(" Chưa có GROQ_API_KEY")
            st.info("Vui lòng thêm key vào file `.env` và restart Streamlit")
        active_key = GROQ_API_KEY

        st.markdown("---")
        if active_key:
            status_html = '<span class="api-status ok"><span class="status-dot"></span>API Key đã cấu hình</span>'
        else:
            status_html = '<span class="api-status err"><span class="status-dot"></span>Chưa cấu hình API</span>'
        st.markdown(status_html, unsafe_allow_html=True)

        st.markdown("---")
        if st.session_state["chatbot_messages"]:
            full_history_text = ""
            for msg in st.session_state["chatbot_messages"]:
                role = "USER" if msg["role"] == "user" else "AI ASSISTANT"
                full_history_text += f"[{msg.get('timestamp','--:--')}] {role}:\n{msg['content']}\n\n"
            
            st.download_button(
                label=" Export lịch sử chat (.txt)",
                data=full_history_text,
                file_name=f"dataco_chat_{get_datetime_now()}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.markdown('<div style="font-size:0.75rem;color:#a0aec0;text-align:center">Chưa có hội thoại để xuất.</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button(" Xoá lịch sử", use_container_width=True, type="secondary"):
            st.session_state["chatbot_messages"] = []
            st.session_state["chatbot_feedback"] = {}
            st.session_state["chatbot_last_error"] = ""
            st.session_state["chatbot_retry_count"] = 0
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ==============================================================================
# ĐOẠN CODE ĐÃ ĐƯỢC SỬA LẠI (Thay thế từ dòng "with chat_col:" đến hết Tab 7)
# ==============================================================================

    with chat_col:
        if st.session_state.get("chatbot_last_error") in ("rate_limit", "timeout", "server"):
            err_map = {
                "rate_limit": ("Rate limit — đã retry 2 lần. Vui lòng đợi vài giây."),
                "timeout": ("Timeout — kết nối chậm. Hãy thử lại."),
                "server": ("Lỗi máy chủ Groq. Dịch vụ có thể đang bận."),
            }
            icon, msg = err_map.get(st.session_state["chatbot_last_error"], ("", "Lỗi không xác định."))
            retry_col1, retry_col2 = st.columns([4, 1])
            with retry_col1:
                st.markdown(f'<div class="retry-banner">{icon} <b>{msg}</b></div>', unsafe_allow_html=True)
            with retry_col2:
                if st.button(" Retry", use_container_width=True):
                    st.session_state["chatbot_last_error"] = ""
                    st.rerun()

        chat_box = st.container()
        with chat_box:
            if not st.session_state["chatbot_messages"]:
                st.markdown("""
                <div style='text-align:center;padding:52px 20px;color:#8a9fb0'>
                  <div style='font-size:1.4rem;margin-bottom:12px;font-weight:700;color:#4a5568'>Chat</div>
                  <b style='color:#4a5568'>Chưa có tin nhắn nào</b><br>
                  <span style='font-size:0.8rem'>Hãy chọn một câu hỏi nhanh phía trên hoặc nhập nội dung vào hộp thoại bên dưới để bắt đầu thảo luận với Trợ lý AI.</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                for idx, msg in enumerate(st.session_state["chatbot_messages"]):
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div class="chat-row user">
                          <div class="msg-bubble user">
                            <span style="font-size:0.7rem;opacity:0.75;display:block;margin-bottom:3px;text-align:right">Bạn • {msg.get('timestamp','')}</span>
                            {msg['content']}
                          </div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-row bot">
                          <div class="msg-bubble bot">
                            <span style="font-size:0.7rem;color:#7c3aed;font-weight:700;display:block;margin-bottom:3px">Trợ lý AI • {msg.get('timestamp','')}</span>
                            {msg['content']}
                          </div>
                        </div>""", unsafe_allow_html=True)
                        
                        # FIX: Nút feedback trước đây dùng <button onclick="return false;">
                        # nên bấm vào KHÔNG có tác dụng gì (bug UI thật). Thay bằng
                        # st.button thật, có lưu trạng thái vào session_state.
                        fb_state = st.session_state["chatbot_feedback"].get(idx, None)
                        fb_c1, fb_c2, fb_c3 = st.columns([1, 1, 8])
                        with fb_c1:
                            up_label = "✅ 👍" if fb_state == "up" else "👍 Hữu ích"
                            if st.button(up_label, key=f"fb_up_{idx}", use_container_width=True):
                                st.session_state["chatbot_feedback"][idx] = "up"
                                st.rerun()
                        with fb_c2:
                            down_label = "✅ 👎" if fb_state == "down" else "👎 Chưa tốt"
                            if st.button(down_label, key=f"fb_down_{idx}", use_container_width=True):
                                st.session_state["chatbot_feedback"][idx] = "down"
                                st.rerun()
                        
                        if "followups" in msg and msg["followups"]:
                            st.markdown('<div class="followup-row">', unsafe_allow_html=True)
                            for f_idx, fu in enumerate(msg["followups"]):
                                if st.button(
                                    f"{fu}",
                                    key=f"fu_{idx}_{f_idx}",
                                    use_container_width=True,
                                    help=fu,
                                ):
                                    st.session_state["chatbot_input_prefill"] = fu
                                    st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        typing_placeholder = st.empty()

    # ─────────────────────────────────────────────────────────────
    #  Đoạn này được đưa ra ngoài cùng (ngang hàng với 'with chat_col:')
    # ─────────────────────────────────────────────────────────────
    prefill = st.session_state.pop("chatbot_input_prefill", "")
    user_input = st.chat_input(
        placeholder="Ví dụ: Tại sao First Class có tỷ lệ trễ cao? Cần làm gì?",
    )
    if prefill:
        user_input = prefill

    if user_input:
        if not active_key:
            st.warning(" Vui lòng nhập **Groq API Key** ở cột bên phải hoặc cấu hình `GROQ_API_KEY` trong `.env`.")
        else:
            now_str = datetime.now().strftime("%H:%M")
            
            st.session_state["chatbot_messages"].append({
                "role": "user",
                "content": user_input,
                "timestamp": now_str
            })
            st.rerun()

    # Xử lý sau khi Streamlit nhận diện trạng thái vừa thêm tin nhắn mới của User
    if st.session_state["chatbot_messages"] and st.session_state["chatbot_messages"][-1]["role"] == "user":
        latest_user_msg = st.session_state["chatbot_messages"][-1]["content"]
        
        with chat_col:
            with typing_placeholder.container():
                st.markdown("""
                <div class="typing-indicator">
                  <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                  </div>
                  <span style="font-size:0.78rem;color:#7c3aed;font-weight:600">Trợ lý đang truy vấn Gold Layer & phân tích phản hồi...</span>
                </div>""", unsafe_allow_html=True)

            api_messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state["chatbot_messages"][-6:]:
                api_messages.append({"role": m["role"], "content": m["content"]})

            raw_response, success, err_type = call_groq_with_retry(api_messages, active_key)
            
            if not success:
                st.session_state["chatbot_last_error"] = err_type
                st.session_state["chatbot_messages"].append({
                    "role": "assistant",
                    "content": raw_response,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "followups": [],
                    "success": False,
                })
                st.rerun()
            else:
                st.session_state["chatbot_last_error"] = ""
                clean_response, followups = extract_followups(raw_response)
                
                st.session_state["chatbot_messages"].append({
                    "role": "assistant",
                    "content": clean_response,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "followups": followups,
                    "success": True,
                })
                st.rerun()

    st.markdown('<hr class="dash-hr">', unsafe_allow_html=True)