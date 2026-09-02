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
# Pengaturan dasar halaman dashboard

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
# Judul utama dashboard

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
# Mengambil data dari sumber Excel
# yang sudah didefinisikan di config.data_sources

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
# menjadi format tanggal yang dapat dibaca Pandas.
#
# Contoh:
# 19 Juli 2026
# akan dikenali sebagai tanggal.
#
# Filter BULAN nantinya mengambil informasi
# bulan langsung dari kolom ini.

if (
    not financial_df.empty
    and "Tanggal Pengajuan" in financial_df.columns
):

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
# Mengambil daftar program yang tersedia
# dari kolom "Program".

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


# ---------------------------------------------------------
# PROGRAM CHECKBOX DROPDOWN
# ---------------------------------------------------------
# Daftar program disembunyikan di dalam expander.
#
# Jadi sidebar tidak langsung penuh dengan
# daftar OSN, OPSI, Riset, dan sebagainya.
#
# User cukup klik "Pilih Program" untuk
# membuka daftar checkbox.

with st.sidebar.expander(
    "☑  Pilih Program",
    expanded=False
):

    # -----------------------------------------------------
    # PILIH SEMUA PROGRAM
    # -----------------------------------------------------
    # Jika dicentang, semua program akan dipilih.

    select_all = st.checkbox(
        "Semua Program",
        value=True,
        key="select_all_program"
    )


    # -----------------------------------------------------
    # DAFTAR PROGRAM
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
# Untuk sementara pilihan Bidang masih "Semua Bidang".
#
# Nanti kalau data sudah memiliki kolom Bidang,
# bagian ini bisa dikembangkan menjadi filter
# seperti Program.

bidang_filter = st.sidebar.selectbox(
    "Bidang",
    ["Semua Bidang"]
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
    year_options
)


# =========================================================
# 4. BULAN FILTER
# =========================================================
# Bulan TIDAK perlu dibuat sebagai kolom baru
# di Excel.
#
# Bulan diambil langsung dari:
#
# "Tanggal Pengajuan"
#
# Contoh:
# 19 Juli 2026 -> Juli
# 5 Agustus 2026 -> Agustus

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
    bulan_options
)


# =========================================================
# 5. REFRESH DATA
# =========================================================
# Tombol untuk mengambil data terbaru.

if st.sidebar.button(
    "🔄 Refresh Data"
):

    st.cache_data.clear()

    st.rerun()


# =========================================================
# FILTER DATA
# =========================================================
# Membuat salinan data awal.
#
# Semua filter Program, Tahun, dan Bulan
# akan diterapkan ke dataframe ini.

filtered_df = financial_df.copy()


# =========================================================
# FILTER 1 — PROGRAM
# =========================================================
# Karena Program menggunakan checkbox,
# program_filter berbentuk LIST.
#
# Contoh:
#
# ["OSN", "OPSI", "Riset"]
#
# .isin() digunakan untuk mengambil
# beberapa program sekaligus.

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
    # tampilkan dataframe kosong.

    filtered_df = filtered_df.iloc[0:0]


# =========================================================
# FILTER 2 — TAHUN
# =========================================================
# Filter tahun hanya dilakukan jika user
# tidak memilih "Semua Tahun".

if tahun_filter != "Semua Tahun":

    filtered_df = filtered_df[
        filtered_df[
            "Tahun"
        ] == tahun_filter
    ]


# =========================================================
# FILTER 3 — BULAN
# =========================================================
# Mengambil nomor bulan dari pilihan user.
#
# Contoh:
#
# Juli -> 7
# Agustus -> 8
#
# Kemudian membandingkannya dengan bulan
# pada "Tanggal Pengajuan".

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
# Menghitung nilai KPI berdasarkan data
# yang sudah difilter.

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
# Menampilkan 4 KPI utama.

col1, col2, col3, col4 = st.columns(4)


# ---------------------------------------------------------
# KPI 1 — TOTAL PROGRAM
# ---------------------------------------------------------

with col1:

    st.metric(
        "Total Program",
        total_program
    )


# ---------------------------------------------------------
# KPI 2 — TOTAL NILAI PENGAJUAN
# ---------------------------------------------------------

with col2:

    st.metric(
        "Total Nilai Pengajuan",
        f"Rp {total_pengajuan:,.0f}"
    )


# ---------------------------------------------------------
# KPI 3 — SISA SALDO
# ---------------------------------------------------------

with col3:

    st.metric(
        "Sisa Saldo",
        f"Rp {total_saldo:,.0f}"
    )


# ---------------------------------------------------------
# KPI 4 — MANAGEMENT ALERT
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
