import streamlit as st
import pandas as pd

from src.load_data import load_all_data
from src.calculations import calculate_dashboard
from config.data_sources import EXCEL_URLS
from src.load_data import load_excel_sheets
from src.calculations import (
    extract_financial_performance,
    create_financial_chart
)

sheets = load_excel_sheets(
    EXCEL_URLS["financial"]
)

financial_df = extract_financial_performance(
    sheets
)

financial_chart = create_financial_chart(
    financial_df
)

st.subheader("Financial Performance")

st.plotly_chart(
    financial_chart,
    use_container_width=True
)

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Dashboard Program Ditsama 2026",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# LOAD CSS
# ==========================================

with open("assets/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# ==========================================
# HEADER
# ==========================================

st.title("📊 Dashboard Program Ditsama 2026")

st.write(
    "Dashboard monitoring program, progress, "
    "financial performance, dan management alert."
)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("CONTROL")

st.sidebar.selectbox(
    "Program",
    ["Semua Program"]
)

st.sidebar.selectbox(
    "Bidang",
    ["Semua Bidang"]
)

st.sidebar.selectbox(
    "Tahun",
    [2026]
)

st.sidebar.button("🔄 Refresh Data")


# ==========================================
# KPI
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Program", "0")

with col2:
    st.metric("Progress", "0%")

with col3:
    st.metric("Budget Utilization", "0%")

with col4:
    st.metric("Management Alert", "0")


# ==========================================
# FINANCIAL PERFORMANCE & PARTICIPANT TARGET
# ==========================================

col_left, col_right = st.columns(2)

# ------------------------------------------
# FINANCIAL PERFORMANCE
# ------------------------------------------

with col_left:

    st.subheader("Financial Performance")

    st.info(
        "Data financial performance akan "
        "ditampilkan di sini."
    )


# ------------------------------------------
# PARTICIPANT TARGET
# ------------------------------------------

with col_right:

    st.subheader("Participant Target")

    st.info(
        "Data participant target akan "
        "ditampilkan di sini."
    )

# ==========================================
# MANAGEMENT ALERT
# ==========================================

st.subheader("Management Alert")

st.info(
    "Management alert akan "
    "muncul setelah data program terhubung."
)
