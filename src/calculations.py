import pandas as pd
import plotly.graph_objects as go


def extract_financial_performance(sheets):

    results = []

    for sheet_name, df in sheets.items():

        # ==================================
        # NAMA PROGRAM
        # ==================================

        program = sheet_name.split("-")[-1].strip()

        # ==================================
        # BERSIHKAN NAMA KOLOM
        # ==================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        # ==================================
        # TARGET
        # Target = Nilai PKS
        # ==================================

        target = 0

        if "Uraian Pengajuan" in df.columns:

            target_row = df[
                df["Uraian Pengajuan"]
                .astype(str)
                .str.contains(
                    "Nilai PKS",
                    case=False,
                    na=False
                )
            ]

            if not target_row.empty:

                row = target_row.iloc[0]

                for value in row:

                    try:

                        number = pd.to_numeric(
                            value,
                            errors="coerce"
                        )

                        if pd.notna(number):
                            target = max(
                                target,
                                float(number)
                            )

                    except Exception:
                        pass

        # ==================================
        # ACTUAL
        # Total Nilai Pengajuan
        # ==================================

        actual = 0

        if (
            "Uraian Pengajuan" in df.columns
            and
            "Nilai Pengajuan" in df.columns
        ):

            actual_data = df[
                ~df["Uraian Pengajuan"]
                .astype(str)
                .str.contains(
                    "Nilai PKS",
                    case=False,
                    na=False
                )
            ]

            actual = pd.to_numeric(
                actual_data["Nilai Pengajuan"],
                errors="coerce"
            ).fillna(0).sum()

        # ==================================
        # SIMPAN
        # ==================================

        results.append({
            "Program": program,
            "Target": target,
            "Actual": actual
        })

    return pd.DataFrame(results)


# ==========================================
# FINANCIAL PERFORMANCE CHART
# ==========================================

def create_financial_chart(df):

    fig = go.Figure()

    # TARGET
    fig.add_trace(
        go.Bar(
            name="Target",
            x=df["Program"],
            y=df["Target"],
            text=df["Target"],
            texttemplate="Rp %{text:,.0f}",
            textposition="outside"
        )
    )

    # ACTUAL
    fig.add_trace(
        go.Bar(
            name="Actual",
            x=df["Program"],
            y=df["Actual"],
            text=df["Actual"],
            texttemplate="Rp %{text:,.0f}",
            textposition="outside"
        )
    )

    fig.update_layout(
        title="Financial Performance",

        xaxis_title="Nama Program",

        yaxis_title="Total (Rp)",

        barmode="group",

        plot_bgcolor="white",

        paper_bgcolor="white",

        font=dict(
            color="#17365D"
        ),

        legend=dict(
            title="Keterangan"
        ),

        yaxis=dict(
            tickformat=","
        ),

        margin=dict(
            l=50,
            r=30,
            t=70,
            b=50
        )
    )

    return fig
