import pandas as pd
import plotly.graph_objects as go
import re


def extract_program_info(sheet_name):

    pattern = (
        r"DITSAMA\.PM-"
        r"(\d+)-"
        r"(\d+)-"
        r"(\d{4})-"
        r"(.+)"
    )

    match = re.match(
        pattern,
        sheet_name
    )

    if not match:
        return None

    tanggal = int(match.group(1))
    bulan = int(match.group(2))
    tahun = int(match.group(3))
    program = match.group(4).strip()

    return {
        "Tanggal": tanggal,
        "Bulan": bulan,
        "Tahun": tahun,
        "Program": program
    }


def clean_number(value):

    if pd.isna(value):
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value)

    # Hilangkan Rp
    value = value.replace(
        "Rp",
        ""
    )

    # Hilangkan spasi
    value = value.replace(
        " ",
        ""
    )

    # Format Indonesia
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


def extract_financial_performance(sheets):

    results = []

    for sheet_name, df in sheets.items():

        # ==================================
        # CEK FORMAT NAMA SHEET
        # ==================================

        info = extract_program_info(
            sheet_name
        )

        if info is None:
            continue

        # ==================================
        # BERSIHKAN HEADER
        # ==================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        # ==================================
        # CARI KOLOM
        # ==================================

        uraian_col = None
        pengajuan_col = None

        for col in df.columns:

            col_clean = (
                str(col)
                .strip()
                .lower()
            )

            if "uraian" in col_clean:

                uraian_col = col

            if (
                "nilai pengajuan"
                in col_clean
            ):

                pengajuan_col = col

        # ==================================
        # TARGET
        # ==================================

        target = 0

        if uraian_col:

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

                # Cari angka terbesar
                # pada baris Nilai PKS

                for value in row:

                    number = clean_number(
                        value
                    )

                    if number > target:
                        target = number

        # ==================================
        # ACTUAL
        # ==================================

        actual = 0

        if (
            uraian_col
            and
            pengajuan_col
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

                actual += clean_number(
                    value
                )

        # ==================================
        # PERSENTASE
        # ==================================

        if target > 0:

            percentage = (
                actual / target
            ) * 100

        else:

            percentage = 0

        # ==================================
        # SIMPAN
        # ==================================

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
                actual,

            "Percentage":
                percentage
        })

    return pd.DataFrame(
        results
    )


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


def create_financial_chart(df):

    fig = go.Figure()

    # ==================================
    # TARGET
    # ==================================

    fig.add_trace(
        go.Bar(

            name="Target",

            x=df["Program"],

            y=df["Target"],

            text=[
                format_rupiah(x)
                for x in df["Target"]
            ],

            textposition="outside",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Target: Rp %{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    # ==================================
    # ACTUAL
    # ==================================

    fig.add_trace(
        go.Bar(

            name="Actual",

            x=df["Program"],

            y=df["Actual"],

            text=[
                format_rupiah(x)
                for x in df["Actual"]
            ],

            textposition="outside",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Actual: Rp %{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    # ==================================
    # LAYOUT
    # ==================================

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
            b=80
        )
    )

    return fig
