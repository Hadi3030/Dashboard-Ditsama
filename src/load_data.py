import pandas as pd
import requests
import re
from io import StringIO


def get_spreadsheet_id(url):
    """
    Mengambil ID Google Spreadsheet dari URL.
    """

    match = re.search(
        r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
        url
    )

    if not match:
        raise ValueError(
            "URL Google Sheets tidak valid."
        )

    return match.group(1)


def get_sheet_data(
    spreadsheet_id,
    sheet_name
):
    """
    Membaca satu sheet Google Sheets.
    """

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/gviz/tq"
        f"?tqx=out:csv"
        f"&sheet={sheet_name}"
    )

    response = requests.get(url)

    response.raise_for_status()

    return pd.read_csv(
        StringIO(response.text)
    )


def load_all_sheets(url):
    """
    Membaca seluruh sheet yang tersedia
    dari satu Google Spreadsheet.

    Hanya sheet dengan format:

    DITSAMA.PM-3-6-2026-SIAP

    yang akan diproses.
    """

    spreadsheet_id = get_spreadsheet_id(url)

    # ==========================================
    # AMBIL HALAMAN GOOGLE SHEETS
    # ==========================================

    html_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/edit"
    )

    response = requests.get(html_url)

    response.raise_for_status()

    html = response.text

    # ==========================================
    # CARI NAMA SHEET
    # ==========================================

    sheet_names = re.findall(
        r'DITSAMA\.PM-[0-9]+-[0-9]+-[0-9]{4}-[^"]+',
        html
    )

    # Hilangkan duplikasi
    sheet_names = list(
        dict.fromkeys(sheet_names)
    )

    sheets = {}

    # ==========================================
    # BACA SETIAP SHEET
    # ==========================================

    for sheet_name in sheet_names:

        try:

            df = get_sheet_data(
                spreadsheet_id,
                sheet_name
            )

            sheets[sheet_name] = df

        except Exception:
            continue

    return sheets
