import streamlit as st
import pandas as pd

from src.load_data import load_all_data
from src.calculations import calculate_dashboard


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
# FINANCIAL
# ==========================================

st.subheader("Financial Performance")

st.info(
    "Data financial performance akan "
    "dihubungkan setelah sumber Excel selesai dibuat."
)


# ==========================================
# PROGRAM PROGRESS
# ==========================================

st.subheader("Program Progress")

st.info(
    "Data progress program akan "
    "dihubungkan setelah sumber Excel selesai dibuat."
)


# ==========================================
# MANAGEMENT ALERT
# ==========================================

st.subheader("Management Alert")

st.info(
    "Management alert akan "
    "muncul setelah data program terhubung."
)
