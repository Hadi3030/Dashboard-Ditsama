import re
import pandas as pd
import plotly.express as px


# =========================================================
# 1. EXTRACT PROGRAM INFO DARI NAMA SHEET
# =========================================================

def extract_program_info(sheet_name):
    """
    Contoh nama sheet:
    PM-01-01-2026-OSN

    Hasil:
    Program = OSN
    Bulan = 1
    Tanggal = 1
    Tahun = 2026
    """

    match = re.search(
        r"PM-(\d{1,2})-(\d{1,2})-(\d{4})-(.+)",
        str(sheet_name)
    )

    if match:
        bulan = int(match.group(1))
        tanggal = int(match.group(2))
        tahun = int(match.group(3))
        program = match.group(4).strip()

        return {
            "Program": program,
            "Bulan": bulan,
            "Tanggal": tanggal,
            "Tahun": tahun
        }

    return None


# =========================================================
# 2. CLEAN NUMBER FINANCIAL
# =========================================================

def clean_number(value):
    """
    Membersihkan angka dari format Excel / string.

    Contoh:
    1.500.000
    Rp 1.500.000
    1,500,000
    1500000
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

    # Jika menggunakan format Indonesia
    if "." in value and "," in value:
        value = value.replace(".", "").replace(",", ".")
    elif "." in value:
        value = value.replace(".", "")
    elif "," in value:
        value = value.replace(",", ".")

    try:
        return float(value)
    except Exception:
        return 0


# =========================================================
# 3. CLEAN NUMBER PARTICIPANT
# =========================================================

def clean_participant_number(value):
    """
    Membersihkan angka peserta.

    Contoh:
    10
    10 peserta
    10.0
    """

    if pd.isna(value):
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if value == "":
        return 0

    value = re.sub(r"[^\d.,-]", "", value)

    try:
        return float(value.replace(",", "."))
    except Exception:
        return 0


# =========================================================
# 4. EXTRACT FINANCIAL PERFORMANCE
# =========================================================

def extract_financial_performance(sheets):
    """
    Mengambil data Financial Performance dari setiap sheet.

    Yang dicari:
    - Target
    - Actual
    - Total Nilai Pengajuan
    - Saldo
    - Persentase
    """

    results = []

    if not sheets:
        return pd.DataFrame()

    for sheet_name, df in sheets.items():

        program_info = extract_program_info(sheet_name)

        if program_info is None:
            continue

        if df is None or df.empty:
            continue

        df = df.copy()

        # -------------------------------------------------
        # Cari header
        # -------------------------------------------------

        header_row = None

        for i in range(min(30, len(df))):

            row_values = df.iloc[i].tolist()

            # PERBAIKAN:
            # Semua value dipastikan menjadi string
            # agar tidak muncul error:
            # sequence item 0, expected str instance, float found

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

        if header_row is None:
            continue

        # -------------------------------------------------
        # Cari kolom
        # -------------------------------------------------

        header_values = df.iloc[header_row].tolist()

        header_values = [
            "" if pd.isna(value)
            else str(value).strip().lower()
            for value in header_values
        ]

        uraian_col = None
        nilai_col = None

        for idx, value in enumerate(header_values):

            if "uraian pengajuan" in value:
                uraian_col = idx

            if "nilai pengajuan" in value:
                nilai_col = idx

        if nilai_col is None:
            continue

        # -------------------------------------------------
        # Data setelah header
        # -------------------------------------------------

        data = df.iloc[header_row + 1:].copy()

        if data.empty:
            continue

        # -------------------------------------------------
        # TARGET
        # -------------------------------------------------

        target = 0

        # Cari baris PKS
        for _, row in data.iterrows():

            if uraian_col is not None:
                uraian = str(
                    row.iloc[uraian_col]
                ).strip().lower()

                if "pks" in uraian:

                    target = clean_number(
                        row.iloc[nilai_col]
                    )

                    if target > 0:
                        break

        # -------------------------------------------------
        # TOTAL NILAI PENGAJUAN
        # -------------------------------------------------

        total_pengajuan = 0

        for _, row in data.iterrows():

            nilai = clean_number(
                row.iloc[nilai_col]
            )

            total_pengajuan += nilai

        # -------------------------------------------------
        # ACTUAL
        # -------------------------------------------------

        actual = 0

        # Actual dihitung dari nilai setelah DPKS
        # jika struktur sheet menggunakan DPKS

        dpk_found = False

        for _, row in data.iterrows():

            uraian = ""

            if uraian_col is not None:
                uraian = str(
                    row.iloc[uraian_col]
                ).strip().lower()

            if "dpks" in uraian:
                dpk_found = True
                continue

            if dpk_found:
                nilai = clean_number(
                    row.iloc[nilai_col]
                )

                actual += nilai

        # Jika DPKS tidak ditemukan,
        # gunakan total pengajuan sebagai fallback
        if not dpk_found:
            actual = total_pengajuan

        # -------------------------------------------------
        # SALDO
        # -------------------------------------------------

        saldo = 0

        # Cari kata saldo
        saldo_values = []

        for _, row in data.iterrows():

            uraian = ""

            if uraian_col is not None:
                uraian = str(
                    row.iloc[uraian_col]
                ).strip().lower()

            if "saldo" in uraian:

                nilai = clean_number(
                    row.iloc[nilai_col]
                )

                saldo_values.append(nilai)

        if saldo_values:
            # Ambil saldo terakhir yang tidak nol
            non_zero_saldo = [
                x for x in saldo_values
                if x != 0
            ]

            if non_zero_saldo:
                saldo = non_zero_saldo[-1]
            else:
                saldo = saldo_values[-1]

        # -------------------------------------------------
        # TARGET FALLBACK
        # -------------------------------------------------

        if target == 0:
            target = total_pengajuan

        # -------------------------------------------------
        # PERSENTASE
        # -------------------------------------------------

        if target > 0:
            percentage = (
                actual / target
            ) * 100
        else:
            percentage = 0

        # -------------------------------------------------
        # SIMPAN
        # -------------------------------------------------

        results.append({
            "Program": program_info["Program"],
            "Tahun": program_info["Tahun"],
            "Bulan": program_info["Bulan"],
            "Tanggal": program_info["Tanggal"],
            "Target": target,
            "Actual": actual,
            "Total Nilai Pengajuan": total_pengajuan,
            "Saldo": saldo,
            "Persentase": percentage
        })

    if not results:
        return pd.DataFrame()

    result_df = pd.DataFrame(results)

    return result_df


# =========================================================
# 5. EXTRACT PARTICIPANT TARGET & ACTUAL
# =========================================================

def extract_participant_target(sheets):
    """
    Mengambil data peserta dari sheet:
    - SIAP
    - INSPIRASI

    Struktur:
    A = Tahun
    B = Bulan
    C = Tanggal
    G = Participant Target
    H = Participant Actual

    Header berada di Excel row 3-4,
    sehingga data dimulai dari iloc[4].
    """

    results = []

    if not sheets:
        return pd.DataFrame()

    for sheet_name in ["SIAP", "INSPIRASI"]:

        if sheet_name not in sheets:
            continue

        df = sheets[sheet_name].copy()

        if df is None or df.empty:
            continue

        # Data dimulai Excel row 5
        data = df.iloc[4:].copy()

        if data.empty:
            continue

        for _, row in data.iterrows():

            # Pastikan minimal 8 kolom
            if len(row) < 8:
                continue

            tahun = pd.to_numeric(
                row.iloc[0],
                errors="coerce"
            )

            bulan = pd.to_numeric(
                row.iloc[1],
                errors="coerce"
            )

            tanggal = pd.to_numeric(
                row.iloc[2],
                errors="coerce"
            )

            target = clean_participant_number(
                row.iloc[6]
            )

            actual = clean_participant_number(
                row.iloc[7]
            )

            if pd.isna(tahun) or pd.isna(bulan):
                continue

            if pd.isna(tanggal):
                continue

            # Jika semuanya kosong / nol,
            # tidak perlu dimasukkan
            if target == 0 and actual == 0:
                continue

            results.append({
                "Program": sheet_name,
                "Tahun": int(tahun),
                "Bulan": int(bulan),
                "Tanggal": int(tanggal),
                "Target": target,
                "Actual": actual
            })

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(results)


# =========================================================
# 6. GRAFIK FINANCIAL PERFORMANCE
# =========================================================

def create_financial_chart(df):
    """
    Financial Performance:
    menggunakan BAR CHART.

    Target vs Actual ditampilkan
    sebagai batang berdampingan.
    """

    if df is None or df.empty:
        return None

    chart_df = df.copy()

    # -------------------------------------------------
    # Pastikan tipe data benar
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Buat tanggal
    # -------------------------------------------------

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

    if chart_df.empty:
        return None

    # -------------------------------------------------
    # Sorting
    # -------------------------------------------------

    chart_df = chart_df.sort_values(
        [
            "Tahun",
            "Bulan",
            "Tanggal",
            "Program"
        ]
    )

    # -------------------------------------------------
    # Bentuk data untuk Plotly
    # -------------------------------------------------

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

    # -------------------------------------------------
    # BAR CHART
    # -------------------------------------------------

    fig = px.bar(
        plot_df,
        x="Tanggal Periode",
        y="Nilai",
        color="Jenis",
        barmode="group",
        hover_data=[
            "Program"
        ],
        title="Financial Target vs Actual"
    )

    # -------------------------------------------------
    # Layout
    # -------------------------------------------------

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
# 7. GRAFIK PARTICIPANT TARGET VS ACTUAL
# =========================================================

def create_participant_chart(df):
    """
    Participant Target vs Actual:
    tetap menggunakan LINE CHART.
    """

    if df is None or df.empty:
        return None

    chart_df = df.copy()

    # -------------------------------------------------
    # Pastikan tipe data
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Buat tanggal
    # -------------------------------------------------

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

    if chart_df.empty:
        return None

    # -------------------------------------------------
    # Sorting
    # -------------------------------------------------

    chart_df = chart_df.sort_values(
        [
            "Tahun",
            "Bulan",
            "Tanggal",
            "Program"
        ]
    )

    # -------------------------------------------------
    # Data untuk Plotly
    # -------------------------------------------------

    plot_df = chart_df[
        [
            "Program",
            "Tanggal Periode",
            "Target",
            "Actual",
            "Tahun",
            "Bulan",
            "Tanggal"
        ]
    ].copy()

    plot_df = plot_df.melt(
        id_vars=[
            "Program",
            "Tanggal Periode",
            "Tahun",
            "Bulan",
            "Tanggal"
        ],
        value_vars=[
            "Target",
            "Actual"
        ],
        var_name="Jenis",
        value_name="Peserta"
    )

    # -------------------------------------------------
    # LINE CHART
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Layout
    # -------------------------------------------------

    fig.update_layout(
        xaxis_title="Periode",
        yaxis_title="Jumlah Peserta",
        legend_title="",
        hovermode="x unified"
    )

    fig.update_xaxes(
        tickformat="%b %Y"
    )

    return fig



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

#     Contoh:
#     10 -> 10
#     10.0 -> 10
#     15 -> 15
#     20 -> 20

#     Tidak menggunakan clean_number() karena titik pada
#     angka participant merupakan desimal, bukan pemisah ribuan.
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

#         # -------------------------------------------------
#         # Ambil informasi program dari nama sheet
#         # -------------------------------------------------

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

#             row_values = df.iloc[i].tolist()

#             # Pastikan SEMUA value menjadi string
#             # sehingga aman digunakan oleh join()
#             row_values = [
#                 "" if pd.isna(value)
#                 else str(value)
#                 for value in row_values
#             ]

#             row_text = " ".join(row_values).lower()

#             if (
#                 "uraian pengajuan" in row_text
#                 and
#                 "nilai pengajuan" in row_text
#             ):
#                 header_row = i
#                 break

#         # Kalau header tidak ditemukan
#         if header_row is None:
#             continue

#         # -------------------------------------------------
#         # Data dimulai setelah header
#         # -------------------------------------------------

#         data = df.iloc[header_row + 1:].copy()

#         if data.empty:
#             continue

#         # -------------------------------------------------
#         # Cari posisi kolom
#         # -------------------------------------------------

#         raw_headers = df.iloc[header_row].tolist()

#         headers = [
#             "" if pd.isna(value)
#             else str(value).strip().lower()
#             for value in raw_headers
#         ]

#         uraian_col = None
#         nilai_col = None
#         saldo_col = None

#         for col_index, header in enumerate(headers):

#             if "uraian pengajuan" in header:
#                 uraian_col = col_index

#             if "nilai pengajuan" in header:
#                 nilai_col = col_index

#             if "saldo" in header:
#                 saldo_col = col_index

#         # -------------------------------------------------
#         # Kolom wajib tidak ditemukan
#         # -------------------------------------------------

#         if uraian_col is None or nilai_col is None:
#             continue

#         # =================================================
#         # CARI PKS
#         # =================================================

#         target = 0

#         for _, row in data.iterrows():

#             if len(row) <= uraian_col:
#                 continue

#             uraian_value = row.iloc[uraian_col]

#             if pd.isna(uraian_value):
#                 uraian = ""
#             else:
#                 uraian = str(
#                     uraian_value
#                 ).strip().upper()

#             # -------------------------------------------------
#             # Jika menemukan PKS
#             # -------------------------------------------------

#             if "PKS" in uraian:

#                 # Prioritas pertama:
#                 # ambil dari kolom Saldo
#                 if (
#                     saldo_col is not None
#                     and len(row) > saldo_col
#                 ):

#                     target = clean_number(
#                         row.iloc[saldo_col]
#                     )

#                 # Kalau Saldo 0/kosong,
#                 # gunakan Nilai Pengajuan
#                 if target == 0:

#                     if len(row) > nilai_col:

#                         target = clean_number(
#                             row.iloc[nilai_col]
#                         )

#                 # Kalau sudah mendapatkan target,
#                 # berhenti mencari PKS
#                 if target > 0:
#                     break

#         # =================================================
#         # CARI DPKS
#         # =================================================

#         actual = 0

#         found_dpks = False

#         for _, row in data.iterrows():

#             if len(row) <= uraian_col:
#                 continue

#             uraian_value = row.iloc[uraian_col]

#             if pd.isna(uraian_value):
#                 uraian = ""
#             else:
#                 uraian = str(
#                     uraian_value
#                 ).strip().upper()

#             # -------------------------------------------------
#             # Temukan DPKS
#             # -------------------------------------------------

#             if "DPKS" in uraian:

#                 found_dpks = True

#                 continue

#             # -------------------------------------------------
#             # Setelah DPKS,
#             # semua Nilai Pengajuan dijumlahkan
#             # sebagai Actual
#             # -------------------------------------------------

#             if found_dpks:

#                 if len(row) > nilai_col:

#                     nilai = clean_number(
#                         row.iloc[nilai_col]
#                     )

#                     actual += nilai

#         # -------------------------------------------------
#         # Kalau DPKS tidak ditemukan
#         # -------------------------------------------------

#         if not found_dpks:
#             actual = 0

#         # =================================================
#         # TOTAL PENGAJUAN
#         # =================================================

#         total_pengajuan = 0

#         for _, row in data.iterrows():

#             if len(row) > nilai_col:

#                 nilai = clean_number(
#                     row.iloc[nilai_col]
#                 )

#                 total_pengajuan += nilai

#         # =================================================
#         # SALDO TERAKHIR
#         # =================================================

#         saldo_terakhir = 0

#         if saldo_col is not None:

#             for _, row in data.iterrows():

#                 if len(row) > saldo_col:

#                     saldo = clean_number(
#                         row.iloc[saldo_col]
#                     )

#                     if saldo != 0:
#                         saldo_terakhir = saldo

#         # =================================================
#         # PERCENTAGE
#         # =================================================

#         if target > 0:

#             percentage = (
#                 actual / target
#             ) * 100

#         else:

#             percentage = 0

#         # =================================================
#         # SIMPAN RECORD
#         # =================================================

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

#     # =====================================================
#     # BUAT DATAFRAME
#     # =====================================================

#     result = pd.DataFrame(records)

#     if result.empty:
#         return result

#     # -----------------------------------------------------
#     # Pastikan kolom numeric
#     # -----------------------------------------------------

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

#     # -----------------------------------------------------
#     # Urutkan data
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
#         # Data dimulai dari Excel baris 5
#         # Python index = 4
#         # -------------------------------------------------

#         data = df.iloc[4:].copy()

#         current_year = None
#         current_month = None

#         for _, row in data.iterrows():

#             # -------------------------------------------------
#             # Minimal 8 kolom
#             # -------------------------------------------------

#             if len(row) < 8:
#                 continue

#             # =================================================
#             # TAHUN
#             # =================================================

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

#             # =================================================
#             # BULAN
#             # =================================================

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

#                     # -----------------------------------------
#                     # Jika bulan berupa angka
#                     # -----------------------------------------

#                     try:

#                         current_month = int(
#                             float(month_text)
#                         )

#                     except (ValueError, TypeError):

#                         # -------------------------------------
#                         # Jika bulan berupa nama
#                         # -------------------------------------

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
#                             "MAY": 5,
#                             "JUNE": 6,
#                             "JULY": 7,
#                             "AUGUST": 8,
#                             "OCTOBER": 10,
#                             "NOVEMBER": 11,
#                             "DECEMBER": 12
#                         }

#                         current_month = month_map.get(
#                             month_text.upper()
#                         )

#             # -------------------------------------------------
#             # Tahun / bulan belum tersedia
#             # -------------------------------------------------

#             if current_year is None:
#                 continue

#             if current_month is None:
#                 continue

#             # =================================================
#             # TANGGAL
#             # =================================================

#             date_value = row.iloc[DATE_COL]

#             if pd.isna(date_value):
#                 continue

#             date_number = None

#             # -------------------------------------------------
#             # Jika Excel memberikan angka
#             # -------------------------------------------------

#             if isinstance(
#                 date_value,
#                 (int, float)
#             ):

#                 if not pd.isna(date_value):

#                     date_number = int(
#                         date_value
#                     )

#             # -------------------------------------------------
#             # Jika berupa teks
#             # -------------------------------------------------

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

#                 # ---------------------------------------------
#                 # Coba parse tanggal
#                 # ---------------------------------------------

#                 parsed_date = pd.to_datetime(
#                     date_text,
#                     errors="coerce"
#                 )

#                 if not pd.isna(parsed_date):

#                     date_number = int(
#                         parsed_date.day
#                     )

#                 else:

#                     # -----------------------------------------
#                     # Coba sebagai angka
#                     # -----------------------------------------

#                     try:

#                         date_number = int(
#                             float(date_text)
#                         )

#                     except (ValueError, TypeError):
#                         continue

#             # -------------------------------------------------
#             # Validasi tanggal
#             # -------------------------------------------------

#             if date_number is None:
#                 continue

#             if date_number < 1 or date_number > 31:
#                 continue

#             # =================================================
#             # TARGET & ACTUAL
#             # =================================================

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

#             # =================================================
#             # PERCENTAGE
#             # =================================================

#             if target > 0:

#                 percentage = (
#                     actual / target
#                 ) * 100

#             else:

#                 percentage = 0

#             # =================================================
#             # SIMPAN RECORD
#             # =================================================

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
#     # Urutkan
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
#     # Pastikan numeric
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

#     chart_df = chart_df.dropna(
#         subset=["Tanggal Periode"]
#     )

#     chart_df = chart_df.sort_values(
#         [
#             "Tahun",
#             "Bulan",
#             "Tanggal",
#             "Program"
#         ]
#     )

#     # =====================================================
#     # LONG FORMAT
#     # =====================================================

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

#     # =====================================================
#     # LINE CHART
#     # =====================================================

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
#     # Pastikan numeric
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
#     # Urutkan
#     # -----------------------------------------------------

#     chart_df = chart_df.sort_values(
#         [
#             "Program",
#             "Tahun",
#             "Bulan",
#             "Tanggal"
#         ]
#     )

#     # =====================================================
#     # AMBIL DATA TERAKHIR SETIAP BULAN
#     # =====================================================

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

#     # =====================================================
#     # MAPPING NAMA BULAN
#     # =====================================================

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

#     # =====================================================
#     # BUAT TANGGAL PERIODE
#     # =====================================================

#     monthly_df["Tanggal Periode"] = pd.to_datetime(
#         dict(
#             year=monthly_df["Tahun"].astype(int),
#             month=monthly_df["Bulan"].astype(int),
#             day=1
#         ),
#         errors="coerce"
#     )

#     monthly_df = monthly_df.dropna(
#         subset=["Tanggal Periode"]
#     )

#     monthly_df = monthly_df.sort_values(
#         [
#             "Program",
#             "Tanggal Periode"
#         ]
#     )

#     # =====================================================
#     # LONG FORMAT
#     # =====================================================

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

#     # =====================================================
#     # LINE CHART
#     # =====================================================

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
