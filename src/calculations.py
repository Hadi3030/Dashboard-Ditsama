import pandas as pd


def load_excel_sheets(url):

    spreadsheet_id = url.split("/d/")[1].split("/")[0]

    # Daftar sheet yang sementara digunakan
    sheet_names = [
        "DITSAMA.PM-3-6-2026-SIAP"
    ]

    sheets = {}

    for sheet_name in sheet_names:

        csv_url = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{spreadsheet_id}/gviz/tq"
            f"?tqx=out:csv"
            f"&sheet={sheet_name}"
        )

        df = pd.read_csv(csv_url)

        sheets[sheet_name] = df

    return sheets
