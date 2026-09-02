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


import pandas as pd
import plotly.graph_objects as go
import re


# =========================================================
# EXTRACT PROGRAM INFO
# =========================================================

def extract_program_info(sheet_name):

    # Pastikan nama sheet menjadi string
    sheet_name = str(sheet_name)

    # -----------------------------------------------------
    # HAPUS HTML DARI NAMA SHEET
    # -----------------------------------------------------

    sheet_name = re.sub(
        r"<[^>]*>",
        "",
        sheet_name
    )

    # Bersihkan HTML entity
    sheet_name = (
        sheet_name
        .replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .strip()
    )

    # -----------------------------------------------------
    # FORMAT:
    #
    # DITSAMA.PM-3-6-2026-SIAP
    #
    # 3    = tanggal
    # 6    = bulan
    # 2026 = tahun
    # SIAP = program
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

    program = match.group(4).strip()


    # -----------------------------------------------------
    # BERSIHKAN PROGRAM
    # -----------------------------------------------------

    # Hapus semua tag HTML
    program = re.sub(
        r"<[^>]+>",
        "",
        program
    )

    # Hapus potongan HTML yang tidak lengkap
    program = re.sub(
        r"</?\s*[a-zA-Z][^>]*",
        "",
        program
    )

    # Hapus entity HTML
    program = (
        program
        .replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .strip()
    )

    # -----------------------------------------------------
    # HANYA AMBIL NAMA PROGRAM SEBELUM HTML
    # -----------------------------------------------------

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

    if pd.isna(value):

        return 0

    if isinstance(
        value,
        (int, float)
    ):

        return float(value)

    value = str(value)

    value = value.replace(
        "Rp",
        ""
    )

    value = value.replace(
        " ",
        ""
    )

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
    # PROSES SEMUA SHEET
    # =====================================================

    for sheet_name, raw_df in sheets.items():

        # -------------------------------------------------
        # Ambil informasi dari nama sheet
        # -------------------------------------------------

        info = extract_program_info(
            sheet_name
        )

        if info is None:

            continue


        # -------------------------------------------------
        # Copy dataframe
        # -------------------------------------------------

        df = raw_df.copy()


        # =================================================
        # CARI BARIS HEADER
        # =================================================

        header_row = None


        for i in range(len(df)):

            row_text = " ".join(

                df.iloc[i]
                .fillna("")
                .astype(str)
                .str.strip()
                .tolist()

            ).lower()


            if (
                "uraian pengajuan" in row_text
                and
                "nilai pengajuan" in row_text
                and
                "saldo" in row_text
            ):

                header_row = i

                break


        # -------------------------------------------------
        # Jika header tidak ditemukan
        # -------------------------------------------------

        if header_row is None:

            continue


        # =================================================
        # SET HEADER
        # =================================================

        df.columns = (

            df.iloc[header_row]
            .fillna("")
            .astype(str)
            .str.strip()

        )


        # Ambil data setelah header

        df = df.iloc[
            header_row + 1:
        ].copy()


        # Reset index

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


        # -------------------------------------------------
        # Pastikan kolom tersedia
        # -------------------------------------------------

        if (
            uraian_col is None
            or
            pengajuan_col is None
            or
            saldo_col is None
        ):

            continue


        # =================================================
        # CARI BARIS NILAI PKS
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


            # Nilai PKS berada di kolom Saldo

            target = clean_number(

                df.loc[
                    target_index,
                    saldo_col
                ]

            )


            # Jika tidak ditemukan di saldo,
            # cari angka terbesar pada baris tersebut

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
        # CARI BARIS DPKS
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
        # TOTAL NILAI PENGAJUAN
        # =================================================

        total_pengajuan = 0


        if not dpks_rows.empty:

            # Ambil data SETELAH DPKS

            dpks_index = (
                dpks_rows.index[0]
            )


            actual_df = df.loc[
                dpks_index + 1:
            ]


        elif target_index is not None:

            # Jika DPKS tidak ada,
            # mulai setelah Nilai PKS

            actual_df = df.loc[
                target_index + 1:
            ]


        else:

            actual_df = df.copy()


        # -------------------------------------------------
        # Jumlahkan Nilai Pengajuan
        # -------------------------------------------------

        for value in actual_df[
            pengajuan_col
        ]:

            total_pengajuan += (
                clean_number(value)
            )


        # =================================================
        # SALDO TERAKHIR
        # =================================================

        saldo_terakhir = 0


        # Ambil seluruh saldo
        # lalu cari nilai numerik terakhir

        saldo_values = (
            df[saldo_col]
            .apply(clean_number)
        )


        saldo_valid = saldo_values[
            saldo_values != 0
        ]


        if not saldo_valid.empty:

            saldo_terakhir = (
                saldo_valid.iloc[-1]
            )


        # =================================================
        # PERSENTASE
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
    # BUAT DATAFRAME
    # =====================================================

    result_df = pd.DataFrame(
        results
    )


    # =====================================================
    # BERSIHKAN NAMA PROGRAM
    # =====================================================

    if not result_df.empty:

        result_df["Program"] = (

            result_df["Program"]
            .astype(str)

            # Hapus HTML tag
            .str.replace(
                r"<[^>]*>",
                "",
                regex=True
            )

            # Hapus sisa HTML
            .str.replace(
                r"</?\s*[^>]+>",
                "",
                regex=True
            )

            # Hapus slash di akhir
            .str.replace(
                r"/+$",
                "",
                regex=True
            )

            # Hapus spasi berlebih
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )

            .str.strip()

        )


        # Hapus program kosong

        result_df = result_df[
            result_df["Program"] != ""
        ]


    return result_df


# =========================================================
# PARTICIPANT TARGET & ACTUAL
# =========================================================

def extract_participant_target(sheets):

    """
    Mengambil data Participant Target dan Actual
    dari sheet SIAP dan INSPIRASI.

    Struktur Excel:

    Kolom A = Tahun
    Kolom B = Bulan
    Kolom C = Tanggal
    Kolom D = Finance Performance
    Kolom E = Finance
    Kolom F = Participant Target
    Kolom G = Participant Actual

    Header berada pada baris ke-4 Excel.
    """

    results = []


    # =====================================================
    # PROGRAM YANG DIBACA
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
    # PROSES SETIAP SHEET
    # =====================================================

    for sheet_name, raw_df in sheets.items():

        # Nama sheet
        program = str(
            sheet_name
        ).strip().upper()


        # -------------------------------------------------
        # Hanya baca SIAP dan INSPIRASI
        # -------------------------------------------------

        if program not in target_programs:

            continue


        # -------------------------------------------------
        # Copy dataframe
        # -------------------------------------------------

        df = raw_df.copy()


        # -------------------------------------------------
        # Pastikan minimal 7 kolom
        # -------------------------------------------------

        if df.shape[1] < 7:

            continue


        # -------------------------------------------------
        # Ambil kolom A sampai G
        # -------------------------------------------------

        df = df.iloc[
            :,
            :7
        ].copy()


        # =================================================
        # HEADER BARIS KE-4
        # =================================================
        #
        # Excel:
        # baris 1 -> index 0
        # baris 2 -> index 1
        # baris 3 -> index 2
        # baris 4 -> index 3
        #
        # Data dimulai setelah baris 4
        # =================================================

        data = df.iloc[
            4:
        ].copy()


        data.reset_index(
            drop=True,
            inplace=True
        )


        # =================================================
        # VARIABEL UNTUK FORWARD FILL
        # =================================================

        current_year = None

        current_month = None


        # =================================================
        # BACA BARIS DATA
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


                # Jika bulan berupa nama

                if month_text in month_map:

                    current_month = (
                        month_map[month_text]
                    )


                else:

                    # Jika bulan berupa angka

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
            # PARTICIPANT TARGET — KOLOM F
            # -------------------------------------------------

            target = row.iloc[5]


            # -------------------------------------------------
            # PARTICIPANT ACTUAL — KOLOM G
            # -------------------------------------------------

            actual = row.iloc[6]


            # -------------------------------------------------
            # Jika Target dan Actual kosong
            # -------------------------------------------------

            if (
                pd.isna(target)
                and
                pd.isna(actual)
            ):

                continue


            # =================================================
            # KONVERSI TARGET
            # =================================================

            try:

                target = float(target)

            except:

                target = 0


            # =================================================
            # KONVERSI ACTUAL
            # =================================================

            try:

                actual = float(actual)

            except:

                actual = 0


            # =================================================
            # SIMPAN DATA
            # =================================================

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
    # BUAT DATAFRAME
    # =====================================================

    participant_df = pd.DataFrame(
        results
    )


    # =====================================================
    # JIKA KOSONG
    # =====================================================

    if participant_df.empty:

        return participant_df


    # =====================================================
    # PASTIKAN TIPE DATA
    # =====================================================

    participant_df["Tahun"] = (
        pd.to_numeric(
            participant_df["Tahun"],
            errors="coerce"
        )
    )


    participant_df["Bulan"] = (
        pd.to_numeric(
            participant_df["Bulan"],
            errors="coerce"
        )
    )


    participant_df["Tanggal"] = (
        pd.to_numeric(
            participant_df["Tanggal"],
            errors="coerce"
        )
    )


    participant_df["Target"] = (
        pd.to_numeric(
            participant_df["Target"],
            errors="coerce"
        )
        .fillna(0)
    )


    participant_df["Actual"] = (
        pd.to_numeric(
            participant_df["Actual"],
            errors="coerce"
        )
        .fillna(0)
    )


    # =====================================================
    # HAPUS DATA TANPA BULAN
    # =====================================================

    participant_df = participant_df[
        participant_df["Bulan"].notna()
    ]


    # =====================================================
    # HAPUS DATA TANPA TAHUN
    # =====================================================

    participant_df = participant_df[
        participant_df["Tahun"].notna()
    ]


    return participant_df


# =========================================================
# CREATE FINANCIAL CHART
# =========================================================

def create_financial_chart(df):

    fig = go.Figure()


    # =====================================================
    # JIKA DATA KOSONG
    # =====================================================

    if df.empty:

        return fig


    # =====================================================
    # COPY DATA
    # =====================================================

    chart_df = df.copy()


    # =====================================================
    # PASTIKAN TARGET NUMERIK
    # =====================================================

    chart_df["Target"] = pd.to_numeric(

        chart_df["Target"],

        errors="coerce"

    ).fillna(0)


    # =====================================================
    # PASTIKAN ACTUAL NUMERIK
    # =====================================================

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
    # CARI NILAI MAKSIMUM
    # =====================================================

    max_value = max(

        chart_df["Target"].max(),

        chart_df["Actual"].max()

    )


    if max_value <= 0:

        max_value = 1


    # =====================================================
    # INTERVAL SUMBU Y
    # =====================================================

    tick_step = max_value / 5


    tickvals = [

        tick_step * i

        for i in range(6)

    ]


    # =====================================================
    # FORMAT SUMBU Y
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
                .replace(
                    ".",
                    ","
                )
            )

            return f"Rp{teks} M"


        elif value >= 1_000_000:

            angka = (
                value
                /
                1_000_000
            )

            teks = (
                f"{angka:.0f}"
            )

            return f"Rp{teks} Jt"


        elif value >= 1_000:

            angka = (
                value
                /
                1_000
            )

            teks = (
                f"{angka:.0f}"
            )

            return f"Rp{teks} Rb"


        else:

            return (
                f"Rp{value:,.0f}"
                .replace(
                    ",",
                    "."
                )
            )


    # =====================================================
    # LABEL SUMBU Y
    # =====================================================

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


    # =====================================================
    # FORMAT SUMBU Y
    # =====================================================

    fig.update_yaxes(

        tickmode="array",

        tickvals=tickvals,

        ticktext=ticktext,

        exponentformat="none",

        showexponent="none"

    )


    return fig


# =========================================================
# CREATE PARTICIPANT CHART
# =========================================================

def create_participant_chart(df):

    """
    Membuat grafik Participant Target vs Actual.

    Target:
        Garis titik-titik

    Actual:
        Garis penuh

    Jika terdapat dua program:
        SIAP
        INSPIRASI

    maka masing-masing program memiliki:
        Target
        Actual
    """

    fig = go.Figure()


    # =====================================================
    # JIKA DATA KOSONG
    # =====================================================

    if df.empty:

        return fig


    # =====================================================
    # COPY DATA
    # =====================================================

    chart_df = df.copy()


    # =====================================================
    # PASTIKAN DATA NUMERIK
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
    # MAPPING NAMA BULAN
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
    # URUTKAN DATA
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
    # AMBIL DATA TERAKHIR SETIAP BULAN
    # =====================================================
    #
    # Contoh:
    #
    # September:
    # tanggal 5  -> Target 10 / Actual 20
    # tanggal 17 -> Target 15 / Actual 20
    # tanggal 27 -> Target 20 / Actual 11
    #
    # Grafik akan mengambil tanggal 27
    # sebagai kondisi terakhir September.
    #
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
    # URUTKAN KEMBALI
    # =====================================================

    chart_df = chart_df.sort_values(

        [
            "Tahun",
            "Bulan",
            "Program"
        ]

    )


    # =====================================================
    # BUAT GRAFIK
    # =====================================================

    for program in chart_df[
        "Program"
    ].unique():

        program_df = chart_df[
            chart_df["Program"]
            == program
        ].copy()


        # -------------------------------------------------
        # X AXIS
        # -------------------------------------------------

        x_values = [

            month_names.get(

                int(month),

                str(month)

            )

            for month in program_df[
                "Bulan"
            ]

        ]


        # =================================================
        # TARGET
        # =================================================
        #
        # Garis titik-titik
        # =================================================

        fig.add_trace(

            go.Scatter(

                x=x_values,

                y=program_df[
                    "Target"
                ],

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
        #
        # Garis penuh
        # =================================================

        fig.add_trace(

            go.Scatter(

                x=x_values,

                y=program_df[
                    "Actual"
                ],

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

            b=50

        ),

        xaxis_title="Bulan",

        yaxis_title="Jumlah Participant",

        legend_title="Participant",

        hovermode="x unified"

    )


    # =====================================================
    # SUMBU Y
    # =====================================================

    fig.update_yaxes(

        rangemode="tozero"

    )


    return fig
