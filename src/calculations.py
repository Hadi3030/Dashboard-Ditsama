# import pandas as pd
# import plotly.graph_objects as go
# import re


# # =========================================================
# # EXTRACT PROGRAM INFO
# # =========================================================

# def extract_program_info(sheet_name):

#     # Pastikan nama sheet menjadi string
#     sheet_name = str(sheet_name)

#     # -----------------------------------------------------
#     # HAPUS HTML DARI NAMA SHEET
#     # -----------------------------------------------------

#     sheet_name = re.sub(
#         r"<[^>]*>",
#         "",
#         sheet_name
#     )

#     # Bersihkan HTML entity
#     sheet_name = (
#         sheet_name
#         .replace("&nbsp;", " ")
#         .replace("&amp;", "&")
#         .strip()
#     )

#     # -----------------------------------------------------
#     # FORMAT:
#     #
#     # DITSAMA.PM-3-6-2026-SIAP
#     #
#     # 3    = tanggal
#     # 6    = bulan
#     # 2026 = tahun
#     # SIAP = program
#     # -----------------------------------------------------

#     pattern = (
#         r"DITSAMA\.PM-"
#         r"(\d+)-"
#         r"(\d+)-"
#         r"(\d{4})-"
#         r"(.+)"
#     )

#     match = re.match(
#         pattern,
#         sheet_name,
#         re.IGNORECASE
#     )

#     if not match:
#         return None

#     tanggal = int(match.group(1))
#     bulan = int(match.group(2))
#     tahun = int(match.group(3))

#     program = match.group(4).strip()

#     # -----------------------------------------------------
#     # BERSIHKAN PROGRAM
#     # -----------------------------------------------------

#     # Hapus semua tag HTML
#     program = re.sub(
#         r"<[^>]+>",
#         "",
#         program
#     )

#     # Hapus potongan HTML yang tidak lengkap
#     program = re.sub(
#         r"</?\s*[a-zA-Z][^>]*",
#         "",
#         program
#     )

#     # Hapus entity HTML
#     program = (
#         program
#         .replace("&nbsp;", " ")
#         .replace("&amp;", "&")
#         .replace("&lt;", "<")
#         .replace("&gt;", ">")
#         .strip()
#     )

#     # -----------------------------------------------------
#     # HANYA AMBIL NAMA PROGRAM SEBELUM HTML
#     # -----------------------------------------------------

#     program = re.split(
#         r"<|&lt;",
#         program
#     )[0].strip()

#     return {
#         "Tanggal": tanggal,
#         "Bulan": bulan,
#         "Tahun": tahun,
#         "Program": program
#     }


# # =========================================================
# # CLEAN NUMBER
# # =========================================================

# def clean_number(value):

#     if pd.isna(value):
#         return 0

#     if isinstance(value, (int, float)):
#         return float(value)

#     value = str(value)

#     value = value.replace(
#         "Rp",
#         ""
#     )

#     value = value.replace(
#         " ",
#         ""
#     )

#     value = value.replace(
#         ".",
#         ""
#     )

#     value = value.replace(
#         ",",
#         "."
#     )

#     try:
#         return float(value)

#     except:
#         return 0


# # =========================================================
# # FINANCIAL PERFORMANCE
# # =========================================================

# def extract_financial_performance(sheets):

#     results = []

#     # =====================================================
#     # PROSES SEMUA SHEET
#     # =====================================================

#     for sheet_name, raw_df in sheets.items():

#         # -------------------------------------------------
#         # Ambil informasi dari nama sheet
#         # -------------------------------------------------

#         info = extract_program_info(
#             sheet_name
#         )

#         if info is None:
#             continue

#         # -------------------------------------------------
#         # Copy dataframe
#         # -------------------------------------------------

#         df = raw_df.copy()

#         # =================================================
#         # CARI BARIS HEADER
#         # =================================================

#         header_row = None

#         for i in range(len(df)):

#             row_text = " ".join(
#                 df.iloc[i]
#                 .fillna("")
#                 .astype(str)
#                 .str.strip()
#                 .tolist()
#             ).lower()

#             if (
#                 "uraian pengajuan" in row_text
#                 and
#                 "nilai pengajuan" in row_text
#                 and
#                 "saldo" in row_text
#             ):

#                 header_row = i
#                 break

#         # -------------------------------------------------
#         # Jika header tidak ditemukan
#         # -------------------------------------------------

#         if header_row is None:
#             continue

#         # =================================================
#         # SET HEADER
#         # =================================================

#         df.columns = (
#             df.iloc[header_row]
#             .fillna("")
#             .astype(str)
#             .str.strip()
#         )

#         # Ambil data setelah header

#         df = df.iloc[
#             header_row + 1:
#         ].copy()

#         # Reset index

#         df.reset_index(
#             drop=True,
#             inplace=True
#         )

#         # =================================================
#         # CARI KOLOM
#         # =================================================

#         uraian_col = None
#         pengajuan_col = None
#         saldo_col = None

#         for col in df.columns:

#             col_clean = (
#                 str(col)
#                 .strip()
#                 .lower()
#             )

#             if (
#                 "uraian pengajuan"
#                 in col_clean
#             ):

#                 uraian_col = col

#             elif (
#                 "nilai pengajuan"
#                 in col_clean
#             ):

#                 pengajuan_col = col

#             elif (
#                 col_clean == "saldo"
#                 or
#                 "saldo" in col_clean
#             ):

#                 saldo_col = col

#         # -------------------------------------------------
#         # Pastikan kolom tersedia
#         # -------------------------------------------------

#         if (
#             uraian_col is None
#             or
#             pengajuan_col is None
#             or
#             saldo_col is None
#         ):

#             continue

#         # =================================================
#         # CARI BARIS NILAI PKS
#         # =================================================

#         target = 0

#         target_index = None

#         pks_mask = (
#             df[uraian_col]
#             .astype(str)
#             .str.strip()
#             .str.contains(
#                 r"nilai\s+pks",
#                 case=False,
#                 na=False,
#                 regex=True
#             )
#         )

#         pks_rows = df[
#             pks_mask
#         ]

#         if not pks_rows.empty:

#             target_index = (
#                 pks_rows.index[0]
#             )

#             # Nilai PKS berada di kolom Saldo
#             target = clean_number(
#                 df.loc[
#                     target_index,
#                     saldo_col
#                 ]
#             )

#             # Jika tidak ditemukan di saldo,
#             # cari angka terbesar pada baris tersebut

#             if target == 0:

#                 for value in (
#                     df.loc[
#                         target_index
#                     ]
#                 ):

#                     number = clean_number(
#                         value
#                     )

#                     if number > target:

#                         target = number

#         # =================================================
#         # CARI BARIS DPKS
#         # =================================================

#         dpks_mask = (
#             df[uraian_col]
#             .astype(str)
#             .str.strip()
#             .str.contains(
#                 r"^dpks$",
#                 case=False,
#                 na=False,
#                 regex=True
#             )
#         )

#         dpks_rows = df[
#             dpks_mask
#         ]

#         # =================================================
#         # TOTAL NILAI PENGAJUAN
#         # =================================================

#         total_pengajuan = 0

#         if not dpks_rows.empty:

#             # Ambil data SETELAH DPKS

#             dpks_index = (
#                 dpks_rows.index[0]
#             )

#             actual_df = df.loc[
#                 dpks_index + 1:
#             ]

#         elif target_index is not None:

#             # Jika DPKS tidak ada,
#             # mulai setelah Nilai PKS

#             actual_df = df.loc[
#                 target_index + 1:
#             ]

#         else:

#             actual_df = df.copy()

#         # -------------------------------------------------
#         # Jumlahkan Nilai Pengajuan
#         # -------------------------------------------------

#         for value in actual_df[
#             pengajuan_col
#         ]:

#             total_pengajuan += (
#                 clean_number(value)
#             )

#         # =================================================
#         # SALDO TERAKHIR
#         # =================================================

#         saldo_terakhir = 0

#         # Ambil seluruh saldo
#         # lalu cari nilai numerik terakhir

#         saldo_values = (
#             df[saldo_col]
#             .apply(clean_number)
#         )

#         saldo_valid = saldo_values[
#             saldo_values != 0
#         ]

#         if not saldo_valid.empty:

#             saldo_terakhir = (
#                 saldo_valid.iloc[-1]
#             )

#         # =================================================
#         # PERSENTASE
#         # =================================================

#         if target > 0:

#             percentage = (
#                 total_pengajuan
#                 /
#                 target
#             ) * 100

#         else:

#             percentage = 0

#         # =================================================
#         # SIMPAN
#         # =================================================

#         results.append({

#             "Program":
#                 info["Program"],

#             "Tanggal":
#                 info["Tanggal"],

#             "Bulan":
#                 info["Bulan"],

#             "Tahun":
#                 info["Tahun"],

#             "Target":
#                 target,

#             "Actual":
#                 total_pengajuan,

#             "Total Pengajuan":
#                 total_pengajuan,

#             "Saldo Terakhir":
#                 saldo_terakhir,

#             "Percentage":
#                 percentage
#         })

#     # =====================================================
#     # BUAT DATAFRAME
#     # =====================================================

#     result_df = pd.DataFrame(
#         results
#     )

#     # =====================================================
#     # BERSIHKAN NAMA PROGRAM
#     # =====================================================

#     if not result_df.empty:

#         result_df["Program"] = (
#             result_df["Program"]
#             .astype(str)

#             # Hapus HTML tag
#             .str.replace(
#                 r"<[^>]*>",
#                 "",
#                 regex=True
#             )

#             # Hapus sisa HTML
#             .str.replace(
#                 r"</?\s*[^>]+>",
#                 "",
#                 regex=True
#             )

#             # Hapus slash di akhir
#             .str.replace(
#                 r"/+$",
#                 "",
#                 regex=True
#             )

#             # Hapus spasi berlebih
#             .str.replace(
#                 r"\s+",
#                 " ",
#                 regex=True
#             )

#             .str.strip()
#         )

#         # Hapus program kosong

#         result_df = result_df[
#             result_df["Program"] != ""
#         ]

#     return result_df

# # =========================================================
# # CREATE FINANCIAL CHART
# # =========================================================

# def create_financial_chart(df):

#     fig = go.Figure()

#     if df.empty:
#         return fig

#     chart_df = df.copy()

#     # Pastikan angka numerik
#     chart_df["Target"] = pd.to_numeric(
#         chart_df["Target"],
#         errors="coerce"
#     ).fillna(0)

#     chart_df["Actual"] = pd.to_numeric(
#         chart_df["Actual"],
#         errors="coerce"
#     ).fillna(0)

#     # =====================================================
#     # TARGET
#     # =====================================================

#     fig.add_trace(
#         go.Bar(
#             x=chart_df["Program"],
#             y=chart_df["Target"],
#             name="Target"
#         )
#     )

#     # =====================================================
#     # ACTUAL
#     # =====================================================

#     fig.add_trace(
#         go.Bar(
#             x=chart_df["Program"],
#             y=chart_df["Actual"],
#             name="Actual"
#         )
#     )

#     # =====================================================
#     # FORMAT SUMBU Y INDONESIA
#     # =====================================================

#     max_value = max(
#         chart_df["Target"].max(),
#         chart_df["Actual"].max()
#     )

#     tick_step = max_value / 5

#     tickvals = [
#         tick_step * i
#         for i in range(6)
#     ]

#     def format_axis(value):

#         if value >= 1_000_000_000:
#             angka = value / 1_000_000_000
#             teks = f"{angka:.1f}".replace(".", ",")
#             return f"Rp{teks} M"
    
#         elif value >= 1_000_000:
#             angka = value / 1_000_000
#             teks = f"{angka:.0f}"
#             return f"Rp{teks} Jt"
    
#         elif value >= 1_000:
#             angka = value / 1_000
#             teks = f"{angka:.0f}"
#             return f"Rp{teks} Rb"
    
#         else:
#             return f"Rp{value:,.0f}".replace(",", ".")
        

#     ticktext = [
#         format_axis(value)
#         for value in tickvals
#     ]

#     # =====================================================
#     # LAYOUT
#     # =====================================================

#     fig.update_layout(
#         barmode="group",
#         height=350,
#         margin=dict(
#             l=20,
#             r=20,
#             t=20,
#             b=80
#         ),
#         xaxis_title="Program",
#         yaxis_title="Nilai",
#         legend_title="Financial Performance"
#     )

#     # =====================================================
#     # TERAPKAN FORMAT SUMBU Y
#     # =====================================================

#     fig.update_yaxes(
#     tickmode="array",
#     tickvals=tickvals,
#     ticktext=ticktext,
#     exponentformat="none",
#     showexponent="none"
#     )

#     return fig

# # =========================================================
# # CREATE FINANCIAL CHART
# # =========================================================

# def create_financial_chart(df):

#     fig = go.Figure()


#     # =====================================================
#     # JIKA DATA KOSONG
#     # =====================================================

#     if df.empty:

#         return fig


#     # =====================================================
#     # COPY DATA
#     # =====================================================

#     chart_df = df.copy()


#     # =====================================================
#     # PASTIKAN TARGET NUMERIK
#     # =====================================================

#     chart_df["Target"] = pd.to_numeric(
#         chart_df["Target"],
#         errors="coerce"
#     ).fillna(0)


#     # =====================================================
#     # PASTIKAN ACTUAL NUMERIK
#     # =====================================================

#     chart_df["Actual"] = pd.to_numeric(
#         chart_df["Actual"],
#         errors="coerce"
#     ).fillna(0)


#     # =====================================================
#     # TARGET
#     # =====================================================

#     fig.add_trace(

#         go.Bar(

#             x=chart_df["Program"],

#             y=chart_df["Target"],

#             name="Target"

#         )

#     )


#     # =====================================================
#     # ACTUAL
#     # =====================================================

#     fig.add_trace(

#         go.Bar(

#             x=chart_df["Program"],

#             y=chart_df["Actual"],

#             name="Actual"

#         )

#     )


#     # =====================================================
#     # CARI NILAI MAKSIMUM
#     # =====================================================

#     max_value = max(

#         chart_df["Target"].max(),

#         chart_df["Actual"].max()

#     )


#     # -----------------------------------------------------
#     # Jika nilai maksimum 0
#     # -----------------------------------------------------

#     if max_value <= 0:

#         max_value = 1


#     # =====================================================
#     # INTERVAL SUMBU Y
#     # =====================================================

#     tick_step = max_value / 5


#     tickvals = [

#         tick_step * i

#         for i in range(6)

#     ]


#     # =====================================================
#     # FORMAT SUMBU Y
#     # =====================================================

#     def format_axis(value):

#         if value >= 1_000_000_000:

#             angka = (
#                 value /
#                 1_000_000_000
#             )

#             teks = (
#                 f"{angka:.1f}"
#                 .replace(".", ",")
#             )

#             return f"Rp{teks} M"


#         elif value >= 1_000_000:

#             angka = (
#                 value /
#                 1_000_000
#             )

#             teks = (
#                 f"{angka:.0f}"
#             )

#             return f"Rp{teks} Jt"


#         elif value >= 1_000:

#             angka = (
#                 value /
#                 1_000
#             )

#             teks = (
#                 f"{angka:.0f}"
#             )

#             return f"Rp{teks} Rb"


#         else:

#             return (
#                 f"Rp{value:,.0f}"
#                 .replace(",", ".")
#             )


#     # =====================================================
#     # LABEL SUMBU Y
#     # =====================================================

#     ticktext = [

#         format_axis(value)

#         for value in tickvals

#     ]


#     # =====================================================
#     # LAYOUT
#     # =====================================================

#     fig.update_layout(

#         barmode="group",

#         height=350,

#         margin=dict(

#             l=20,
#             r=20,
#             t=20,
#             b=80

#         ),

#         xaxis_title="Program",

#         yaxis_title="Nilai",

#         legend_title="Financial Performance"

#     )


#     # =====================================================
#     # FORMAT SUMBU Y
#     # =====================================================

#     fig.update_yaxes(

#         tickmode="array",

#         tickvals=tickvals,

#         ticktext=ticktext,

#         exponentformat="none",

#         showexponent="none"

#     )


#     return fig


# =========================================================
# CALCULATIONS
# Dashboard Program Ditsama 2026
# =========================================================

import re

import pandas as pd
import plotly.graph_objects as go


# =========================================================
# EXTRACT PROGRAM INFO
# =========================================================

def extract_program_info(sheet_name):
    """
    Membaca informasi program dari nama sheet.

    Contoh:
    DITSAMA.PM-3-6-2026-SIAP

    Hasil:
    {
        "Tanggal": 3,
        "Bulan": 6,
        "Tahun": 2026,
        "Program": "SIAP"
    }
    """

    sheet_name = str(sheet_name)


    # -----------------------------------------------------
    # Bersihkan HTML
    # -----------------------------------------------------

    sheet_name = re.sub(
        r"<[^>]*>",
        "",
        sheet_name
    )

    sheet_name = (
        sheet_name
        .replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .strip()
    )


    # -----------------------------------------------------
    # Pattern nama sheet
    # -----------------------------------------------------

    pattern = (
        r"DITSAMA\.PM-"
        r"(\d+)-"
        r"(\d+)-"
        r"(\d{4})-"
        r"(.+)"
    )


    match = re.match(
        pattern,
        sheet_name,
        re.IGNORECASE
    )


    if not match:

        return None


    tanggal = int(
        match.group(1)
    )

    bulan = int(
        match.group(2)
    )

    tahun = int(
        match.group(3)
    )

    program = (
        match.group(4)
        .strip()
    )


    # -----------------------------------------------------
    # Bersihkan program
    # -----------------------------------------------------

    program = re.sub(
        r"<[^>]+>",
        "",
        program
    )

    program = re.sub(
        r"</?\s*[a-zA-Z][^>]*",
        "",
        program
    )

    program = (
        program
        .replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .strip()
    )


    program = re.split(
        r"<|&lt;",
        program
    )[0].strip()


    return {

        "Tanggal": tanggal,

        "Bulan": bulan,

        "Tahun": tahun,

        "Program": program

    }


# =========================================================
# CLEAN NUMBER
# =========================================================

def clean_number(value):
    """
    Mengubah angka/currency Indonesia
    menjadi float.

    Contoh:
    Rp 1.500.000 -> 1500000
    1.500.000    -> 1500000
    1,5          -> 1.5
    """

    if pd.isna(value):

        return 0


    if isinstance(
        value,
        (int, float)
    ):

        return float(value)


    value = str(value)


    value = (
        value
        .replace("Rp", "")
        .replace("rp", "")
        .replace(" ", "")
    )


    # -----------------------------------------------------
    # Format Indonesia
    # -----------------------------------------------------

    value = value.replace(
        ".",
        ""
    )

    value = value.replace(
        ",",
        "."
    )


    try:

        return float(value)

    except:

        return 0


# =========================================================
# FINANCIAL PERFORMANCE
# =========================================================

def extract_financial_performance(sheets):

    results = []


    # =====================================================
    # LOOP SHEET
    # =====================================================

    for sheet_name, raw_df in sheets.items():

        # -------------------------------------------------
        # Ambil informasi program
        # -------------------------------------------------

        info = extract_program_info(
            sheet_name
        )


        if info is None:

            continue


        df = raw_df.copy()


        # =================================================
        # CARI HEADER
        # =================================================

        header_row = None


        for i in range(
            len(df)
        ):

            row_text = " ".join(

                df.iloc[i]
                .fillna("")
                .astype(str)
                .str.strip()
                .tolist()

            ).lower()


            if (
                "uraian pengajuan"
                in row_text

                and

                "nilai pengajuan"
                in row_text

                and

                "saldo"
                in row_text
            ):

                header_row = i

                break


        if header_row is None:

            continue


        # =================================================
        # SET HEADER
        # =================================================

        df.columns = (

            df.iloc[
                header_row
            ]
            .fillna("")
            .astype(str)
            .str.strip()

        )


        df = df.iloc[
            header_row + 1:
        ].copy()


        df.reset_index(
            drop=True,
            inplace=True
        )


        # =================================================
        # CARI KOLOM
        # =================================================

        uraian_col = None

        pengajuan_col = None

        saldo_col = None


        for col in df.columns:

            col_clean = (
                str(col)
                .strip()
                .lower()
            )


            if (
                "uraian pengajuan"
                in col_clean
            ):

                uraian_col = col


            elif (
                "nilai pengajuan"
                in col_clean
            ):

                pengajuan_col = col


            elif (
                col_clean == "saldo"
                or
                "saldo" in col_clean
            ):

                saldo_col = col


        if (
            uraian_col is None
            or
            pengajuan_col is None
            or
            saldo_col is None
        ):

            continue


        # =================================================
        # CARI NILAI PKS
        # =================================================

        target = 0

        target_index = None


        pks_mask = (

            df[uraian_col]
            .astype(str)
            .str.strip()
            .str.contains(
                r"nilai\s+pks",
                case=False,
                na=False,
                regex=True
            )

        )


        pks_rows = df[
            pks_mask
        ]


        if not pks_rows.empty:

            target_index = (
                pks_rows.index[0]
            )


            target = clean_number(

                df.loc[
                    target_index,
                    saldo_col
                ]

            )


            # -------------------------------------------------
            # Jika saldo kosong, cari angka terbesar
            # -------------------------------------------------

            if target == 0:

                for value in (
                    df.loc[
                        target_index
                    ]
                ):

                    number = clean_number(
                        value
                    )


                    if number > target:

                        target = number


        # =================================================
        # CARI DPKS
        # =================================================

        dpks_mask = (

            df[uraian_col]
            .astype(str)
            .str.strip()
            .str.contains(
                r"^dpks$",
                case=False,
                na=False,
                regex=True
            )

        )


        dpks_rows = df[
            dpks_mask
        ]


        # =================================================
        # TENTUKAN DATA ACTUAL
        # =================================================

        if not dpks_rows.empty:

            dpks_index = (
                dpks_rows.index[0]
            )

            actual_df = df.loc[
                dpks_index + 1:
            ]


        elif target_index is not None:

            actual_df = df.loc[
                target_index + 1:
            ]


        else:

            actual_df = df.copy()


        # =================================================
        # TOTAL PENGAJUAN
        # =================================================

        total_pengajuan = 0


        for value in (
            actual_df[
                pengajuan_col
            ]
        ):

            total_pengajuan += (
                clean_number(value)
            )


        # =================================================
        # SALDO TERAKHIR
        # =================================================

        saldo_terakhir = 0


        saldo_values = (

            df[
                saldo_col
            ]
            .apply(clean_number)

        )


        saldo_valid = (
            saldo_values[
                saldo_values != 0
            ]
        )


        if not saldo_valid.empty:

            saldo_terakhir = (
                saldo_valid.iloc[-1]
            )


        # =================================================
        # PERCENTAGE
        # =================================================

        if target > 0:

            percentage = (
                total_pengajuan
                /
                target
            ) * 100

        else:

            percentage = 0


        # =================================================
        # SIMPAN
        # =================================================

        results.append({

            "Program":
                info["Program"],

            "Tanggal":
                info["Tanggal"],

            "Bulan":
                info["Bulan"],

            "Tahun":
                info["Tahun"],

            "Target":
                target,

            "Actual":
                total_pengajuan,

            "Total Pengajuan":
                total_pengajuan,

            "Saldo Terakhir":
                saldo_terakhir,

            "Percentage":
                percentage

        })


    # =====================================================
    # DATAFRAME
    # =====================================================

    result_df = pd.DataFrame(

        results,

        columns=[
            "Program",
            "Tanggal",
            "Bulan",
            "Tahun",
            "Target",
            "Actual",
            "Total Pengajuan",
            "Saldo Terakhir",
            "Percentage"
        ]

    )


    # =====================================================
    # CLEAN PROGRAM
    # =====================================================

    if not result_df.empty:

        result_df["Program"] = (

            result_df["Program"]
            .astype(str)

            .str.replace(
                r"<[^>]*>",
                "",
                regex=True
            )

            .str.replace(
                r"</?\s*[^>]+>",
                "",
                regex=True
            )

            .str.replace(
                r"/+$",
                "",
                regex=True
            )

            .str.replace(
                r"\s+",
                " ",
                regex=True
            )

            .str.strip()

        )


        result_df = result_df[
            result_df["Program"] != ""
        ]


    return result_df


# =========================================================
# PARTICIPANT TARGET & ACTUAL
# =========================================================

def extract_participant_target(sheets):
    """
    Mengambil Participant Target dan Actual
    dari DATA KEDUA.

    Sheet yang diproses:
    - SIAP
    - INSPIRASI

    Struktur:
    A = Tahun
    B = Bulan
    C = Tanggal
    D = Finance Performance
    E = Finance
    F = Participant Target
    G = Participant Actual

    Header berada pada Excel row ke-4.
    Data dimulai dari Excel row ke-5.
    """

    results = []


    # =====================================================
    # PROGRAM YANG DIPROSES
    # =====================================================

    target_programs = [
        "SIAP",
        "INSPIRASI"
    ]


    # =====================================================
    # MAPPING BULAN
    # =====================================================

    month_map = {

        "januari": 1,
        "februari": 2,
        "maret": 3,
        "april": 4,
        "mei": 5,
        "juni": 6,
        "juli": 7,
        "agustus": 8,
        "september": 9,
        "oktober": 10,
        "november": 11,
        "desember": 12

    }


    # =====================================================
    # LOOP SEMUA SHEET
    # =====================================================

    for sheet_name, raw_df in sheets.items():

        # -------------------------------------------------
        # Bersihkan nama sheet
        # -------------------------------------------------

        sheet_clean = re.sub(
            r"<[^>]*>",
            "",
            str(sheet_name)
        ).strip().upper()


        # -------------------------------------------------
        # Cari program
        # -------------------------------------------------

        program = None


        for target_program in target_programs:

            if target_program in sheet_clean:

                program = target_program

                break


        # -------------------------------------------------
        # Bukan SIAP / INSPIRASI
        # -------------------------------------------------

        if program is None:

            continue


        # -------------------------------------------------
        # Copy data
        # -------------------------------------------------

        df = raw_df.copy()


        # -------------------------------------------------
        # Minimal 7 kolom A:G
        # -------------------------------------------------

        if df.shape[1] < 7:

            continue


        # -------------------------------------------------
        # Hanya A:G
        # -------------------------------------------------

        df = df.iloc[
            :,
            :7
        ].copy()


        # =================================================
        # DATA DIMULAI SETELAH HEADER BARIS 4
        # =================================================

        data = df.iloc[
            4:
        ].copy()


        data.reset_index(
            drop=True,
            inplace=True
        )


        # =================================================
        # VARIABLE BULAN / TAHUN
        # =================================================

        current_year = None

        current_month = None


        # =================================================
        # LOOP BARIS
        # =================================================

        for _, row in data.iterrows():

            # -------------------------------------------------
            # TAHUN — KOLOM A
            # -------------------------------------------------

            year_value = row.iloc[0]


            if (
                pd.notna(year_value)
                and
                str(year_value).strip() != ""
            ):

                try:

                    current_year = int(
                        float(year_value)
                    )

                except:

                    pass


            # -------------------------------------------------
            # BULAN — KOLOM B
            # -------------------------------------------------

            month_value = row.iloc[1]


            if (
                pd.notna(month_value)
                and
                str(month_value).strip() != ""
            ):

                month_text = (
                    str(month_value)
                    .strip()
                    .lower()
                )


                if month_text in month_map:

                    current_month = (
                        month_map[
                            month_text
                        ]
                    )

                else:

                    try:

                        current_month = int(
                            float(month_value)
                        )

                    except:

                        pass


            # -------------------------------------------------
            # TANGGAL — KOLOM C
            # -------------------------------------------------

            tanggal = row.iloc[2]


            if (
                pd.isna(tanggal)
                or
                str(tanggal).strip() == ""
            ):

                continue


            try:

                tanggal = int(
                    float(tanggal)
                )

            except:

                continue


            # -------------------------------------------------
            # TARGET — KOLOM F
            # -------------------------------------------------

            target = row.iloc[5]


            # -------------------------------------------------
            # ACTUAL — KOLOM G
            # -------------------------------------------------

            actual = row.iloc[6]


            # -------------------------------------------------
            # Jika dua-duanya kosong
            # -------------------------------------------------

            if (
                pd.isna(target)
                and
                pd.isna(actual)
            ):

                continue


            # -------------------------------------------------
            # Konversi target
            # -------------------------------------------------

            try:

                target = float(target)

            except:

                target = 0


            # -------------------------------------------------
            # Konversi actual
            # -------------------------------------------------

            try:

                actual = float(actual)

            except:

                actual = 0


            # -------------------------------------------------
            # Simpan
            # -------------------------------------------------

            results.append({

                "Program":
                    program,

                "Tahun":
                    current_year,

                "Bulan":
                    current_month,

                "Tanggal":
                    tanggal,

                "Target":
                    target,

                "Actual":
                    actual

            })


    # =====================================================
    # DATAFRAME
    # =====================================================

    participant_df = pd.DataFrame(

        results,

        columns=[
            "Program",
            "Tahun",
            "Bulan",
            "Tanggal",
            "Target",
            "Actual"
        ]

    )


    # =====================================================
    # JIKA KOSONG
    # =====================================================

    if participant_df.empty:

        return participant_df


    # =====================================================
    # KONVERSI NUMERIK
    # =====================================================

    participant_df["Tahun"] = pd.to_numeric(
        participant_df["Tahun"],
        errors="coerce"
    )


    participant_df["Bulan"] = pd.to_numeric(
        participant_df["Bulan"],
        errors="coerce"
    )


    participant_df["Tanggal"] = pd.to_numeric(
        participant_df["Tanggal"],
        errors="coerce"
    )


    participant_df["Target"] = pd.to_numeric(
        participant_df["Target"],
        errors="coerce"
    ).fillna(0)


    participant_df["Actual"] = pd.to_numeric(
        participant_df["Actual"],
        errors="coerce"
    ).fillna(0)


    # =====================================================
    # HANYA DATA TAHUN/BULAN VALID
    # =====================================================

    participant_df = participant_df[
        participant_df["Tahun"].notna()
    ]


    participant_df = participant_df[
        participant_df["Bulan"].notna()
    ]


    # =====================================================
    # SORT
    # =====================================================

    participant_df = participant_df.sort_values(

        [
            "Program",
            "Tahun",
            "Bulan",
            "Tanggal"
        ]

    ).reset_index(
        drop=True
    )


    return participant_df


# =========================================================
# FINANCIAL CHART
# =========================================================

def create_financial_chart(df):

    fig = go.Figure()


    if df.empty:

        return fig


    chart_df = df.copy()


    # =====================================================
    # NUMERIC
    # =====================================================

    chart_df["Target"] = pd.to_numeric(
        chart_df["Target"],
        errors="coerce"
    ).fillna(0)


    chart_df["Actual"] = pd.to_numeric(
        chart_df["Actual"],
        errors="coerce"
    ).fillna(0)


    # =====================================================
    # TARGET
    # =====================================================

    fig.add_trace(

        go.Bar(

            x=chart_df["Program"],

            y=chart_df["Target"],

            name="Target"

        )

    )


    # =====================================================
    # ACTUAL
    # =====================================================

    fig.add_trace(

        go.Bar(

            x=chart_df["Program"],

            y=chart_df["Actual"],

            name="Actual"

        )

    )


    # =====================================================
    # MAX VALUE
    # =====================================================

    max_value = max(

        chart_df["Target"].max(),

        chart_df["Actual"].max()

    )


    if max_value <= 0:

        max_value = 1


    # =====================================================
    # TICK
    # =====================================================

    tick_step = (
        max_value / 5
    )


    tickvals = [

        tick_step * i

        for i in range(6)

    ]


    # =====================================================
    # FORMAT AXIS
    # =====================================================

    def format_axis(value):

        if value >= 1_000_000_000:

            angka = (
                value
                /
                1_000_000_000
            )

            teks = (
                f"{angka:.1f}"
                .replace(".", ",")
            )

            return f"Rp{teks} M"


        elif value >= 1_000_000:

            angka = (
                value
                /
                1_000_000
            )

            return (
                f"Rp{angka:.0f} Jt"
            )


        elif value >= 1_000:

            angka = (
                value
                /
                1_000
            )

            return (
                f"Rp{angka:.0f} Rb"
            )


        else:

            return (
                f"Rp{value:,.0f}"
                .replace(",", ".")
            )


    ticktext = [

        format_axis(value)

        for value in tickvals

    ]


    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        barmode="group",

        height=350,

        margin=dict(

            l=20,
            r=20,
            t=20,
            b=80

        ),

        xaxis_title="Program",

        yaxis_title="Nilai",

        legend_title="Financial Performance"

    )


    fig.update_yaxes(

        tickmode="array",

        tickvals=tickvals,

        ticktext=ticktext,

        exponentformat="none",

        showexponent="none"

    )


    return fig


# =========================================================
# PARTICIPANT CHART
# =========================================================

def create_participant_chart(df):

    fig = go.Figure()


    if df.empty:

        return fig


    chart_df = df.copy()


    # =====================================================
    # NUMERIC
    # =====================================================

    chart_df["Target"] = pd.to_numeric(

        chart_df["Target"],

        errors="coerce"

    ).fillna(0)


    chart_df["Actual"] = pd.to_numeric(

        chart_df["Actual"],

        errors="coerce"

    ).fillna(0)


    chart_df["Bulan"] = pd.to_numeric(

        chart_df["Bulan"],

        errors="coerce"

    )


    chart_df["Tanggal"] = pd.to_numeric(

        chart_df["Tanggal"],

        errors="coerce"

    )


    # =====================================================
    # NAMA BULAN
    # =====================================================

    month_names = {

        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "Mei",
        6: "Jun",
        7: "Jul",
        8: "Agu",
        9: "Sep",
        10: "Okt",
        11: "Nov",
        12: "Des"

    }


    # =====================================================
    # SORT
    # =====================================================

    chart_df = chart_df.sort_values(

        [
            "Program",
            "Tahun",
            "Bulan",
            "Tanggal"
        ]

    )


    # =====================================================
    # AMBIL DATA TERAKHIR
    # DALAM SETIAP BULAN
    # =====================================================

    chart_df = (

        chart_df

        .groupby(

            [
                "Program",
                "Tahun",
                "Bulan"
            ],

            as_index=False

        )

        .last()

    )


    # =====================================================
    # SORT FINAL
    # =====================================================

    chart_df = chart_df.sort_values(

        [
            "Tahun",
            "Bulan",
            "Program"
        ]

    )


    # =====================================================
    # BUAT CHART PER PROGRAM
    # =====================================================

    for program in (

        chart_df[
            "Program"
        ].unique()

    ):

        program_df = chart_df[

            chart_df["Program"]
            == program

        ].copy()


        x_values = [

            month_names.get(

                int(month),

                str(month)

            )

            for month
            in program_df["Bulan"]

        ]


        # =================================================
        # TARGET
        # =================================================

        fig.add_trace(

            go.Scatter(

                x=x_values,

                y=program_df["Target"],

                mode="lines+markers",

                name=f"{program} - Target",

                line=dict(
                    dash="dot"
                ),

                marker=dict(
                    symbol="circle"
                )

            )

        )


        # =================================================
        # ACTUAL
        # =================================================

        fig.add_trace(

            go.Scatter(

                x=x_values,

                y=program_df["Actual"],

                mode="lines+markers",

                name=f"{program} - Actual",

                line=dict(
                    dash="solid"
                ),

                marker=dict(
                    symbol="circle"
                )

            )

        )


    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        height=350,

        margin=dict(

            l=20,
            r=20,
            t=20,
            b=60

        ),

        xaxis_title="Bulan",

        yaxis_title="Jumlah Participant",

        legend_title="Participant",

        hovermode="x unified"

    )


    fig.update_yaxes(
        rangemode="tozero"
    )


    return fig
