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

    tanggal = int(match.group(1))
    bulan = int(match.group(2))
    tahun = int(match.group(3))

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

    if isinstance(value, (int, float)):
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
# CREATE FINANCIAL CHART
# =========================================================

def create_financial_chart(df):

    fig = go.Figure()

    if df.empty:
        return fig

    chart_df = df.copy()

    # Pastikan angka numerik
    chart_df["Target"] = pd.to_numeric(
        chart_df["Target"],
        errors="coerce"
    ).fillna(0)

    chart_df["Actual"] = pd.to_numeric(
        chart_df["Actual"],
        errors="coerce"
    ).fillna(0)

    chart_df["Saldo Terakhir"] = pd.to_numeric(
        chart_df["Saldo Terakhir"],
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

    return fig

# =========================================================
# CREATE FINANCIAL CHART
# =========================================================

def create_financial_chart(df):

    fig = go.Figure()

    if df.empty:
        return fig

    chart_df = df.copy()

    # Pastikan angka numerik
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
    # FORMAT SUMBU Y INDONESIA
    # =====================================================

    max_value = max(
        chart_df["Target"].max(),
        chart_df["Actual"].max()
    )

    tick_step = max_value / 5

    tickvals = [
        tick_step * i
        for i in range(6)
    ]

    def format_axis(value):

        if value >= 1_000_000_000:
            angka = value / 1_000_000_000
            teks = f"{angka:.1f}".replace(".", ",")
            return f"Rp{teks} M"
    
        elif value >= 1_000_000:
            angka = value / 1_000_000
            teks = f"{angka:.0f}"
            return f"Rp{teks} Jt"
    
        elif value >= 1_000:
            angka = value / 1_000
            teks = f"{angka:.0f}"
            return f"Rp{teks} Rb"
    
        else:
            return f"Rp{value:,.0f}".replace(",", ".")
        

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
    # TERAPKAN FORMAT SUMBU Y
    # =====================================================

    fig.update_yaxes(
    tickmode="array",
    tickvals=tickvals,
    ticktext=ticktext,
    exponentformat="none",
    showexponent="none"
    )

    return fig
