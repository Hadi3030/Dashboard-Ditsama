import streamlit as st
import pandas as pd

from src.load_data import load_all_data
from src.calculations import calculate_dashboard


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Program Dashboard",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# HEADER
# ==========================================

st.title("📊 Program Performance Dashboard")

st.caption("Monitoring Progress, Financial Performance & Management Alert")


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.header("Filter")

program = st.sidebar.selectbox(
    "Program",
    ["Semua Program"]
)

tahun = st.sidebar.selectbox(
    "Tahun",
    [2026]
)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()


# ==========================================
# LOAD DATA
# ==========================================

try:

    data = load_all_data()

    dashboard_data = calculate_dashboard(data)

except Exception as e:

    st.error(f"Gagal mengambil data: {e}")
    st.stop()


# ==========================================
# KPI
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Program",
        dashboard_data["total_program"]
    )

with col2:
    st.metric(
        "Progress",
        f'{dashboard_data["progress"]:.1f}%'
    )

with col3:
    st.metric(
        "Budget Utilization",
        f'{dashboard_data["budget_usage"]:.1f}%'
    )

with col4:
    st.metric(
        "Management Alert",
        dashboard_data["alert_count"]
    )


# ==========================================
# FINANCIAL PERFORMANCE
# ==========================================

st.subheader("Financial Performance")

financial_col1, financial_col2 = st.columns(2)

with financial_col1:

    st.plotly_chart(
        dashboard_data["financial_chart"],
        use_container_width=True
    )


with financial_col2:

    st.plotly_chart(
        dashboard_data["budget_chart"],
        use_container_width=True
    )


# ==========================================
# PROGRAM PROGRESS
# ==========================================

st.subheader("Program Progress")

st.plotly_chart(
    dashboard_data["progress_chart"],
    use_container_width=True
)


# ==========================================
# MANAGEMENT ALERT
# ==========================================

st.subheader("Management Alert")

st.dataframe(
    dashboard_data["alerts"],
    use_container_width=True,
    hide_index=True
)
