import streamlit as st
import pandas as pd

from src.load_data import load_all_sheets

from src.calculations import (
    extract_financial_performance,
    create_financial_chart
)

from config.data_sources import EXCEL_URLS


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Dashboard Program Ditsama 2026",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# LOAD CSS
# =========================================================

try:

    with open(
        "assets/style.css",
        "r",
        encoding="utf-8"
    ) as f:

        css = f.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )

except FileNotFoundError:

    st.warning(
        "File assets/style.css tidak ditemukan."
    )


# =========================================================
# HEADER
# =========================================================

st.title(
    "📊 Dashboard Program Ditsama 2026"
)

st.write(
    "Dashboard monitoring program, progress, "
    "financial performance, dan management alert."
)


# =========================================================
# LOAD DATA
# =========================================================

try:

    sheets = load_all_sheets(
        EXCEL_URLS["financial"]
    )

    financial_df = extract_financial_performance(
        sheets
    )

    data_loaded = True

except Exception as e:

    financial_df = pd.DataFrame()

    data_loaded = False

    st.error(
        "Gagal mengambil data Financial Performance."
    )

    st.caption(
        f"Detail error: {e}"
    )


# =========================================================
# SIDEBAR / CONTROL
# =========================================================

st.sidebar.title("CONTROL")


# =========================================================
# PROGRAM FILTER
# =========================================================

if not financial_df.empty:

    program_list = sorted(
        financial_df[
            "Program"
        ]
        .dropna()
        .unique()
        .tolist()
    )

else:

    program_list = []


# =========================================================
# PROGRAM FILTER
# =========================================================

if not financial_df.empty:

    program_list = sorted(
        financial_df[
            "Program"
        ]
        .dropna()
        .unique()
        .tolist()
    )

else:

    program_list = []


# ---------------------------------------------------------
# PROGRAM CHECKBOX DROPDOWN
# ---------------------------------------------------------

with st.sidebar.expander(
    "☑  Pilih Program",
    expanded=False
):

    select_all = st.checkbox(
        "Semua Program",
        value=True,
        key="select_all_program"
    )

    program_filter = []

    for program in program_list:

        selected = st.checkbox(
            program,
            value=select_all,
            key=f"program_{program}"
        )

        if selected:
            program_filter.append(program)


# =========================================================
# BIDANG FILTER
# =========================================================

bidang_filter = st.sidebar.selectbox(
    "Bidang",
    ["Semua Bidang"]
)


# =========================================================
# TAHUN FILTER
# =========================================================

if not financial_df.empty:

    year_list = sorted(
        financial_df[
            "Tahun"
        ]
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


# =========================================================
# REFRESH DATA
# =========================================================

if st.sidebar.button(
    "🔄 Refresh Data"
):

    st.cache_data.clear()

    st.rerun()


# =========================================================
# FILTER DATA
# =========================================================

filtered_df = financial_df.copy()


# ---------------------------------------------------------
# FILTER PROGRAM
# ---------------------------------------------------------

if program_filter != "Semua Program":

    filtered_df = filtered_df[
        filtered_df[
            "Program"
        ]
        == program_filter
    ]


# ---------------------------------------------------------
# FILTER TAHUN
# ---------------------------------------------------------

if tahun_filter != "Semua Tahun":

    filtered_df = filtered_df[
        filtered_df[
            "Tahun"
        ]
        == tahun_filter
    ]


# =========================================================
# KPI
# =========================================================

if not filtered_df.empty:

    total_program = (
        filtered_df[
            "Program"
        ]
        .nunique()
    )

    total_pengajuan = (
        filtered_df[
            "Total Pengajuan"
        ]
        .sum()
    )

    total_saldo = (
        filtered_df[
            "Saldo Terakhir"
        ]
        .sum()
    )

else:

    total_program = 0

    total_pengajuan = 0

    total_saldo = 0


# =========================================================
# KPI DISPLAY
# =========================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Program",
        total_program
    )


with col2:

    st.metric(
        "Total Nilai Pengajuan",
        f"Rp {total_pengajuan:,.0f}"
    )


with col3:

    st.metric(
        "Sisa Saldo",
        f"Rp {total_saldo:,.0f}"
    )


with col4:

    st.metric(
        "Management Alert",
        "0"
    )


# =========================================================
# FINANCIAL PERFORMANCE
# &
# PARTICIPANT TARGET
# =========================================================

col_left, col_right = st.columns(
    [1, 1]
)


# =========================================================
# FINANCIAL PERFORMANCE
# =========================================================

with col_left:

    st.subheader(
        "Financial Performance"
    )

    if not filtered_df.empty:

        financial_chart = (
            create_financial_chart(
                filtered_df
            )
        )

        st.plotly_chart(
            financial_chart,
            use_container_width=True
        )

    else:

        st.info(
            "Belum ada data Financial Performance."
        )


# =========================================================
# PARTICIPANT TARGET
# =========================================================

with col_right:

    st.subheader(
        "Participant Target"
    )

    st.info(
        "Data Participant Target "
        "akan ditampilkan di sini."
    )


# =========================================================
# PROGRAM PROGRESS
# =========================================================

st.subheader(
    "Program Progress"
)

st.info(
    "Grafik Program Progress "
    "akan ditampilkan di sini."
)


# =========================================================
# MANAGEMENT ALERT
# =========================================================

st.subheader(
    "Management Alert"
)

st.info(
    "Management Alert akan muncul "
    "setelah data program terhubung."
)
