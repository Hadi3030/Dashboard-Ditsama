```python
import pandas as pd
import plotly.graph_objects as go
import re


# =========================================================
# MEMBACA FORMAT NAMA SHEET
# Contoh:
# DITSAMA.PM-3-6-2026-SIAP
#
# 3    = tanggal
# 6    = bulan
# 2026 = tahun
# SIAP = nama program
# =========================================================

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


# =========================================================
# MEMBERSIHKAN ANGKA RUPIAH
# =========================================================

def clean_number(value):

    if pd.isna(value):
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value)

    value = value.replace("Rp", "")
    value = value.replace(" ", "")

    # Format angka Indonesia
    # Contoh:
    # 1.068.000.000
    # menjadi:
    # 1068000000

    value = value.replace(".", "")

    # Jika ada koma
    value = value.replace(",", ".")

    try:
        return float(value)

    except:
        return 0


# =========================================================
# FINANCIAL PERFORMANCE
#
# Batang 1:
# TOTAL NILAI PENGAJUAN
#
# Batang 2:
# SISA SALDO TERAKHIR
# =========================================================

def extract_financial_performance(sheets):

    results = []

    # Loop semua sheet
    for sheet_name, df in sheets.items():

        # =================================================
        # CEK NAMA SHEET
        # =================================================

        info = extract_program_info(
            sheet_name
        )

        # Kalau nama sheet tidak sesuai format,
        # lewati sheet tersebut

        if info is None:
            continue

        # =================================================
        # BERSIHKAN NAMA KOLOM
        # =================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        # =================================================
        # CARI KOLOM SECARA OTOMATIS
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

            elif "nilai pengajuan" in col_clean:

                pengajuan_col = col

            elif "saldo" in col_clean:

                saldo_col = col

        # =================================================
        # TOTAL NILAI PENGAJUAN
        # =================================================

        total_pengajuan = 0

        if pengajuan_col:

            data_pengajuan = df.copy()

            # Jangan memasukkan baris "Nilai PKS"
            # karena itu bukan transaksi pengajuan

            if uraian_col:

                data_pengajuan = data_pengajuan[
                    ~data_pengajuan[
                        uraian_col
                    ]
                    .astype(str)
                    .str.contains(
                        "nilai pks",
                        case=False,
                        na=False
                    )
                ]

            # Jumlahkan seluruh Nilai Pengajuan

            total_pengajuan = (
                data_pengajuan[
                    pengajuan_col
                ]
                .apply(clean_number)
                .sum()
            )

        # =================================================
        # SISA SALDO TERAKHIR
        # =================================================

        saldo_terakhir = 0

        if saldo_col:

            saldo_values = (
                df[saldo_col]
                .apply(clean_number)
            )

            # Buang nilai kosong / 0

            saldo_values = saldo_values[
                saldo_values > 0
            ]

            # Ambil saldo paling terakhir

            if not saldo_values.empty:

                saldo_terakhir = (
                    saldo_values.iloc[-1]
                )

        # =================================================
        # SIMPAN HASIL
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

            "Total Pengajuan":
                total_pengajuan,

            "Saldo Terakhir":
                saldo_terakhir
        })

    # =====================================================
    # HASIL AKHIR
    # =====================================================

    return pd.DataFrame(
        results
    )


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
# MEMBUAT GRAFIK FINANCIAL PERFORMANCE
# =========================================================

def create_financial_chart(df):

    fig = go.Figure()

    # =====================================================
    # BATANG 1
    # TOTAL NILAI PENGAJUAN
    # =====================================================

    fig.add_trace(

        go.Bar(

            name="Total Nilai Pengajuan",

            x=df["Program"],

            y=df["Total Pengajuan"],

            text=[
                format_rupiah(x)
                for x in df["Total Pengajuan"]
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
    # BATANG 2
    # SISA SALDO
    # =====================================================

    fig.add_trace(

        go.Bar(

            name="Sisa Saldo",

            x=df["Program"],

            y=df["Saldo Terakhir"],

            text=[
                format_rupiah(x)
                for x in df["Saldo Terakhir"]
            ],

            textposition="outside",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Sisa Saldo: "
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

        # -------------------------------------------------
        # SUMBU X
        # -------------------------------------------------

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

        # -------------------------------------------------
        # SUMBU Y
        # -------------------------------------------------

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

        # -------------------------------------------------
        # DUA BATANG BERDAMPINGAN
        # -------------------------------------------------

        barmode="group",

        # -------------------------------------------------
        # BACKGROUND
        # -------------------------------------------------

        plot_bgcolor="white",

        paper_bgcolor="white",

        # -------------------------------------------------
        # WARNA TEKS
        # -------------------------------------------------

        font=dict(

            color="#17365D"
        ),

        # -------------------------------------------------
        # LEGEND
        # -------------------------------------------------

        legend=dict(

            title=dict(

                text="Keterangan",

                font=dict(

                    color="#17365D",

                    size=13
                )
            ),

            font=dict(

                color="#17365D",

                size=12
            )
        ),

        # -------------------------------------------------
        # MARGIN
        # -------------------------------------------------

        margin=dict(

            l=80,

            r=40,

            t=90,

            b=80
        )
    )

    return fig
