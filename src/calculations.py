# import re
# import pandas as pd
# import plotly.express as px


# # =========================================================
# # 1. EXTRACT PROGRAM INFO DARI NAMA SHEET FINANCIAL
# # =========================================================

# def extract_program_info(sheet_name):
#     """
#     Contoh nama sheet:
#     DITSAMA.PM-3-6-2026-SIAP

#     Hasil:
#     Program = SIAP
#     Tanggal = 3
#     Bulan = 6
#     Tahun = 2026
#     """

#     sheet_name = str(sheet_name).strip()

#     pattern = r"PM-(\d{1,2})-(\d{1,2})-(\d{4})-(.+)"

#     match = re.search(pattern, sheet_name)

#     if not match:
#         return None

#     tanggal = int(match.group(1))
#     bulan = int(match.group(2))
#     tahun = int(match.group(3))
#     program = match.group(4).strip()

#     return {
#         "Program": program,
#         "Tanggal": tanggal,
#         "Bulan": bulan,
#         "Tahun": tahun
#     }


# # =========================================================
# # 2. CLEAN NUMBER UNTUK DATA FINANCIAL
# # =========================================================

# def clean_number(value):
#     """
#     Membersihkan angka financial.

#     Contoh:
#     Rp 10.000.000 -> 10000000
#     10.000.000 -> 10000000
#     10.500.000,50 -> 10500000.50
#     """

#     if pd.isna(value):
#         return 0

#     if isinstance(value, (int, float)):
#         return float(value)

#     value = str(value).strip()

#     if value == "":
#         return 0

#     value = (
#         value
#         .replace("Rp", "")
#         .replace("rp", "")
#         .replace(" ", "")
#     )

#     # Format Indonesia
#     value = value.replace(".", "")
#     value = value.replace(",", ".")

#     try:
#         return float(value)

#     except (ValueError, TypeError):
#         return 0


# # =========================================================
# # 3. CLEAN NUMBER UNTUK PARTICIPANT
# # =========================================================

# def clean_participant_number(value):
#     """
#     Membersihkan angka Participant Target / Actual.

#     PENTING:
#     Untuk participant jangan menggunakan clean_number()
#     karena:

#         "10.0"

#     bisa dianggap menjadi:

#         100

#     oleh format angka financial Indonesia.

#     Fungsi ini mempertahankan:
#         10
#         10.0
#         15
#         20
#     sebagai angka sebenarnya.
#     """

#     if pd.isna(value):
#         return 0

#     if isinstance(value, (int, float)):
#         return float(value)

#     value = str(value).strip()

#     if value == "":
#         return 0

#     value = value.replace(" ", "")

#     try:
#         # Jika desimal menggunakan koma
#         value = value.replace(",", ".")

#         return float(value)

#     except (ValueError, TypeError):
#         return 0


# # =========================================================
# # 4. EXTRACT FINANCIAL PERFORMANCE
# # =========================================================

# def extract_financial_performance(sheets):

#     records = []

#     for sheet_name, df in sheets.items():

#         info = extract_program_info(sheet_name)

#         if info is None:
#             continue

#         if df is None or df.empty:
#             continue

#         # -------------------------------------------------
#         # Cari baris header
#         # -------------------------------------------------

#         header_row = None

#         for i in range(min(len(df), 30)):

#             row_text = " ".join(
#                 df.iloc[i]
#                 .astype(str)
#                 .str.lower()
#                 .tolist()
#             )

#             if (
#                 "uraian pengajuan" in row_text
#                 and
#                 "nilai pengajuan" in row_text
#             ):
#                 header_row = i
#                 break

#         if header_row is None:
#             continue

#         data = df.iloc[header_row + 1:].copy()

#         # -------------------------------------------------
#         # Cari posisi kolom
#         # -------------------------------------------------

#         headers = df.iloc[header_row].astype(str).str.lower()

#         uraian_col = None
#         nilai_col = None
#         saldo_col = None

#         for col_index, header in headers.items():

#             header = str(header).strip()

#             if "uraian pengajuan" in header:
#                 uraian_col = col_index

#             if "nilai pengajuan" in header:
#                 nilai_col = col_index

#             if "saldo" in header:
#                 saldo_col = col_index

#         if uraian_col is None or nilai_col is None:
#             continue

#         # -------------------------------------------------
#         # Cari PKS
#         # -------------------------------------------------

#         target = 0

#         for _, row in data.iterrows():

#             uraian = str(row.iloc[uraian_col]).strip().upper()

#             if "PKS" in uraian:

#                 if saldo_col is not None:
#                     target = clean_number(
#                         row.iloc[saldo_col]
#                     )

#                 if target == 0:
#                     target = clean_number(
#                         row.iloc[nilai_col]
#                     )

#                 if target > 0:
#                     break

#         # -------------------------------------------------
#         # Cari DPKS
#         # -------------------------------------------------

#         actual = 0
#         found_dpks = False

#         for _, row in data.iterrows():

#             uraian = str(row.iloc[uraian_col]).strip().upper()

#             if "DPKS" in uraian:
#                 found_dpks = True
#                 continue

#             if found_dpks:

#                 nilai = clean_number(
#                     row.iloc[nilai_col]
#                 )

#                 actual += nilai

#         # -------------------------------------------------
#         # Kalau DPKS tidak ditemukan
#         # -------------------------------------------------

#         if not found_dpks:

#             actual = 0

#         # -------------------------------------------------
#         # Total pengajuan
#         # -------------------------------------------------

#         total_pengajuan = 0

#         for _, row in data.iterrows():

#             nilai = clean_number(
#                 row.iloc[nilai_col]
#             )

#             total_pengajuan += nilai

#         # -------------------------------------------------
#         # Saldo terakhir
#         # -------------------------------------------------

#         saldo_terakhir = 0

#         if saldo_col is not None:

#             for _, row in data.iterrows():

#                 saldo = clean_number(
#                     row.iloc[saldo_col]
#                 )

#                 if saldo != 0:
#                     saldo_terakhir = saldo

#         # -------------------------------------------------
#         # Percentage
#         # -------------------------------------------------

#         if target > 0:
#             percentage = (
#                 actual / target
#             ) * 100

#         else:
#             percentage = 0

#         records.append({
#             "Program": info["Program"],
#             "Tanggal": info["Tanggal"],
#             "Bulan": info["Bulan"],
#             "Tahun": info["Tahun"],
#             "Target": target,
#             "Actual": actual,
#             "Total Pengajuan": total_pengajuan,
#             "Saldo Terakhir": saldo_terakhir,
#             "Percentage": percentage
#         })

#     # -----------------------------------------------------
#     # DataFrame
#     # -----------------------------------------------------

#     result = pd.DataFrame(records)

#     if result.empty:
#         return result

#     numeric_columns = [
#         "Tanggal",
#         "Bulan",
#         "Tahun",
#         "Target",
#         "Actual",
#         "Total Pengajuan",
#         "Saldo Terakhir",
#         "Percentage"
#     ]

#     for col in numeric_columns:
#         result[col] = pd.to_numeric(
#             result[col],
#             errors="coerce"
#         ).fillna(0)

#     result = result.sort_values(
#         ["Tahun", "Bulan", "Tanggal", "Program"]
#     ).reset_index(drop=True)

#     return result


# # =========================================================
# # 5. EXTRACT PARTICIPANT TARGET & ACTUAL
# # =========================================================

# def extract_participant_target(sheets):

#     records = []

#     # =====================================================
#     # Struktur file Participant
#     #
#     # Baris Excel 3-4 = HEADER
#     # Baris Excel 5 dst = DATA
#     #
#     # A = Tahun
#     # B = Bulan
#     # C = Tanggal
#     # D = ...
#     # E = ...
#     # F = ...
#     # G = Participant Target
#     # H = Participant Actual
#     #
#     # Python index:
#     # A = 0
#     # B = 1
#     # C = 2
#     # G = 6
#     # H = 7
#     # =====================================================

#     YEAR_COL = 0
#     MONTH_COL = 1
#     DATE_COL = 2
#     TARGET_COL = 6
#     ACTUAL_COL = 7

#     # -----------------------------------------------------
#     # Hanya ambil sheet SIAP dan INSPIRASI
#     # -----------------------------------------------------

#     for sheet_name, df in sheets.items():

#         sheet_name_clean = (
#             str(sheet_name)
#             .strip()
#             .upper()
#         )

#         if sheet_name_clean not in [
#             "SIAP",
#             "INSPIRASI"
#         ]:
#             continue

#         if df is None or df.empty:
#             continue

#         # -------------------------------------------------
#         # Header berada pada baris Excel 3-4
#         #
#         # Python index:
#         # Excel baris 3 = index 2
#         # Excel baris 4 = index 3
#         #
#         # Kita mulai data dari index 4
#         # = Excel baris 5
#         # -------------------------------------------------

#         data = df.iloc[4:].copy()

#         current_year = None
#         current_month = None

#         for _, row in data.iterrows():

#             # -------------------------------------------------
#             # Pastikan jumlah kolom minimal 8
#             # -------------------------------------------------

#             if len(row) < 8:
#                 continue

#             # -------------------------------------------------
#             # Ambil Tahun
#             # -------------------------------------------------

#             year_value = row.iloc[YEAR_COL]

#             if not pd.isna(year_value):

#                 year_text = str(
#                     year_value
#                 ).strip()

#                 if year_text not in [
#                     "",
#                     "nan",
#                     "None"
#                 ]:

#                     try:
#                         current_year = int(
#                             float(year_text)
#                         )

#                     except (ValueError, TypeError):
#                         pass

#             # -------------------------------------------------
#             # Ambil Bulan
#             # -------------------------------------------------

#             month_value = row.iloc[MONTH_COL]

#             if not pd.isna(month_value):

#                 month_text = str(
#                     month_value
#                 ).strip()

#                 if month_text not in [
#                     "",
#                     "nan",
#                     "None"
#                 ]:

#                     # Jika bulan berupa angka
#                     try:

#                         current_month = int(
#                             float(month_text)
#                         )

#                     except (ValueError, TypeError):

#                         # Jika bulan berupa nama
#                         month_map = {
#                             "JANUARI": 1,
#                             "FEBRUARI": 2,
#                             "MARET": 3,
#                             "APRIL": 4,
#                             "MEI": 5,
#                             "JUNI": 6,
#                             "JULI": 7,
#                             "AGUSTUS": 8,
#                             "SEPTEMBER": 9,
#                             "OKTOBER": 10,
#                             "NOVEMBER": 11,
#                             "DESEMBER": 12,

#                             "JANUARY": 1,
#                             "FEBRUARY": 2,
#                             "MARCH": 3,
#                             "APRIL": 4,
#                             "MAY": 5,
#                             "JUNE": 6,
#                             "JULY": 7,
#                             "AUGUST": 8,
#                             "SEPTEMBER": 9,
#                             "OCTOBER": 10,
#                             "NOVEMBER": 11,
#                             "DECEMBER": 12
#                         }

#                         current_month = month_map.get(
#                             month_text.upper()
#                         )

#             # -------------------------------------------------
#             # Kalau tahun atau bulan belum tersedia
#             # -------------------------------------------------

#             if current_year is None:
#                 continue

#             if current_month is None:
#                 continue

#             # -------------------------------------------------
#             # Ambil Tanggal dari kolom C
#             # -------------------------------------------------

#             date_value = row.iloc[DATE_COL]

#             if pd.isna(date_value):
#                 continue

#             date_number = None

#             # Jika Excel langsung memberikan angka
#             if isinstance(
#                 date_value,
#                 (int, float)
#             ):

#                 if not pd.isna(date_value):
#                     date_number = int(
#                         date_value
#                     )

#             else:

#                 date_text = str(
#                     date_value
#                 ).strip()

#                 if date_text in [
#                     "",
#                     "nan",
#                     "None"
#                 ]:
#                     continue

#                 # Coba format tanggal penuh
#                 parsed_date = pd.to_datetime(
#                     date_text,
#                     errors="coerce"
#                 )

#                 if not pd.isna(parsed_date):

#                     # Kalau hasilnya tanggal
#                     # gunakan day
#                     date_number = int(
#                         parsed_date.day
#                     )

#                 else:

#                     # Coba angka biasa
#                     try:

#                         date_number = int(
#                             float(date_text)
#                         )

#                     except (ValueError, TypeError):
#                         continue

#             if date_number is None:
#                 continue

#             # -------------------------------------------------
#             # Validasi tanggal
#             # -------------------------------------------------

#             if date_number < 1 or date_number > 31:
#                 continue

#             # -------------------------------------------------
#             # G = Participant Target
#             # H = Participant Actual
#             # -------------------------------------------------

#             target_value = row.iloc[TARGET_COL]
#             actual_value = row.iloc[ACTUAL_COL]

#             target = clean_participant_number(
#                 target_value
#             )

#             actual = clean_participant_number(
#                 actual_value
#             )

#             # -------------------------------------------------
#             # Kalau Target dan Actual sama-sama kosong
#             # -------------------------------------------------

#             if target == 0 and actual == 0:

#                 # Cek apakah benar-benar kosong
#                 target_empty = (
#                     pd.isna(target_value)
#                     or str(target_value).strip() == ""
#                 )

#                 actual_empty = (
#                     pd.isna(actual_value)
#                     or str(actual_value).strip() == ""
#                 )

#                 if target_empty and actual_empty:
#                     continue

#             # -------------------------------------------------
#             # Percentage
#             # -------------------------------------------------

#             if target > 0:

#                 percentage = (
#                     actual / target
#                 ) * 100

#             else:

#                 percentage = 0

#             # -------------------------------------------------
#             # Simpan
#             # -------------------------------------------------

#             records.append({
#                 "Program": sheet_name_clean,
#                 "Tanggal": date_number,
#                 "Bulan": current_month,
#                 "Tahun": current_year,
#                 "Target": target,
#                 "Actual": actual,
#                 "Percentage": percentage
#             })

#     # =====================================================
#     # BUAT DATAFRAME
#     # =====================================================

#     result = pd.DataFrame(records)

#     if result.empty:
#         return result

#     # -----------------------------------------------------
#     # Pastikan numeric
#     # -----------------------------------------------------

#     numeric_columns = [
#         "Tanggal",
#         "Bulan",
#         "Tahun",
#         "Target",
#         "Actual",
#         "Percentage"
#     ]

#     for col in numeric_columns:

#         result[col] = pd.to_numeric(
#             result[col],
#             errors="coerce"
#         ).fillna(0)

#     # -----------------------------------------------------
#     # Urutkan berdasarkan tanggal
#     # -----------------------------------------------------

#     result = result.sort_values(
#         [
#             "Tahun",
#             "Bulan",
#             "Tanggal",
#             "Program"
#         ]
#     ).reset_index(drop=True)

#     return result


# # =========================================================
# # 6. FINANCIAL CHART
# # =========================================================

# def create_financial_chart(df):

#     if df is None or df.empty:
#         return None

#     chart_df = df.copy()

#     # -----------------------------------------------------
#     # Pastikan kolom numeric
#     # -----------------------------------------------------

#     for col in [
#         "Tanggal",
#         "Bulan",
#         "Tahun",
#         "Target",
#         "Actual"
#     ]:
#         chart_df[col] = pd.to_numeric(
#             chart_df[col],
#             errors="coerce"
#         ).fillna(0)

#     # -----------------------------------------------------
#     # Buat tanggal periode
#     # -----------------------------------------------------

#     chart_df["Tanggal Periode"] = pd.to_datetime(
#         dict(
#             year=chart_df["Tahun"].astype(int),
#             month=chart_df["Bulan"].astype(int),
#             day=chart_df["Tanggal"].astype(int)
#         ),
#         errors="coerce"
#     )

#     chart_df = chart_df.sort_values(
#         [
#             "Tahun",
#             "Bulan",
#             "Tanggal",
#             "Program"
#         ]
#     )

#     # -----------------------------------------------------
#     # Long format
#     # -----------------------------------------------------

#     plot_df = chart_df[
#         [
#             "Program",
#             "Tanggal Periode",
#             "Target",
#             "Actual"
#         ]
#     ].copy()

#     plot_df = plot_df.melt(
#         id_vars=[
#             "Program",
#             "Tanggal Periode"
#         ],
#         value_vars=[
#             "Target",
#             "Actual"
#         ],
#         var_name="Jenis",
#         value_name="Nilai"
#     )

#     # -----------------------------------------------------
#     # LINE CHART
#     # -----------------------------------------------------

#     fig = px.line(
#         plot_df,
#         x="Tanggal Periode",
#         y="Nilai",
#         color="Jenis",
#         markers=True,
#         line_dash="Program",
#         hover_data=[
#             "Program"
#         ],
#         title="Financial Target vs Actual"
#     )

#     fig.update_layout(
#         xaxis_title="Periode",
#         yaxis_title="Nilai",
#         legend_title="",
#         hovermode="x unified"
#     )

#     fig.update_xaxes(
#         tickformat="%d %b %Y"
#     )

#     return fig


# # =========================================================
# # 7. PARTICIPANT CHART
# # =========================================================

# def create_participant_chart(df):

#     if df is None or df.empty:
#         return None

#     chart_df = df.copy()

#     # -----------------------------------------------------
#     # Pastikan kolom numeric
#     # -----------------------------------------------------

#     for col in [
#         "Tanggal",
#         "Bulan",
#         "Tahun",
#         "Target",
#         "Actual"
#     ]:
#         chart_df[col] = pd.to_numeric(
#             chart_df[col],
#             errors="coerce"
#         ).fillna(0)

#     # -----------------------------------------------------
#     # Urutkan berdasarkan tanggal
#     # -----------------------------------------------------

#     chart_df = chart_df.sort_values(
#         [
#             "Program",
#             "Tahun",
#             "Bulan",
#             "Tanggal"
#         ]
#     )

#     # -----------------------------------------------------
#     # Ambil DATA TERAKHIR setiap bulan
#     # -----------------------------------------------------
#     #
#     # Contoh:
#     #
#     # Juli
#     # 4 Juli  -> Target 10, Actual 8
#     # 11 Juli -> Target 10, Actual 10
#     #
#     # Yang digunakan:
#     # 11 Juli -> Target 10, Actual 10
#     #
#     # -----------------------------------------------------

#     monthly_df = (
#         chart_df
#         .groupby(
#             [
#                 "Program",
#                 "Tahun",
#                 "Bulan"
#             ],
#             as_index=False
#         )
#         .tail(1)
#         .copy()
#     )

#     # -----------------------------------------------------
#     # Mapping nama bulan
#     # -----------------------------------------------------

#     month_names = {
#         1: "Januari",
#         2: "Februari",
#         3: "Maret",
#         4: "April",
#         5: "Mei",
#         6: "Juni",
#         7: "Juli",
#         8: "Agustus",
#         9: "September",
#         10: "Oktober",
#         11: "November",
#         12: "Desember"
#     }

#     monthly_df["Nama Bulan"] = (
#         monthly_df["Bulan"]
#         .map(month_names)
#     )

#     # -----------------------------------------------------
#     # Buat tanggal periode untuk sumbu X
#     # -----------------------------------------------------

#     monthly_df["Tanggal Periode"] = pd.to_datetime(
#         dict(
#             year=monthly_df["Tahun"].astype(int),
#             month=monthly_df["Bulan"].astype(int),
#             day=1
#         ),
#         errors="coerce"
#     )

#     monthly_df = monthly_df.sort_values(
#         [
#             "Program",
#             "Tanggal Periode"
#         ]
#     )

#     # -----------------------------------------------------
#     # Long format
#     # -----------------------------------------------------

#     plot_df = monthly_df[
#         [
#             "Program",
#             "Tahun",
#             "Bulan",
#             "Nama Bulan",
#             "Tanggal",
#             "Tanggal Periode",
#             "Target",
#             "Actual"
#         ]
#     ].copy()

#     plot_df = plot_df.melt(
#         id_vars=[
#             "Program",
#             "Tahun",
#             "Bulan",
#             "Nama Bulan",
#             "Tanggal",
#             "Tanggal Periode"
#         ],
#         value_vars=[
#             "Target",
#             "Actual"
#         ],
#         var_name="Jenis",
#         value_name="Peserta"
#     )

#     # -----------------------------------------------------
#     # LINE CHART
#     # -----------------------------------------------------

#     fig = px.line(
#         plot_df,
#         x="Tanggal Periode",
#         y="Peserta",
#         color="Jenis",
#         markers=True,
#         line_dash="Program",
#         hover_data=[
#             "Program",
#             "Tahun",
#             "Tanggal"
#         ],
#         title="Participant Target vs Actual"
#     )

#     fig.update_layout(
#         xaxis_title="Bulan",
#         yaxis_title="Jumlah Peserta",
#         legend_title="",
#         hovermode="x unified"
#     )

#     fig.update_xaxes(
#         tickformat="%b %Y"
#     )

#     return fig





import re
import pandas as pd
import plotly.express as px


# =========================================================
# 1. EXTRACT PROGRAM INFO DARI NAMA SHEET FINANCIAL
# =========================================================

def extract_program_info(sheet_name):
    """
    Contoh nama sheet:
    DITSAMA.PM-3-6-2026-SIAP

    Hasil:
    Program = SIAP
    Tanggal = 3
    Bulan = 6
    Tahun = 2026
    """

    sheet_name = str(sheet_name).strip()

    pattern = r"PM-(\d{1,2})-(\d{1,2})-(\d{4})-(.+)"

    match = re.search(pattern, sheet_name)

    if not match:
        return None

    tanggal = int(match.group(1))
    bulan = int(match.group(2))
    tahun = int(match.group(3))
    program = match.group(4).strip()

    return {
        "Program": program,
        "Tanggal": tanggal,
        "Bulan": bulan,
        "Tahun": tahun
    }


# =========================================================
# 2. CLEAN NUMBER UNTUK DATA FINANCIAL
# =========================================================

def clean_number(value):
    """
    Membersihkan angka financial.

    Contoh:
    Rp 10.000.000 -> 10000000
    10.000.000 -> 10000000
    10.500.000,50 -> 10500000.50
    """

    if pd.isna(value):
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if value == "":
        return 0

    value = (
        value
        .replace("Rp", "")
        .replace("rp", "")
        .replace(" ", "")
    )

    # Format Indonesia
    value = value.replace(".", "")
    value = value.replace(",", ".")

    try:
        return float(value)

    except (ValueError, TypeError):
        return 0


# =========================================================
# 3. CLEAN NUMBER UNTUK PARTICIPANT
# =========================================================

def clean_participant_number(value):
    """
    Membersihkan angka Participant Target / Actual.

    Contoh:
    10 -> 10
    10.0 -> 10
    15 -> 15
    20 -> 20

    Tidak menggunakan clean_number() karena titik pada
    angka participant merupakan desimal, bukan pemisah ribuan.
    """

    if pd.isna(value):
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if value == "":
        return 0

    value = value.replace(" ", "")

    try:
        value = value.replace(",", ".")

        return float(value)

    except (ValueError, TypeError):
        return 0


# =========================================================
# 4. EXTRACT FINANCIAL PERFORMANCE
# =========================================================

def extract_financial_performance(sheets):

    records = []

    for sheet_name, df in sheets.items():

        # -------------------------------------------------
        # Ambil informasi program dari nama sheet
        # -------------------------------------------------

        info = extract_program_info(sheet_name)

        if info is None:
            continue

        if df is None or df.empty:
            continue

        # -------------------------------------------------
        # Cari baris header
        # -------------------------------------------------

        header_row = None

        for i in range(min(len(df), 30)):

            row_values = df.iloc[i].tolist()

            # Pastikan SEMUA value menjadi string
            # sehingga aman digunakan oleh join()
            row_values = [
                "" if pd.isna(value)
                else str(value)
                for value in row_values
            ]

            row_text = " ".join(row_values).lower()

            if (
                "uraian pengajuan" in row_text
                and
                "nilai pengajuan" in row_text
            ):
                header_row = i
                break

        # Kalau header tidak ditemukan
        if header_row is None:
            continue

        # -------------------------------------------------
        # Data dimulai setelah header
        # -------------------------------------------------

        data = df.iloc[header_row + 1:].copy()

        if data.empty:
            continue

        # -------------------------------------------------
        # Cari posisi kolom
        # -------------------------------------------------

        raw_headers = df.iloc[header_row].tolist()

        headers = [
            "" if pd.isna(value)
            else str(value).strip().lower()
            for value in raw_headers
        ]

        uraian_col = None
        nilai_col = None
        saldo_col = None

        for col_index, header in enumerate(headers):

            if "uraian pengajuan" in header:
                uraian_col = col_index

            if "nilai pengajuan" in header:
                nilai_col = col_index

            if "saldo" in header:
                saldo_col = col_index

        # -------------------------------------------------
        # Kolom wajib tidak ditemukan
        # -------------------------------------------------

        if uraian_col is None or nilai_col is None:
            continue

        # =================================================
        # CARI PKS
        # =================================================

        target = 0

        for _, row in data.iterrows():

            if len(row) <= uraian_col:
                continue

            uraian_value = row.iloc[uraian_col]

            if pd.isna(uraian_value):
                uraian = ""
            else:
                uraian = str(
                    uraian_value
                ).strip().upper()

            # -------------------------------------------------
            # Jika menemukan PKS
            # -------------------------------------------------

            if "PKS" in uraian:

                # Prioritas pertama:
                # ambil dari kolom Saldo
                if (
                    saldo_col is not None
                    and len(row) > saldo_col
                ):

                    target = clean_number(
                        row.iloc[saldo_col]
                    )

                # Kalau Saldo 0/kosong,
                # gunakan Nilai Pengajuan
                if target == 0:

                    if len(row) > nilai_col:

                        target = clean_number(
                            row.iloc[nilai_col]
                        )

                # Kalau sudah mendapatkan target,
                # berhenti mencari PKS
                if target > 0:
                    break

        # =================================================
        # CARI DPKS
        # =================================================

        actual = 0

        found_dpks = False

        for _, row in data.iterrows():

            if len(row) <= uraian_col:
                continue

            uraian_value = row.iloc[uraian_col]

            if pd.isna(uraian_value):
                uraian = ""
            else:
                uraian = str(
                    uraian_value
                ).strip().upper()

            # -------------------------------------------------
            # Temukan DPKS
            # -------------------------------------------------

            if "DPKS" in uraian:

                found_dpks = True

                continue

            # -------------------------------------------------
            # Setelah DPKS,
            # semua Nilai Pengajuan dijumlahkan
            # sebagai Actual
            # -------------------------------------------------

            if found_dpks:

                if len(row) > nilai_col:

                    nilai = clean_number(
                        row.iloc[nilai_col]
                    )

                    actual += nilai

        # -------------------------------------------------
        # Kalau DPKS tidak ditemukan
        # -------------------------------------------------

        if not found_dpks:
            actual = 0

        # =================================================
        # TOTAL PENGAJUAN
        # =================================================

        total_pengajuan = 0

        for _, row in data.iterrows():

            if len(row) > nilai_col:

                nilai = clean_number(
                    row.iloc[nilai_col]
                )

                total_pengajuan += nilai

        # =================================================
        # SALDO TERAKHIR
        # =================================================

        saldo_terakhir = 0

        if saldo_col is not None:

            for _, row in data.iterrows():

                if len(row) > saldo_col:

                    saldo = clean_number(
                        row.iloc[saldo_col]
                    )

                    if saldo != 0:
                        saldo_terakhir = saldo

        # =================================================
        # PERCENTAGE
        # =================================================

        if target > 0:

            percentage = (
                actual / target
            ) * 100

        else:

            percentage = 0

        # =================================================
        # SIMPAN RECORD
        # =================================================

        records.append({
            "Program": info["Program"],
            "Tanggal": info["Tanggal"],
            "Bulan": info["Bulan"],
            "Tahun": info["Tahun"],
            "Target": target,
            "Actual": actual,
            "Total Pengajuan": total_pengajuan,
            "Saldo Terakhir": saldo_terakhir,
            "Percentage": percentage
        })

    # =====================================================
    # BUAT DATAFRAME
    # =====================================================

    result = pd.DataFrame(records)

    if result.empty:
        return result

    # -----------------------------------------------------
    # Pastikan kolom numeric
    # -----------------------------------------------------

    numeric_columns = [
        "Tanggal",
        "Bulan",
        "Tahun",
        "Target",
        "Actual",
        "Total Pengajuan",
        "Saldo Terakhir",
        "Percentage"
    ]

    for col in numeric_columns:

        result[col] = pd.to_numeric(
            result[col],
            errors="coerce"
        ).fillna(0)

    # -----------------------------------------------------
    # Urutkan data
    # -----------------------------------------------------

    result = result.sort_values(
        [
            "Tahun",
            "Bulan",
            "Tanggal",
            "Program"
        ]
    ).reset_index(drop=True)

    return result


# =========================================================
# 5. EXTRACT PARTICIPANT TARGET & ACTUAL
# =========================================================

def extract_participant_target(sheets):

    records = []

    # =====================================================
    # Struktur file Participant
    #
    # Baris Excel 3-4 = HEADER
    # Baris Excel 5 dst = DATA
    #
    # A = Tahun
    # B = Bulan
    # C = Tanggal
    # D = ...
    # E = ...
    # F = ...
    # G = Participant Target
    # H = Participant Actual
    #
    # Python index:
    # A = 0
    # B = 1
    # C = 2
    # G = 6
    # H = 7
    # =====================================================

    YEAR_COL = 0
    MONTH_COL = 1
    DATE_COL = 2
    TARGET_COL = 6
    ACTUAL_COL = 7

    # -----------------------------------------------------
    # Hanya ambil sheet SIAP dan INSPIRASI
    # -----------------------------------------------------

    for sheet_name, df in sheets.items():

        sheet_name_clean = (
            str(sheet_name)
            .strip()
            .upper()
        )

        if sheet_name_clean not in [
            "SIAP",
            "INSPIRASI"
        ]:
            continue

        if df is None or df.empty:
            continue

        # -------------------------------------------------
        # Data dimulai dari Excel baris 5
        # Python index = 4
        # -------------------------------------------------

        data = df.iloc[4:].copy()

        current_year = None
        current_month = None

        for _, row in data.iterrows():

            # -------------------------------------------------
            # Minimal 8 kolom
            # -------------------------------------------------

            if len(row) < 8:
                continue

            # =================================================
            # TAHUN
            # =================================================

            year_value = row.iloc[YEAR_COL]

            if not pd.isna(year_value):

                year_text = str(
                    year_value
                ).strip()

                if year_text not in [
                    "",
                    "nan",
                    "None"
                ]:

                    try:

                        current_year = int(
                            float(year_text)
                        )

                    except (ValueError, TypeError):
                        pass

            # =================================================
            # BULAN
            # =================================================

            month_value = row.iloc[MONTH_COL]

            if not pd.isna(month_value):

                month_text = str(
                    month_value
                ).strip()

                if month_text not in [
                    "",
                    "nan",
                    "None"
                ]:

                    # -----------------------------------------
                    # Jika bulan berupa angka
                    # -----------------------------------------

                    try:

                        current_month = int(
                            float(month_text)
                        )

                    except (ValueError, TypeError):

                        # -------------------------------------
                        # Jika bulan berupa nama
                        # -------------------------------------

                        month_map = {

                            "JANUARI": 1,
                            "FEBRUARI": 2,
                            "MARET": 3,
                            "APRIL": 4,
                            "MEI": 5,
                            "JUNI": 6,
                            "JULI": 7,
                            "AGUSTUS": 8,
                            "SEPTEMBER": 9,
                            "OKTOBER": 10,
                            "NOVEMBER": 11,
                            "DESEMBER": 12,

                            "JANUARY": 1,
                            "FEBRUARY": 2,
                            "MARCH": 3,
                            "MAY": 5,
                            "JUNE": 6,
                            "JULY": 7,
                            "AUGUST": 8,
                            "OCTOBER": 10,
                            "NOVEMBER": 11,
                            "DECEMBER": 12
                        }

                        current_month = month_map.get(
                            month_text.upper()
                        )

            # -------------------------------------------------
            # Tahun / bulan belum tersedia
            # -------------------------------------------------

            if current_year is None:
                continue

            if current_month is None:
                continue

            # =================================================
            # TANGGAL
            # =================================================

            date_value = row.iloc[DATE_COL]

            if pd.isna(date_value):
                continue

            date_number = None

            # -------------------------------------------------
            # Jika Excel memberikan angka
            # -------------------------------------------------

            if isinstance(
                date_value,
                (int, float)
            ):

                if not pd.isna(date_value):

                    date_number = int(
                        date_value
                    )

            # -------------------------------------------------
            # Jika berupa teks
            # -------------------------------------------------

            else:

                date_text = str(
                    date_value
                ).strip()

                if date_text in [
                    "",
                    "nan",
                    "None"
                ]:
                    continue

                # ---------------------------------------------
                # Coba parse tanggal
                # ---------------------------------------------

                parsed_date = pd.to_datetime(
                    date_text,
                    errors="coerce"
                )

                if not pd.isna(parsed_date):

                    date_number = int(
                        parsed_date.day
                    )

                else:

                    # -----------------------------------------
                    # Coba sebagai angka
                    # -----------------------------------------

                    try:

                        date_number = int(
                            float(date_text)
                        )

                    except (ValueError, TypeError):
                        continue

            # -------------------------------------------------
            # Validasi tanggal
            # -------------------------------------------------

            if date_number is None:
                continue

            if date_number < 1 or date_number > 31:
                continue

            # =================================================
            # TARGET & ACTUAL
            # =================================================

            target_value = row.iloc[TARGET_COL]
            actual_value = row.iloc[ACTUAL_COL]

            target = clean_participant_number(
                target_value
            )

            actual = clean_participant_number(
                actual_value
            )

            # -------------------------------------------------
            # Kalau Target dan Actual sama-sama kosong
            # -------------------------------------------------

            if target == 0 and actual == 0:

                target_empty = (
                    pd.isna(target_value)
                    or str(target_value).strip() == ""
                )

                actual_empty = (
                    pd.isna(actual_value)
                    or str(actual_value).strip() == ""
                )

                if target_empty and actual_empty:
                    continue

            # =================================================
            # PERCENTAGE
            # =================================================

            if target > 0:

                percentage = (
                    actual / target
                ) * 100

            else:

                percentage = 0

            # =================================================
            # SIMPAN RECORD
            # =================================================

            records.append({
                "Program": sheet_name_clean,
                "Tanggal": date_number,
                "Bulan": current_month,
                "Tahun": current_year,
                "Target": target,
                "Actual": actual,
                "Percentage": percentage
            })

    # =====================================================
    # BUAT DATAFRAME
    # =====================================================

    result = pd.DataFrame(records)

    if result.empty:
        return result

    # -----------------------------------------------------
    # Pastikan numeric
    # -----------------------------------------------------

    numeric_columns = [
        "Tanggal",
        "Bulan",
        "Tahun",
        "Target",
        "Actual",
        "Percentage"
    ]

    for col in numeric_columns:

        result[col] = pd.to_numeric(
            result[col],
            errors="coerce"
        ).fillna(0)

    # -----------------------------------------------------
    # Urutkan
    # -----------------------------------------------------

    result = result.sort_values(
        [
            "Tahun",
            "Bulan",
            "Tanggal",
            "Program"
        ]
    ).reset_index(drop=True)

    return result


# =========================================================
# 6. FINANCIAL CHART
# =========================================================

def create_financial_chart(df):

    if df is None or df.empty:
        return None

    chart_df = df.copy()

    # -----------------------------------------------------
    # Pastikan numeric
    # -----------------------------------------------------

    for col in [
        "Tanggal",
        "Bulan",
        "Tahun",
        "Target",
        "Actual"
    ]:

        chart_df[col] = pd.to_numeric(
            chart_df[col],
            errors="coerce"
        ).fillna(0)

    # -----------------------------------------------------
    # Buat tanggal periode
    # -----------------------------------------------------

    chart_df["Tanggal Periode"] = pd.to_datetime(
        dict(
            year=chart_df["Tahun"].astype(int),
            month=chart_df["Bulan"].astype(int),
            day=chart_df["Tanggal"].astype(int)
        ),
        errors="coerce"
    )

    chart_df = chart_df.dropna(
        subset=["Tanggal Periode"]
    )

    chart_df = chart_df.sort_values(
        [
            "Tahun",
            "Bulan",
            "Tanggal",
            "Program"
        ]
    )

    # =====================================================
    # LONG FORMAT
    # =====================================================

    plot_df = chart_df[
        [
            "Program",
            "Tanggal Periode",
            "Target",
            "Actual"
        ]
    ].copy()

    plot_df = plot_df.melt(
        id_vars=[
            "Program",
            "Tanggal Periode"
        ],
        value_vars=[
            "Target",
            "Actual"
        ],
        var_name="Jenis",
        value_name="Nilai"
    )

    # =====================================================
    # LINE CHART
    # =====================================================

    fig = px.line(
        plot_df,
        x="Tanggal Periode",
        y="Nilai",
        color="Jenis",
        markers=True,
        line_dash="Program",
        hover_data=[
            "Program"
        ],
        title="Financial Target vs Actual"
    )

    fig.update_layout(
        xaxis_title="Periode",
        yaxis_title="Nilai",
        legend_title="",
        hovermode="x unified"
    )

    fig.update_xaxes(
        tickformat="%d %b %Y"
    )

    return fig


# =========================================================
# 7. PARTICIPANT CHART
# =========================================================

def create_participant_chart(df):

    if df is None or df.empty:
        return None

    chart_df = df.copy()

    # -----------------------------------------------------
    # Pastikan numeric
    # -----------------------------------------------------

    for col in [
        "Tanggal",
        "Bulan",
        "Tahun",
        "Target",
        "Actual"
    ]:

        chart_df[col] = pd.to_numeric(
            chart_df[col],
            errors="coerce"
        ).fillna(0)

    # -----------------------------------------------------
    # Urutkan
    # -----------------------------------------------------

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

    monthly_df = (
        chart_df
        .groupby(
            [
                "Program",
                "Tahun",
                "Bulan"
            ],
            as_index=False
        )
        .tail(1)
        .copy()
    )

    # =====================================================
    # MAPPING NAMA BULAN
    # =====================================================

    month_names = {
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

    monthly_df["Nama Bulan"] = (
        monthly_df["Bulan"]
        .map(month_names)
    )

    # =====================================================
    # BUAT TANGGAL PERIODE
    # =====================================================

    monthly_df["Tanggal Periode"] = pd.to_datetime(
        dict(
            year=monthly_df["Tahun"].astype(int),
            month=monthly_df["Bulan"].astype(int),
            day=1
        ),
        errors="coerce"
    )

    monthly_df = monthly_df.dropna(
        subset=["Tanggal Periode"]
    )

    monthly_df = monthly_df.sort_values(
        [
            "Program",
            "Tanggal Periode"
        ]
    )

    # =====================================================
    # LONG FORMAT
    # =====================================================

    plot_df = monthly_df[
        [
            "Program",
            "Tahun",
            "Bulan",
            "Nama Bulan",
            "Tanggal",
            "Tanggal Periode",
            "Target",
            "Actual"
        ]
    ].copy()

    plot_df = plot_df.melt(
        id_vars=[
            "Program",
            "Tahun",
            "Bulan",
            "Nama Bulan",
            "Tanggal",
            "Tanggal Periode"
        ],
        value_vars=[
            "Target",
            "Actual"
        ],
        var_name="Jenis",
        value_name="Peserta"
    )

    # =====================================================
    # LINE CHART
    # =====================================================

    fig = px.line(
        plot_df,
        x="Tanggal Periode",
        y="Peserta",
        color="Jenis",
        markers=True,
        line_dash="Program",
        hover_data=[
            "Program",
            "Tahun",
            "Tanggal"
        ],
        title="Participant Target vs Actual"
    )

    fig.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Jumlah Peserta",
        legend_title="",
        hovermode="x unified"
    )

    fig.update_xaxes(
        tickformat="%b %Y"
    )

    return fig
