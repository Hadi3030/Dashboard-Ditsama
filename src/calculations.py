import re
import pandas as pd
import plotly.express as px


# =========================================================
# 1. EXTRACT PROGRAM INFO
# =========================================================

def extract_program_info(sheet_name):
    """
    Membaca informasi dari nama sheet Financial.

    Contoh:
    DITSAMA.PM-3-6-2026-SIAP

    Artinya:
    Tanggal = 3
    Bulan   = 6
    Tahun   = 2026
    Program = SIAP
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
# 2. CLEAN NUMBER FINANCIAL
# =========================================================

def clean_number(value):
    """
    Membersihkan angka financial.

    Contoh:
    Rp 10.000.000
    10.000.000
    10.500.000,50
    """

    if pd.isna(value):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if value == "":
        return 0.0

    value = (
        value
        .replace("Rp", "")
        .replace("rp", "")
        .replace(" ", "")
    )

    # Format Indonesia:
    # 10.500.000,50
    if "." in value and "," in value:
        value = value.replace(".", "")
        value = value.replace(",", ".")

    # Format Indonesia:
    # 10.500.000
    elif "." in value:
        value = value.replace(".", "")

    # Format:
    # 10500000,50
    elif "," in value:
        value = value.replace(",", ".")

    try:
        return float(value)

    except (ValueError, TypeError):
        return 0.0


# =========================================================
# 3. CLEAN NUMBER PARTICIPANT
# =========================================================

def clean_participant_number(value):
    """
    Membersihkan angka Participant Target / Actual.

    Contoh:
    10
    10.0
    15
    20
    """

    if pd.isna(value):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if value == "":
        return 0.0

    value = value.replace(" ", "")

    try:
        value = value.replace(",", ".")

        return float(value)

    except (ValueError, TypeError):
        return 0.0


# =========================================================
# 4. EXTRACT FINANCIAL PERFORMANCE
# =========================================================

def extract_financial_performance(sheets):
    """
    Mengambil data Financial Performance.

    Output kolom:

    Program
    Tanggal
    Bulan
    Tahun
    Target
    Actual
    Total Pengajuan
    Saldo Terakhir
    Percentage
    """

    # -----------------------------------------------------
    # DEFINISI KOLOM WAJIB
    # Supaya DataFrame tidak pernah benar-benar tanpa kolom
    # -----------------------------------------------------

    output_columns = [
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

    records = []

    if not sheets:
        return pd.DataFrame(columns=output_columns)

    # =====================================================
    # LOOP SHEET
    # =====================================================

    for sheet_name, df in sheets.items():

        # =================================================
        # PROGRAM INFO
        # =================================================

        info = extract_program_info(sheet_name)

        if info is None:
            continue

        if df is None or df.empty:
            continue

        df = df.copy()

        # =================================================
        # CARI BARIS HEADER
        # =================================================

        header_row = None

        for i in range(min(len(df), 30)):

            row_values = df.iloc[i].tolist()

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

        # Jika header tidak ditemukan
        if header_row is None:
            continue

        # =================================================
        # DATA SETELAH HEADER
        # =================================================

        data = df.iloc[header_row + 1:].copy()

        if data.empty:
            continue

        # =================================================
        # CARI POSISI KOLOM
        # =================================================

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

        # Kolom wajib
        if (
            uraian_col is None
            or
            nilai_col is None
        ):
            continue

        # =================================================
        # TARGET
        # =================================================

        target = 0.0

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

            # ---------------------------------------------
            # Cari PKS
            # ---------------------------------------------

            if "PKS" in uraian:

                # Prioritas:
                # ambil target dari kolom Saldo

                if (
                    saldo_col is not None
                    and
                    len(row) > saldo_col
                ):

                    target = clean_number(
                        row.iloc[saldo_col]
                    )

                # Kalau Saldo kosong / 0,
                # gunakan Nilai Pengajuan

                if target == 0:

                    if len(row) > nilai_col:

                        target = clean_number(
                            row.iloc[nilai_col]
                        )

                if target > 0:
                    break

        # =================================================
        # ACTUAL
        # =================================================

        actual = 0.0

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

            # ---------------------------------------------
            # Temukan DPKS
            # ---------------------------------------------

            if "DPKS" in uraian:

                found_dpks = True
                continue

            # ---------------------------------------------
            # Setelah DPKS:
            # jumlahkan Nilai Pengajuan
            # ---------------------------------------------

            if found_dpks:

                if len(row) > nilai_col:

                    nilai = clean_number(
                        row.iloc[nilai_col]
                    )

                    actual += nilai

        # Jika DPKS tidak ditemukan,
        # actual = 0

        if not found_dpks:
            actual = 0.0

        # =================================================
        # TOTAL PENGAJUAN
        # =================================================

        total_pengajuan = 0.0

        for _, row in data.iterrows():

            if len(row) > nilai_col:

                nilai = clean_number(
                    row.iloc[nilai_col]
                )

                total_pengajuan += nilai

        # =================================================
        # SALDO TERAKHIR
        # =================================================

        saldo_terakhir = 0.0

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

            percentage = 0.0

        # =================================================
        # SIMPAN RECORD
        # =================================================

        records.append({

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
                actual,

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

    result = pd.DataFrame(
        records,
        columns=output_columns
    )

    # =====================================================
    # PASTIKAN SEMUA KOLOM ADA
    # =====================================================

    for col in output_columns:

        if col not in result.columns:

            if col == "Program":
                result[col] = ""

            else:
                result[col] = 0.0

    # =====================================================
    # PASTIKAN URUTAN KOLOM
    # =====================================================

    result = result[output_columns]

    # =====================================================
    # PASTIKAN NUMERIC
    # =====================================================

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

    # =====================================================
    # SORTING
    # =====================================================

    if not result.empty:

        result = result.sort_values(
            [
                "Tahun",
                "Bulan",
                "Tanggal",
                "Program"
            ]
        ).reset_index(
            drop=True
        )

    return result


# =========================================================
# 5. EXTRACT PARTICIPANT TARGET & ACTUAL
# =========================================================

def extract_participant_target(sheets):
    """
    Mengambil data peserta dari:

    - SIAP
    - INSPIRASI

    Struktur:

    A = Tahun
    B = Bulan
    C = Tanggal
    G = Participant Target
    H = Participant Actual

    Data dimulai Excel row 5
    = Python iloc[4].
    """

    output_columns = [
        "Program",
        "Tanggal",
        "Bulan",
        "Tahun",
        "Target",
        "Actual",
        "Percentage"
    ]

    records = []

    # =====================================================
    # POSISI KOLOM
    # =====================================================

    YEAR_COL = 0
    MONTH_COL = 1
    DATE_COL = 2

    TARGET_COL = 6
    ACTUAL_COL = 7

    # =====================================================
    # VALIDASI SHEETS
    # =====================================================

    if not sheets:
        return pd.DataFrame(columns=output_columns)

    # =====================================================
    # LOOP SHEET
    # =====================================================

    for sheet_name, df in sheets.items():

        sheet_name_clean = (
            str(sheet_name)
            .strip()
            .upper()
        )

        # Hanya SIAP dan INSPIRASI
        if sheet_name_clean not in [
            "SIAP",
            "INSPIRASI"
        ]:
            continue

        if df is None or df.empty:
            continue

        # =================================================
        # DATA MULAI BARIS 5
        # =================================================

        if len(df) <= 4:
            continue

        data = df.iloc[4:].copy()

        current_year = None
        current_month = None

        # =================================================
        # LOOP DATA
        # =================================================

        for _, row in data.iterrows():

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

                    except (
                        ValueError,
                        TypeError
                    ):
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
                    # Bulan berupa angka
                    # -----------------------------------------

                    try:

                        current_month = int(
                            float(month_text)
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        # -------------------------------------
                        # Bulan berupa nama
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
                            "APRIL": 4,
                            "MAY": 5,
                            "JUNE": 6,
                            "JULY": 7,
                            "AUGUST": 8,
                            "SEPTEMBER": 9,
                            "OCTOBER": 10,
                            "NOVEMBER": 11,
                            "DECEMBER": 12
                        }

                        current_month = (
                            month_map.get(
                                month_text.upper()
                            )
                        )

            # =================================================
            # VALIDASI TAHUN & BULAN
            # =================================================

            if current_year is None:
                continue

            if current_month is None:
                continue

            # Validasi bulan
            if (
                current_month < 1
                or
                current_month > 12
            ):
                continue

            # =================================================
            # TANGGAL
            # =================================================

            date_value = row.iloc[DATE_COL]

            if pd.isna(date_value):
                continue

            date_number = None

            # -------------------------------------------------
            # Jika angka
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
            # Jika teks
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

                # Coba parse tanggal
                parsed_date = pd.to_datetime(
                    date_text,
                    errors="coerce"
                )

                if not pd.isna(
                    parsed_date
                ):

                    date_number = int(
                        parsed_date.day
                    )

                else:

                    # Coba sebagai angka
                    try:

                        date_number = int(
                            float(date_text)
                        )

                    except (
                        ValueError,
                        TypeError
                    ):
                        continue

            # =================================================
            # VALIDASI TANGGAL
            # =================================================

            if date_number is None:
                continue

            if (
                date_number < 1
                or
                date_number > 31
            ):
                continue

            # =================================================
            # TARGET & ACTUAL
            # =================================================

            target_value = row.iloc[
                TARGET_COL
            ]

            actual_value = row.iloc[
                ACTUAL_COL
            ]

            target = clean_participant_number(
                target_value
            )

            actual = clean_participant_number(
                actual_value
            )

            # =================================================
            # JIKA KOSONG
            # =================================================

            if target == 0 and actual == 0:

                target_empty = (
                    pd.isna(target_value)
                    or
                    str(
                        target_value
                    ).strip() == ""
                )

                actual_empty = (
                    pd.isna(actual_value)
                    or
                    str(
                        actual_value
                    ).strip() == ""
                )

                if (
                    target_empty
                    and
                    actual_empty
                ):
                    continue

            # =================================================
            # PERCENTAGE
            # =================================================

            if target > 0:

                percentage = (
                    actual / target
                ) * 100

            else:

                percentage = 0.0

            # =================================================
            # SIMPAN
            # =================================================

            records.append({

                "Program":
                    sheet_name_clean,

                "Tanggal":
                    date_number,

                "Bulan":
                    current_month,

                "Tahun":
                    current_year,

                "Target":
                    target,

                "Actual":
                    actual,

                "Percentage":
                    percentage
            })

    # =====================================================
    # DATAFRAME
    # =====================================================

    result = pd.DataFrame(
        records,
        columns=output_columns
    )

    # =====================================================
    # PASTIKAN SEMUA KOLOM ADA
    # =====================================================

    for col in output_columns:

        if col not in result.columns:

            if col == "Program":
                result[col] = ""

            else:
                result[col] = 0.0

    # =====================================================
    # PASTIKAN URUTAN KOLOM
    # =====================================================

    result = result[output_columns]

    # =====================================================
    # NUMERIC
    # =====================================================

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

    # =====================================================
    # SORTING
    # =====================================================

    if not result.empty:

        result = result.sort_values(
            [
                "Program",
                "Tahun",
                "Bulan",
                "Tanggal"
            ]
        ).reset_index(
            drop=True
        )

    return result


# =========================================================
# 6. FINANCIAL PERFORMANCE CHART
# =========================================================

def create_financial_chart(df):
    """
    Financial Performance
    menggunakan BAR CHART.

    Target vs Actual
    ditampilkan sebagai batang.
    """

    if df is None or df.empty:
        return None

    # Pastikan kolom wajib tersedia
    required_columns = [
        "Program",
        "Tanggal",
        "Bulan",
        "Tahun",
        "Target",
        "Actual"
    ]

    for col in required_columns:

        if col not in df.columns:
            return None

    chart_df = df.copy()

    # =====================================================
    # NUMERIC
    # =====================================================

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

    # =====================================================
    # VALIDASI TANGGAL
    # =====================================================

    chart_df = chart_df[
        (
            chart_df["Tahun"] > 0
        )
        &
        (
            chart_df["Bulan"].between(1, 12)
        )
        &
        (
            chart_df["Tanggal"].between(1, 31)
        )
    ].copy()

    if chart_df.empty:
        return None

    # =====================================================
    # TANGGAL PERIODE
    # =====================================================

    chart_df["Tanggal Periode"] = pd.to_datetime(

        dict(

            year=chart_df[
                "Tahun"
            ].astype(int),

            month=chart_df[
                "Bulan"
            ].astype(int),

            day=chart_df[
                "Tanggal"
            ].astype(int)
        ),

        errors="coerce"
    )

    chart_df = chart_df.dropna(
        subset=[
            "Tanggal Periode"
        ]
    )

    if chart_df.empty:
        return None

    # =====================================================
    # SORTING
    # =====================================================

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
    # BAR CHART
    # =====================================================

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

    # =====================================================
    # LAYOUT
    # =====================================================

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
# 7. PARTICIPANT TARGET VS ACTUAL CHART
# =========================================================

def create_participant_chart(df):
    """
    Participant Target vs Actual.

    Mengambil data TERAKHIR
    pada setiap Program / Tahun / Bulan.

    Menggunakan LINE CHART.
    """

    if df is None or df.empty:
        return None

    # Pastikan kolom wajib tersedia
    required_columns = [
        "Program",
        "Tanggal",
        "Bulan",
        "Tahun",
        "Target",
        "Actual"
    ]

    for col in required_columns:

        if col not in df.columns:
            return None

    chart_df = df.copy()

    # =====================================================
    # NUMERIC
    # =====================================================

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

    # =====================================================
    # VALIDASI DATA
    # =====================================================

    chart_df = chart_df[
        (
            chart_df["Tahun"] > 0
        )
        &
        (
            chart_df["Bulan"].between(1, 12)
        )
        &
        (
            chart_df["Tanggal"].between(1, 31)
        )
    ].copy()

    if chart_df.empty:
        return None

    # =====================================================
    # SORTING
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

    if monthly_df.empty:
        return None

    # =====================================================
    # NAMA BULAN
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
        monthly_df[
            "Bulan"
        ].map(month_names)
    )

    # =====================================================
    # TANGGAL PERIODE
    # =====================================================

    monthly_df["Tanggal Periode"] = pd.to_datetime(

        dict(

            year=monthly_df[
                "Tahun"
            ].astype(int),

            month=monthly_df[
                "Bulan"
            ].astype(int),

            day=1
        ),

        errors="coerce"
    )

    monthly_df = monthly_df.dropna(
        subset=[
            "Tanggal Periode"
        ]
    )

    if monthly_df.empty:
        return None

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

    # =====================================================
    # LAYOUT
    # =====================================================

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
