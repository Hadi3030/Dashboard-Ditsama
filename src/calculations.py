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

    for sheet_name, df in sheets.items():

        # =================================================
        # BACA INFORMASI PROGRAM DARI NAMA SHEET
        # =================================================

        info = extract_program_info(
            sheet_name
        )

        if info is None:
            continue

        # =================================================
        # COPY DATAFRAME
        # =================================================

        df = df.copy()

        # =================================================
        # BERSIHKAN HEADER
        # =================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
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

            if "uraian" in col_clean:

                uraian_col = col

            if "nilai pengajuan" in col_clean:

                pengajuan_col = col

            if "saldo" in col_clean:

                saldo_col = col

        # =================================================
        # TARGET / NILAI PKS
        # =================================================

        target = 0

        if uraian_col is not None:

            target_rows = df[
                df[uraian_col]
                .astype(str)
                .str.contains(
                    "nilai pks",
                    case=False,
                    na=False
                )
            ]

            if not target_rows.empty:

                row = target_rows.iloc[0]

                for value in row:

                    number = clean_number(
                        value
                    )

                    if number > target:

                        target = number

        # =================================================
        # TOTAL NILAI PENGAJUAN
        # =================================================

        total_pengajuan = 0

        if (
            uraian_col is not None
            and
            pengajuan_col is not None
        ):

            actual_rows = df[
                ~df[uraian_col]
                .astype(str)
                .str.contains(
                    "nilai pks",
                    case=False,
                    na=False
                )
            ]

            for value in actual_rows[
                pengajuan_col
            ]:

                total_pengajuan += (
                    clean_number(value)
                )

        # =================================================
        # SALDO TERAKHIR
        # =================================================

        saldo_terakhir = 0

        if saldo_col is not None:

            saldo_values = []

            for value in df[
                saldo_col
            ]:

                number = clean_number(
                    value
                )

                if number != 0:

                    saldo_values.append(
                        number
                    )

            if saldo_values:

                saldo_terakhir = (
                    saldo_values[-1]
                )

        # =================================================
        # PERSENTASE
        # =================================================

        if target > 0:

            percentage = (
                total_pengajuan
                / target
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
    # PEMBERSIHAN TERAKHIR NAMA PROGRAM
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
                r"</?\s*[a-zA-Z][^>]*",
                "",
                regex=True
            )
            .str.split(
                "<"
            )
            .str[0]
            .str.strip()
        )

        # Hapus baris program kosong
        result_df = result_df[
            result_df["Program"] != ""
        ]

    return result_df


# =========================================================
# FORMAT RUPIAH
# =========================================================

def format_rupiah(value):

    if value >= 1_000_000_000:

        return (
            f"Rp {value / 1_000_000_000:.1f} M"
        )

    elif value >= 1_000_000:

        return (
            f"Rp {value / 1_000_000:.1f} Jt"
        )

    elif value >= 1_000:

        return (
            f"Rp {value / 1_000:.1f} Rb"
        )

    else:

        return (
            f"Rp {value:,.0f}"
        )


# =========================================================
# FINANCIAL CHART
# =========================================================

def create_financial_chart(df):

    fig = go.Figure()

    # =====================================================
    # TOTAL NILAI PENGAJUAN
    # =====================================================

    fig.add_trace(
        go.Bar(

            name="Total Nilai Pengajuan",

            x=df["Program"],

            y=df["Total Pengajuan"],

            text=[
                format_rupiah(x)
                for x in df[
                    "Total Pengajuan"
                ]
            ],

            textposition="outside",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Total Nilai Pengajuan: "
                "Rp %{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    # =====================================================
    # SALDO TERAKHIR
    # =====================================================

    fig.add_trace(
        go.Bar(

            name="Saldo Terakhir",

            x=df["Program"],

            y=df["Saldo Terakhir"],

            text=[
                format_rupiah(x)
                for x in df[
                    "Saldo Terakhir"
                ]
            ],

            textposition="outside",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Saldo Terakhir: "
                "Rp %{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        title=dict(

            text="Financial Performance",

            font=dict(
                size=20,
                color="#17365D"
            )
        ),

        xaxis=dict(

            title=dict(

                text="Nama Program",

                font=dict(
                    size=14,
                    color="#17365D"
                )
            ),

            tickfont=dict(
                size=12,
                color="#17365D"
            )
        ),

        yaxis=dict(

            title=dict(

                text="Total (Rupiah)",

                font=dict(
                    size=14,
                    color="#17365D"
                )
            ),

            tickfont=dict(
                size=12,
                color="#17365D"
            ),

            tickformat=","
        ),

        barmode="group",

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(
            color="#17365D"
        ),

        legend=dict(

            title=dict(

                text="Keterangan",

                font=dict(
                    color="#17365D"
                )
            ),

            font=dict(
                color="#17365D",
                size=12
            )
        ),

        margin=dict(
            l=80,
            r=40,
            t=90,
            b=100
        )
    )

    return fig
