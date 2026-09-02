import streamlit as st
import pandas as pd

from src.load_data import load_all_sheets

from src.calculations import (
    extract_financial_performance,
    create_financial_chart
)

from config.data_sources import EXCEL_URLS


# =========================================================
# PAGE CONFIGURATION
# =========================================================
# Pengaturan dasar halaman dashboard.

st.set_page_config(
    page_title="Dashboard Program Ditsama 2026",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# LOAD CSS
# =========================================================
# Mengambil file CSS dari:
# assets/style.css

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
# Mengambil data dari Excel.

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
# PREPARE DATE DATA
# =========================================================
# Bagian ini mengubah kolom:
#
# "Tanggal Pengajuan"
#
# menjadi datetime.
#
# Kita buat khusus untuk nama bulan Bahasa Indonesia.
#
# Contoh:
#
# 19 Juli
# 5 Agustus
# 10 September 2026
#
# semuanya akan dapat dibaca oleh Pandas.


if (
    not financial_df.empty
    and "Tanggal Pengajuan" in financial_df.columns
):

    # -----------------------------------------------------
    # MAPPING BULAN INDONESIA KE INGGRIS
    # -----------------------------------------------------

    bulan_id_to_en = {

        "Januari": "January",
        "Februari": "February",
        "Maret": "March",
        "April": "April",
        "Mei": "May",
        "Juni": "June",
        "Juli": "July",
        "Agustus": "August",
        "September": "September",
        "Oktober": "October",
        "November": "November",
        "Desember": "December"

    }


    # -----------------------------------------------------
    # BERSIHKAN DATA TANGGAL
    # -----------------------------------------------------

    financial_df["Tanggal Pengajuan"] = (
        financial_df["Tanggal Pengajuan"]
        .astype(str)
        .str.strip()
    )


    # -----------------------------------------------------
    # UBAH NAMA BULAN INDONESIA
    # MENJADI BAHASA INGGRIS
    # -----------------------------------------------------

    for bulan_id, bulan_en in bulan_id_to_en.items():

        financial_df["Tanggal Pengajuan"] = (
            financial_df["Tanggal Pengajuan"]
            .str.replace(
                bulan_id,
                bulan_en,
                case=False,
                regex=False
            )
        )


    # -----------------------------------------------------
    # KONVERSI MENJADI DATETIME
    # -----------------------------------------------------

    financial_df["Tanggal Pengajuan"] = pd.to_datetime(
        financial_df["Tanggal Pengajuan"],
        errors="coerce",
        dayfirst=True
    )


# =========================================================
# SIDEBAR / CONTROL
# =========================================================

st.sidebar.title("CONTROL")


# =========================================================
# 1. PROGRAM FILTER
# =========================================================
# Mengambil semua nama program dari data.

if (
    not financial_df.empty
    and "Program" in financial_df.columns
):

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
# PROGRAM CHECKBOX DROPDOWN
# =========================================================
# Program disimpan di dalam expander.
#
# Ketika tertutup:
#
# ☑ Pilih Program
#
# Ketika diklik:
#
# Semua Program
# ☑ OSN
# ☑ OPSI
# ☑ Riset
# dst.


with st.sidebar.expander(
    "☑  Pilih Program",
    expanded=False
):

    # -----------------------------------------------------
    # SEMUA PROGRAM
    # -----------------------------------------------------

    select_all = st.checkbox(
        "Semua Program",
        value=True,
        key="select_all_program"
    )


    # -----------------------------------------------------
    # LIST PROGRAM TERPILIH
    # -----------------------------------------------------

    program_filter = []


    for program in program_list:

        selected = st.checkbox(
            program,
            value=select_all,
            key=f"program_{program}"
        )

        if selected:

            program_filter.append(
                program
            )


# =========================================================
# 2. BIDANG FILTER
# =========================================================

bidang_filter = st.sidebar.selectbox(
    "Bidang",
    ["Semua Bidang"],
    key="bidang_filter"
)


# =========================================================
# 3. TAHUN FILTER
# =========================================================
# Mengambil tahun dari kolom "Tahun".

if (
    not financial_df.empty
    and "Tahun" in financial_df.columns
):

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
    year_options,
    key="tahun_filter"
)


# =========================================================
# 4. BULAN FILTER
# =========================================================
# Bulan diambil dari:
#
# "Tanggal Pengajuan"
#
# Jadi tidak perlu ada kolom "Bulan" di Excel.


bulan_mapping = {

    "Januari": 1,
    "Februari": 2,
    "Maret": 3,
    "April": 4,
    "Mei": 5,
    "Juni": 6,
    "Juli": 7,
    "Agustus": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Desember": 12

}


bulan_options = [
    "Semua Bulan"
] + list(
    bulan_mapping.keys()
)


bulan_filter = st.sidebar.selectbox(
    "Bulan",
    bulan_options,
    key="bulan_filter"
)


# =========================================================
# 5. REFRESH DATA
# =========================================================

if st.sidebar.button(
    "🔄 Refresh Data"
):

    st.cache_data.clear()

    st.rerun()


# =========================================================
# FILTER DATA
# =========================================================
# Mulai dari seluruh data.

filtered_df = financial_df.copy()


# =========================================================
# FILTER 1 — PROGRAM
# =========================================================

if program_filter:

    filtered_df = filtered_df[
        filtered_df[
            "Program"
        ].isin(
            program_filter
        )
    ]

else:

    # Jika tidak ada program yang dipilih,
    # dataframe menjadi kosong.

    filtered_df = filtered_df.iloc[0:0]


# =========================================================
# FILTER 2 — BIDANG
# =========================================================
# Saat ini belum diterapkan karena data Bidang
# belum tersedia sebagai filter.
#
# Nanti bisa dikembangkan jika kolom Bidang
# sudah tersedia.


if bidang_filter != "Semua Bidang":

    if "Bidang" in filtered_df.columns:

        filtered_df = filtered_df[
            filtered_df["Bidang"]
            == bidang_filter
        ]


# =========================================================
# FILTER 3 — TAHUN
# =========================================================

if tahun_filter != "Semua Tahun":

    filtered_df = filtered_df[
        filtered_df[
            "Tahun"
        ] == tahun_filter
    ]


# =========================================================
# FILTER 4 — BULAN
# =========================================================
# Filter bulan berdasarkan:
#
# filtered_df["Tanggal Pengajuan"].dt.month
#
# Contoh:
#
# Juli -> 7
# Agustus -> 8


if (
    bulan_filter != "Semua Bulan"
    and "Tanggal Pengajuan" in filtered_df.columns
):

    bulan_number = bulan_mapping[
        bulan_filter
    ]


    filtered_df = filtered_df[
        filtered_df[
            "Tanggal Pengajuan"
        ].dt.month == bulan_number
    ]


# =========================================================
# KPI CALCULATION
# =========================================================

if not filtered_df.empty:

    # -----------------------------------------------------
    # TOTAL PROGRAM
    # -----------------------------------------------------

    total_program = (
        filtered_df[
            "Program"
        ]
        .nunique()
    )


    # -----------------------------------------------------
    # TOTAL NILAI PENGAJUAN
    # -----------------------------------------------------

    total_pengajuan = (
        filtered_df[
            "Total Pengajuan"
        ]
        .sum()
    )


    # -----------------------------------------------------
    # TOTAL SISA SALDO
    # -----------------------------------------------------

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


# ---------------------------------------------------------
# KPI 1
# ---------------------------------------------------------

with col1:

    st.metric(
        "Total Program",
        total_program
    )


# ---------------------------------------------------------
# KPI 2
# ---------------------------------------------------------

with col2:

    st.metric(
        "Total Nilai Pengajuan",
        f"Rp {total_pengajuan:,.0f}"
    )


# ---------------------------------------------------------
# KPI 3
# ---------------------------------------------------------

with col3:

    st.metric(
        "Sisa Saldo",
        f"Rp {total_saldo:,.0f}"
    )


# ---------------------------------------------------------
# KPI 4
# ---------------------------------------------------------

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

        # -------------------------------------------------
        # PENTING:
        #
        # Grafik HARUS menggunakan filtered_df,
        # bukan financial_df.
        #
        # Dengan demikian ketika Program / Tahun /
        # Bulan berubah, grafik ikut berubah.
        # -------------------------------------------------

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
            "Belum ada data Financial Performance "
            "berdasarkan filter yang dipilih."
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
