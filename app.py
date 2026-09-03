import streamlit as st
import pandas as pd


from src.load_data import (
    load_all_sheets
)


from src.calculations import (
    extract_financial_performance,
    extract_participant_target,
    create_financial_chart,
    create_participant_chart
)


from config.data_sources import (
    EXCEL_URLS
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(

    page_title=
        "Dashboard Program Ditsama 2026",

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
# CACHE LOAD DATA
# =========================================================

@st.cache_data(ttl=300)
def get_financial_data(url):

    sheets = load_all_sheets(url)

    df = extract_financial_performance(
        sheets
    )

    return df


@st.cache_data(ttl=300)
def get_participant_data(url):

    sheets = load_all_sheets(url)

    df = extract_participant_target(
        sheets
    )

    return df


# =========================================================
# LOAD FINANCIAL DATA
# =========================================================

financial_df = pd.DataFrame()


try:

    financial_df = get_financial_data(
        EXCEL_URLS["financial"]
    )

    if financial_df is None:

        financial_df = pd.DataFrame()


except Exception as e:

    st.error(
        "Gagal mengambil data Financial Performance."
    )

    st.caption(
        f"Detail error: {e}"
    )

    financial_df = pd.DataFrame()


# =========================================================
# SAFETY COLUMN FINANCIAL
# =========================================================

required_financial_columns = [

    "Program",
    "Tahun",
    "Bulan",
    "Tanggal",
    "Target",
    "Actual",
    "Percentage",
    "Total Pengajuan",
    "Saldo Terakhir"

]


for column in required_financial_columns:

    if column not in financial_df.columns:

        financial_df[column] = pd.Series(
            dtype="float64"
        )


# Pastikan Program menjadi string
if "Program" in financial_df.columns:

    financial_df["Program"] = (
        financial_df["Program"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# =========================================================
# LOAD PARTICIPANT DATA
# =========================================================

participant_df = pd.DataFrame()


try:

    participant_df = get_participant_data(
        EXCEL_URLS["participant"]
    )

    if participant_df is None:

        participant_df = pd.DataFrame()


except Exception as e:

    st.error(
        "Gagal mengambil data Participant Target & Actual."
    )

    st.caption(
        f"Detail error: {e}"
    )

    participant_df = pd.DataFrame()


# =========================================================
# SAFETY COLUMN PARTICIPANT
# =========================================================

required_participant_columns = [

    "Program",
    "Tahun",
    "Bulan",
    "Tanggal",
    "Target",
    "Actual",
    "Percentage"

]


for column in required_participant_columns:

    if column not in participant_df.columns:

        participant_df[column] = pd.Series(
            dtype="object"
        )


# Pastikan Program menjadi string
if "Program" in participant_df.columns:

    participant_df["Program"] = (
        participant_df["Program"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# =========================================================
# DEBUG STATUS DATA
# =========================================================

with st.expander(
    "🔎 Status Data",
    expanded=False
):

    status_col1, status_col2 = st.columns(2)


    # -----------------------------------------------------
    # FINANCIAL STATUS
    # -----------------------------------------------------

    with status_col1:

        st.markdown(
            "### Financial"
        )

        if financial_df.empty:

            st.warning(
                "Financial data kosong."
            )

        else:

            st.success(
                f"{len(financial_df)} baris berhasil dibaca."
            )

            if "Program" in financial_df.columns:

                financial_programs = (

                    financial_df[
                        "Program"
                    ]
                    .replace("", pd.NA)
                    .dropna()
                    .unique()
                    .tolist()

                )

                st.write(
                    "Program:",
                    ", ".join(
                        sorted(financial_programs)
                    )
                )


            st.caption(
                "Kolom Financial:"
            )

            st.code(
                ", ".join(
                    financial_df.columns.tolist()
                )
            )


    # -----------------------------------------------------
    # PARTICIPANT STATUS
    # -----------------------------------------------------

    with status_col2:

        st.markdown(
            "### Participant"
        )

        if participant_df.empty:

            st.warning(
                "Participant data kosong."
            )

            st.caption(
                "Tidak ada data yang berhasil "
                "dihasilkan oleh extract_participant_target()."
            )

        else:

            st.success(
                f"{len(participant_df)} baris berhasil dibaca."
            )

            if "Program" in participant_df.columns:

                participant_programs = (

                    participant_df[
                        "Program"
                    ]
                    .replace("", pd.NA)
                    .dropna()
                    .unique()
                    .tolist()

                )

                st.write(
                    "Program:",
                    ", ".join(
                        sorted(participant_programs)
                    )
                )


            st.caption(
                "Kolom Participant:"
            )

            st.code(
                ", ".join(
                    participant_df.columns.tolist()
                )
            )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "CONTROL"
)


# =========================================================
# PROGRAM FILTER
# =========================================================

financial_program_list = []
participant_program_list = []


# ---------------------------------------------------------
# PROGRAM FINANCIAL
# ---------------------------------------------------------

if (

    not financial_df.empty

    and

    "Program" in financial_df.columns

):

    financial_program_list = sorted(

        financial_df[
            "Program"
        ]
        .replace("", pd.NA)
        .dropna()
        .astype(str)
        .unique()
        .tolist()

    )


# ---------------------------------------------------------
# PROGRAM PARTICIPANT
# ---------------------------------------------------------

if (

    not participant_df.empty

    and

    "Program" in participant_df.columns

):

    participant_program_list = sorted(

        participant_df[
            "Program"
        ]
        .replace("", pd.NA)
        .dropna()
        .astype(str)
        .unique()
        .tolist()

    )


# ---------------------------------------------------------
# GABUNGKAN PROGRAM
# ---------------------------------------------------------

program_list = sorted(

    set(

        financial_program_list
        +
        participant_program_list

    )

)


# =========================================================
# PROGRAM CHECKBOX
# =========================================================

with st.sidebar.expander(

    "☑  Pilih Program",

    expanded=False

):

    # -----------------------------------------------------
    # INITIAL STATE
    # -----------------------------------------------------

    if (
        "select_all_program"
        not in st.session_state
    ):

        st.session_state[
            "select_all_program"
        ] = True


    # -----------------------------------------------------
    # SEMUA PROGRAM
    # -----------------------------------------------------

    st.checkbox(

        "Semua Program",

        key="select_all_program"

    )


    # -----------------------------------------------------
    # PROGRAM INDIVIDUAL
    # -----------------------------------------------------

    program_filter = []


    for program in program_list:

        key = (
            f"program_{program}"
        )


        if key not in st.session_state:

            st.session_state[key] = True


        selected = st.checkbox(

            program,

            key=key

        )


        if selected:

            program_filter.append(
                program
            )


    # -----------------------------------------------------
    # SEMUA PROGRAM AKTIF
    # -----------------------------------------------------

    if st.session_state[
        "select_all_program"
    ]:

        program_filter = (
            program_list.copy()
        )


# =========================================================
# BIDANG
# =========================================================

bidang_filter = st.sidebar.selectbox(

    "Bidang",

    [
        "Semua Bidang"
    ],

    key="bidang_filter"

)


# =========================================================
# TAHUN
# =========================================================

year_values = []


# ---------------------------------------------------------
# FINANCIAL YEAR
# ---------------------------------------------------------

if (

    not financial_df.empty

    and

    "Tahun" in financial_df.columns

):

    financial_years = (

        pd.to_numeric(

            financial_df[
                "Tahun"
            ],

            errors="coerce"

        )
        .dropna()
        .astype(int)
        .tolist()

    )

    year_values.extend(
        financial_years
    )


# ---------------------------------------------------------
# PARTICIPANT YEAR
# ---------------------------------------------------------

if (

    not participant_df.empty

    and

    "Tahun" in participant_df.columns

):

    participant_years = (

        pd.to_numeric(

            participant_df[
                "Tahun"
            ],

            errors="coerce"

        )
        .dropna()
        .astype(int)
        .tolist()

    )

    year_values.extend(
        participant_years
    )


# ---------------------------------------------------------
# YEAR LIST
# ---------------------------------------------------------

year_list = sorted(
    set(year_values)
)


if not year_list:

    year_list = [2026]


tahun_options = [

    "Semua Tahun"

] + year_list


tahun_filter = st.sidebar.selectbox(

    "Tahun",

    tahun_options,

    key="tahun_filter"

)


# =========================================================
# BULAN MAPPING
# =========================================================

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


bulan_list = list(
    bulan_mapping.keys()
)


# =========================================================
# INITIAL BULAN
# =========================================================

if (
    "bulan_initialized"
    not in st.session_state
):

    st.session_state[
        "bulan_initialized"
    ] = True


    for bulan in bulan_list:

        st.session_state[
            f"bulan_{bulan}"
        ] = True


# =========================================================
# FUNCTION PILIH SEMUA BULAN
# =========================================================

def pilih_semua_bulan():

    nilai = st.session_state[
        "semua_bulan"
    ]


    for bulan in bulan_list:

        st.session_state[
            f"bulan_{bulan}"
        ] = nilai


# =========================================================
# INITIAL SEMUA BULAN
# =========================================================

if (
    "semua_bulan"
    not in st.session_state
):

    st.session_state[
        "semua_bulan"
    ] = True


# =========================================================
# BULAN DROPDOWN
# =========================================================

with st.sidebar.expander(

    "☑  Pilih Bulan",

    expanded=False

):

    st.checkbox(

        "Semua Bulan",

        key="semua_bulan",

        on_change=pilih_semua_bulan

    )


    for bulan in bulan_list:

        st.checkbox(

            bulan,

            key=f"bulan_{bulan}"

        )


# =========================================================
# BULAN TERPILIH
# =========================================================

bulan_filter = [

    bulan

    for bulan in bulan_list

    if st.session_state.get(

        f"bulan_{bulan}",

        False

    )

]


semua_bulan_terpilih = (

    len(bulan_filter)
    ==
    len(bulan_list)

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
# FILTER FINANCIAL
# =========================================================

filtered_financial_df = (
    financial_df.copy()
)


# =========================================================
# FINANCIAL — PROGRAM
# =========================================================

if (

    program_filter

    and

    "Program" in filtered_financial_df.columns

):

    filtered_financial_df = (

        filtered_financial_df[

            filtered_financial_df[
                "Program"
            ].isin(
                program_filter
            )

        ]

    )

else:

    filtered_financial_df = (
        filtered_financial_df.iloc[0:0]
    )


# =========================================================
# FINANCIAL — BIDANG
# =========================================================

if (

    bidang_filter
    !=
    "Semua Bidang"

):

    if "Bidang" in filtered_financial_df.columns:

        filtered_financial_df = (

            filtered_financial_df[

                filtered_financial_df[
                    "Bidang"
                ]
                ==
                bidang_filter

            ]

        )


# =========================================================
# FINANCIAL — TAHUN
# =========================================================

if (

    tahun_filter
    !=
    "Semua Tahun"

):

    if "Tahun" in filtered_financial_df.columns:

        filtered_financial_df = (

            filtered_financial_df[

                pd.to_numeric(

                    filtered_financial_df[
                        "Tahun"
                    ],

                    errors="coerce"

                )
                ==
                int(tahun_filter)

            ]

        )


# =========================================================
# FINANCIAL — BULAN
# =========================================================

if not semua_bulan_terpilih:

    if (

        len(bulan_filter) > 0

        and

        "Bulan" in filtered_financial_df.columns

    ):

        bulan_number = [

            bulan_mapping[
                bulan
            ]

            for bulan
            in bulan_filter

        ]


        filtered_financial_df = (

            filtered_financial_df[

                pd.to_numeric(

                    filtered_financial_df[
                        "Bulan"
                    ],

                    errors="coerce"

                ).isin(
                    bulan_number
                )

            ]

        )

    else:

        filtered_financial_df = (
            filtered_financial_df.iloc[0:0]
        )


# =========================================================
# FILTER PARTICIPANT
# =========================================================

filtered_participant_df = (
    participant_df.copy()
)


# =========================================================
# PARTICIPANT — PROGRAM
# =========================================================

if program_filter:

    filtered_participant_df = (

        filtered_participant_df[

            filtered_participant_df[
                "Program"
            ].isin(
                program_filter
            )

        ]

    )

else:

    filtered_participant_df = (
        filtered_participant_df.iloc[0:0]
    )


# =========================================================
# PARTICIPANT — TAHUN
# =========================================================

if (

    tahun_filter
    !=
    "Semua Tahun"

):

    filtered_participant_df = (

        filtered_participant_df[

            pd.to_numeric(

                filtered_participant_df[
                    "Tahun"
                ],

                errors="coerce"

            )
            ==
            int(tahun_filter)

        ]

    )


# =========================================================
# PARTICIPANT — BULAN
# =========================================================

if not semua_bulan_terpilih:

    if len(bulan_filter) > 0:

        bulan_number = [

            bulan_mapping[
                bulan
            ]

            for bulan
            in bulan_filter

        ]


        filtered_participant_df = (

            filtered_participant_df[

                pd.to_numeric(

                    filtered_participant_df[
                        "Bulan"
                    ],

                    errors="coerce"

                ).isin(
                    bulan_number
                )

            ]

        )

    else:

        filtered_participant_df = (
            filtered_participant_df.iloc[0:0]
        )


# =========================================================
# KPI FINANCIAL
# =========================================================

if not filtered_financial_df.empty:

    # -----------------------------------------------------
    # TOTAL PROGRAM
    # -----------------------------------------------------

    total_program = (

        filtered_financial_df[
            "Program"
        ]
        .nunique()

    )


    # -----------------------------------------------------
    # TOTAL PENGAJUAN
    # -----------------------------------------------------

    total_pengajuan = (

        pd.to_numeric(

            filtered_financial_df[
                "Total Pengajuan"
            ],

            errors="coerce"

        )
        .fillna(0)
        .sum()

    )


    # -----------------------------------------------------
    # TOTAL SALDO
    # -----------------------------------------------------

    total_saldo = (

        pd.to_numeric(

            filtered_financial_df[
                "Saldo Terakhir"
            ],

            errors="coerce"

        )
        .fillna(0)
        .sum()

    )

else:

    total_program = 0

    total_pengajuan = 0

    total_saldo = 0


# =========================================================
# KPI PARTICIPANT
# =========================================================

if not filtered_participant_df.empty:

    participant_kpi_df = (
        filtered_participant_df.copy()
    )


    # -----------------------------------------------------
    # Pastikan Target dan Actual berupa angka
    # -----------------------------------------------------

    participant_kpi_df[
        "Target"
    ] = pd.to_numeric(

        participant_kpi_df[
            "Target"
        ],

        errors="coerce"

    ).fillna(0)


    participant_kpi_df[
        "Actual"
    ] = pd.to_numeric(

        participant_kpi_df[
            "Actual"
        ],

        errors="coerce"

    ).fillna(0)


    # -----------------------------------------------------
    # Pastikan Tahun, Bulan, Tanggal numerik
    # -----------------------------------------------------

    participant_kpi_df[
        "Tahun"
    ] = pd.to_numeric(

        participant_kpi_df[
            "Tahun"
        ],

        errors="coerce"

    )


    participant_kpi_df[
        "Bulan"
    ] = pd.to_numeric(

        participant_kpi_df[
            "Bulan"
        ],

        errors="coerce"

    )


    participant_kpi_df[
        "Tanggal"
    ] = pd.to_numeric(

        participant_kpi_df[
            "Tanggal"
        ],

        errors="coerce"

    )


    # -----------------------------------------------------
    # Urutkan berdasarkan tanggal
    # -----------------------------------------------------

    participant_kpi_df = (
        participant_kpi_df.sort_values(

            [
                "Program",
                "Tahun",
                "Bulan",
                "Tanggal"
            ]

        )
    )


    # -----------------------------------------------------
    # Ambil data TERAKHIR setiap
    # Program + Tahun + Bulan
    # -----------------------------------------------------

    participant_kpi_df = (

        participant_kpi_df

        .groupby(

            [
                "Program",
                "Tahun",
                "Bulan"
            ],

            as_index=False

        )

        .tail(1)

    )


    # -----------------------------------------------------
    # Hitung KPI
    # -----------------------------------------------------

    participant_target = (

        participant_kpi_df[
            "Target"
        ].sum()

    )


    participant_actual = (

        participant_kpi_df[
            "Actual"
        ].sum()

    )

else:

    participant_target = 0

    participant_actual = 0


# =========================================================
# MANAGEMENT ALERT
# =========================================================

management_alert = 0


if not filtered_participant_df.empty:

    participant_check = (
        filtered_participant_df.copy()
    )


    # -----------------------------------------------------
    # Pastikan angka
    # -----------------------------------------------------

    participant_check[
        "Target"
    ] = pd.to_numeric(

        participant_check[
            "Target"
        ],

        errors="coerce"

    ).fillna(0)


    participant_check[
        "Actual"
    ] = pd.to_numeric(

        participant_check[
            "Actual"
        ],

        errors="coerce"

    ).fillna(0)


    participant_check[
        "Tahun"
    ] = pd.to_numeric(

        participant_check[
            "Tahun"
        ],

        errors="coerce"

    )


    participant_check[
        "Bulan"
    ] = pd.to_numeric(

        participant_check[
            "Bulan"
        ],

        errors="coerce"

    )


    participant_check[
        "Tanggal"
    ] = pd.to_numeric(

        participant_check[
            "Tanggal"
        ],

        errors="coerce"

    )


    # -----------------------------------------------------
    # Urutkan
    # -----------------------------------------------------

    participant_check = (
        participant_check.sort_values(

            [
                "Program",
                "Tahun",
                "Bulan",
                "Tanggal"
            ]

        )
    )


    # -----------------------------------------------------
    # Ambil data terakhir setiap bulan
    # -----------------------------------------------------

    participant_check = (

        participant_check

        .groupby(

            [
                "Program",
                "Tahun",
                "Bulan"
            ],

            as_index=False

        )

        .tail(1)

    )


    # -----------------------------------------------------
    # Hitung Management Alert
    # -----------------------------------------------------

    management_alert = (

        (

            participant_check[
                "Actual"
            ]

            <

            participant_check[
                "Target"
            ]

        )

        .sum()

    )


# =========================================================
# KPI DISPLAY
# =========================================================

col1, col2, col3, col4 = st.columns(4)


# =========================================================
# KPI 1
# =========================================================

with col1:

    st.metric(

        "Total Program",

        total_program

    )


# =========================================================
# KPI 2
# =========================================================

with col2:

    st.metric(

        "Total Nilai Pengajuan",

        f"Rp {total_pengajuan:,.0f}"

    )


# =========================================================
# KPI 3
# =========================================================

with col3:

    st.metric(

        "Sisa Saldo",

        f"Rp {total_saldo:,.0f}"

    )


# =========================================================
# KPI 4
# =========================================================

with col4:

    st.metric(

        "Management Alert",

        management_alert

    )


# =========================================================
# PARTICIPANT SUMMARY
# =========================================================

st.markdown("---")


participant_col1, participant_col2, participant_col3 = (

    st.columns(3)

)


# =========================================================
# PARTICIPANT TARGET
# =========================================================

with participant_col1:

    st.metric(

        "Participant Target",

        f"{participant_target:,.0f}"

    )


# =========================================================
# PARTICIPANT ACTUAL
# =========================================================

with participant_col2:

    st.metric(

        "Participant Actual",

        f"{participant_actual:,.0f}"

    )


# =========================================================
# PARTICIPANT ACHIEVEMENT
# =========================================================

with participant_col3:

    if participant_target > 0:

        participant_percentage = (

            participant_actual
            /
            participant_target
            *
            100

        )

    else:

        participant_percentage = 0


    st.metric(

        "Participant Achievement",

        f"{participant_percentage:.1f}%"

    )


# =========================================================
# FINANCIAL + PARTICIPANT
# =========================================================

st.markdown("---")


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


    if not filtered_financial_df.empty:

        try:

            financial_chart = (

                create_financial_chart(

                    filtered_financial_df

                )

            )


            if financial_chart is not None:

                st.plotly_chart(

                    financial_chart,

                    use_container_width=True

                )

            else:

                st.info(
                    "Financial chart tidak dapat dibuat."
                )


        except Exception as e:

            st.error(
                "Gagal membuat Financial Performance chart."
            )

            st.caption(
                f"Detail error: {e}"
            )


    else:

        st.info(

            "Belum ada data Financial "
            "Performance berdasarkan "
            "filter yang dipilih."

        )


# =========================================================
# PARTICIPANT TARGET
# =========================================================

with col_right:

    st.subheader(
        "Participant Target vs Actual"
    )


    if not filtered_participant_df.empty:

        try:

            participant_chart = (

                create_participant_chart(

                    filtered_participant_df

                )

            )


            if participant_chart is not None:

                st.plotly_chart(

                    participant_chart,

                    use_container_width=True

                )

            else:

                st.info(
                    "Participant chart tidak dapat dibuat."
                )


        except Exception as e:

            st.error(
                "Gagal membuat Participant chart."
            )

            st.caption(
                f"Detail error: {e}"
            )


    else:

        st.info(

            "Belum ada data Participant "
            "berdasarkan filter yang dipilih."

        )


# =========================================================
# PROGRAM PROGRESS
# =========================================================

st.markdown("---")


st.subheader(
    "Program Progress"
)


if not filtered_participant_df.empty:

    progress_df = (
        filtered_participant_df.copy()
    )


    # -----------------------------------------------------
    # NUMERIC CONVERSION
    # -----------------------------------------------------

    progress_df[
        "Target"
    ] = pd.to_numeric(

        progress_df[
            "Target"
        ],

        errors="coerce"

    ).fillna(0)


    progress_df[
        "Actual"
    ] = pd.to_numeric(

        progress_df[
            "Actual"
        ],

        errors="coerce"

    ).fillna(0)


    progress_df[
        "Tahun"
    ] = pd.to_numeric(

        progress_df[
            "Tahun"
        ],

        errors="coerce"

    )


    progress_df[
        "Bulan"
    ] = pd.to_numeric(

        progress_df[
            "Bulan"
        ],

        errors="coerce"

    )


    progress_df[
        "Tanggal"
    ] = pd.to_numeric(

        progress_df[
            "Tanggal"
        ],

        errors="coerce"

    )


    # -----------------------------------------------------
    # ACHIEVEMENT
    # -----------------------------------------------------

    progress_df[
        "Achievement"
    ] = 0.0


    mask = (
        progress_df["Target"] > 0
    )


    progress_df.loc[

        mask,

        "Achievement"

    ] = (

        progress_df.loc[
            mask,
            "Actual"
        ]

        /

        progress_df.loc[
            mask,
            "Target"
        ]

        *

        100

    )


    # -----------------------------------------------------
    # Ambil data terakhir tiap bulan
    # -----------------------------------------------------

    progress_df = (
        progress_df.sort_values(

            [
                "Program",
                "Tahun",
                "Bulan",
                "Tanggal"

            ]

        )
    )


    progress_df = (

        progress_df

        .groupby(

            [
                "Program",
                "Tahun",
                "Bulan"

            ],

            as_index=False

        )

        .tail(1)

    )


    # -----------------------------------------------------
    # TABEL PROGRESS
    # -----------------------------------------------------

    display_progress = progress_df[

        [
            "Program",
            "Tahun",
            "Bulan",
            "Tanggal",
            "Target",
            "Actual",
            "Achievement"

        ]

    ].copy()


    # -----------------------------------------------------
    # MONTH NAME
    # -----------------------------------------------------

    display_progress[
        "Bulan"
    ] = display_progress[
        "Bulan"
    ].map(

        {

            1: "Januari",
            2: "Februari",
            3: "Maret",
            4: "April",
            5: "Mei",
            6: "Juni",
            7: "Juli",
            8: "Agustus",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember"

        }

    )


    # -----------------------------------------------------
    # FORMAT ACHIEVEMENT
    # -----------------------------------------------------

    display_progress[
        "Achievement"
    ] = display_progress[
        "Achievement"
    ].map(

        lambda x:
            f"{x:.1f}%"

    )


    st.dataframe(

        display_progress,

        use_container_width=True,

        hide_index=True

    )


else:

    st.info(
        "Belum ada data Program Progress."
    )


# =========================================================
# MANAGEMENT ALERT TABLE
# =========================================================

st.markdown("---")


st.subheader(
    "Management Alert"
)


if not filtered_participant_df.empty:

    alert_df = (
        filtered_participant_df.copy()
    )


    # -----------------------------------------------------
    # NUMERIC CONVERSION
    # -----------------------------------------------------

    alert_df[
        "Target"
    ] = pd.to_numeric(

        alert_df[
            "Target"
        ],

        errors="coerce"

    ).fillna(0)


    alert_df[
        "Actual"
    ] = pd.to_numeric(

        alert_df[
            "Actual"
        ],

        errors="coerce"

    ).fillna(0)


    alert_df[
        "Tahun"
    ] = pd.to_numeric(

        alert_df[
            "Tahun"
        ],

        errors="coerce"

    )


    alert_df[
        "Bulan"
    ] = pd.to_numeric(

        alert_df[
            "Bulan"
        ],

        errors="coerce"

    )


    alert_df[
        "Tanggal"
    ] = pd.to_numeric(

        alert_df[
            "Tanggal"
        ],

        errors="coerce"

    )


    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------

    alert_df = (
        alert_df.sort_values(

            [
                "Program",
                "Tahun",
                "Bulan",
                "Tanggal"

            ]

        )
    )


    # -----------------------------------------------------
    # Ambil data terakhir tiap bulan
    # -----------------------------------------------------

    alert_df = (

        alert_df

        .groupby(

            [
                "Program",
                "Tahun",
                "Bulan"

            ],

            as_index=False

        )

        .tail(1)

    )


    # -----------------------------------------------------
    # Hanya Actual < Target
    # -----------------------------------------------------

    alert_df = alert_df[

        alert_df[
            "Actual"
        ]

        <

        alert_df[
            "Target"
        ]

    ]


    # -----------------------------------------------------
    # HASIL ALERT
    # -----------------------------------------------------

    if not alert_df.empty:

        st.warning(

            f"⚠️ Terdapat {len(alert_df)} "
            "periode yang Actual-nya masih "
            "di bawah Target."

        )


        alert_display = alert_df[

            [
                "Program",
                "Tahun",
                "Bulan",
                "Tanggal",
                "Target",
                "Actual"

            ]

        ].copy()


        # -------------------------------------------------
        # MONTH NAME
        # -------------------------------------------------

        alert_display[
            "Bulan"
        ] = alert_display[
            "Bulan"
        ].map(

            {

                1: "Januari",
                2: "Februari",
                3: "Maret",
                4: "April",
                5: "Mei",
                6: "Juni",
                7: "Juli",
                8: "Agustus",
                9: "September",
                10: "Oktober",
                11: "November",
                12: "Desember"

            }

        )


        st.dataframe(

            alert_display,

            use_container_width=True,

            hide_index=True

        )


    else:

        st.success(

            "✅ Tidak ada Management Alert. "
            "Seluruh data terakhir setiap bulan "
            "sudah mencapai Target."

        )


else:

    st.info(

        "Belum ada data untuk Management Alert."

    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")


st.caption(
    "Dashboard Program Ditsama 2026"
)
