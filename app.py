import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.load_data import load_all_sheets
from src.calculations import (
    extract_financial_performance,
    create_financial_chart
)
from config.data_sources import EXCEL_URLS


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

try:
    with open("assets/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except FileNotFoundError:
    pass


# ==========================================
# HEADER
# ==========================================

st.title("📊 Dashboard Program Ditsama 2026")

st.write(
    "Dashboard monitoring program, progress, "
    "financial performance, dan management alert."
)


# ==========================================
# SIDEBAR / CONTROL
# ==========================================

st.sidebar.title("CONTROL")

# ------------------------------------------
# PROGRAM FILTER
# ------------------------------------------

if not financial_df.empty:

    program_list = sorted(
        financial_df["Program"]
        .dropna()
        .unique()
        .tolist()
    )

else:

    program_list = []

program_options = [
    "Semua Program"
] + program_list

program_filter = st.sidebar.selectbox(
    "Program",
    program_options
)


# ------------------------------------------
# TAHUN FILTER
# ------------------------------------------

if not financial_df.empty:

    year_list = sorted(
        financial_df["Tahun"]
        .dropna()
        .unique()
        .tolist()
    )

else:

    year_list = [2026]

year_options = [
    "Semua Tahun"
] + year_list

tahun_filter = st.sidebar.selectbox(
    "Tahun",
    year_options
)


# ------------------------------------------
# FILTER DATA
# ------------------------------------------

filtered_df = financial_df.copy()


if program_filter != "Semua Program":

    filtered_df = filtered_df[
        filtered_df["Program"]
        == program_filter
    ]


if tahun_filter != "Semua Tahun":

    filtered_df = filtered_df[
        filtered_df["Tahun"]
        == tahun_filter
    ]


# ------------------------------------------
# REFRESH
# ------------------------------------------

if st.sidebar.button("🔄 Refresh Data"):

    st.cache_data.clear()

    st.rerun()

# ==========================================
# LOAD FINANCIAL DATA
# ==========================================

try:

    sheets = load_all_sheets(
    EXCEL_URLS["financial"]
    )

    financial_df = extract_financial_performance(
        sheets
    )

    financial_chart = create_financial_chart(
        financial_df
    )

    data_status = True

except Exception as e:

    data_status = False
    financial_df = pd.DataFrame()

    st.warning(
        "Data Financial Performance belum dapat dibaca."
    )

    st.caption(
        f"Detail error: {e}"
    )


# ==========================================
# KPI
# ==========================================

if data_status:

    total_program = financial_df["Program"].nunique()

    total_target = financial_df["Target"].sum()

    total_actual = financial_df["Actual"].sum()

    if total_target > 0:
        budget_utilization = (
            total_actual / total_target
        ) * 100
    else:
        budget_utilization = 0

else:

    total_program = 0
    total_target = 0
    total_actual = 0
    budget_utilization = 0


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Program",
        total_program
    )


with col2:

    st.metric(
        "Progress",
        "0%"
    )


with col3:

    st.metric(
        "Budget Utilization",
        f"{budget_utilization:.1f}%"
    )


with col4:

    st.metric(
        "Management Alert",
        "0"
    )


# ==========================================
# FINANCIAL PERFORMANCE
# &
# PARTICIPANT TARGET
# ==========================================

col_left, col_right = st.columns(2)


# ==========================================
# FINANCIAL PERFORMANCE
# ==========================================

with col_left:

    st.subheader(
        "Financial Performance"
    )

    if data_status:

        st.plotly_chart(
            financial_chart,
            use_container_width=True
        )

    else:

        st.info(
            "Data Financial Performance "
            "belum tersedia."
        )


# ==========================================
# PARTICIPANT TARGET
# ==========================================

with col_right:

    st.subheader(
        "Participant Target"
    )

    st.info(
        "Participant Target akan "
        "ditampilkan di sini."
    )


# ==========================================
# PROGRAM PROGRESS
# ==========================================

st.subheader(
    "Program Progress"
)

st.info(
    "Grafik Program Progress akan "
    "ditampilkan setelah data progress "
    "program terhubung."
)


# ==========================================
# MANAGEMENT ALERT
# ==========================================

st.subheader(
    "Management Alert"
)

st.info(
    "Management Alert akan muncul "
    "setelah data program terhubung."
)
