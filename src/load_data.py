import pandas as pd
import requests
import re
from io import BytesIO
from urllib.parse import quote


# =========================================================
# GET SPREADSHEET ID
# =========================================================

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


# =========================================================
# LOAD SEMUA SHEET
# =========================================================

def load_all_sheets(url):

    """
    Membaca SEMUA sheet dari Google Spreadsheet.

    Google Sheets digunakan sebagai sumber data.
    Tidak perlu upload file Excel ke GitHub.

    Hanya sheet dengan format:

        DITSAMA.PM-3-6-2026-SIAP

    yang akan diproses.
    """

    # -----------------------------------------------------
    # Ambil Spreadsheet ID
    # -----------------------------------------------------

    spreadsheet_id = get_spreadsheet_id(url)

    # -----------------------------------------------------
    # Gunakan endpoint export XLSX
    # -----------------------------------------------------

    xlsx_url = (
        "https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/export?format=xlsx"
    )

    response = requests.get(
        xlsx_url,
        timeout=30
    )

    response.raise_for_status()

    # -----------------------------------------------------
    # Baca file Excel langsung dari memory
    # -----------------------------------------------------

    excel_file = pd.ExcelFile(
        BytesIO(response.content),
        engine="openpyxl"
    )

    # -----------------------------------------------------
    # Ambil semua nama sheet
    # -----------------------------------------------------

    all_sheet_names = (
        excel_file.sheet_names
    )

    sheets = {}

    # =====================================================
    # PROSES SETIAP SHEET
    # =====================================================

    for sheet_name in all_sheet_names:

        # -------------------------------------------------
        # Pastikan nama sheet string
        # -------------------------------------------------

        sheet_name = str(
            sheet_name
        ).strip()

        # -------------------------------------------------
        # Hanya proses format:
        #
        # DITSAMA.PM-3-6-2026-SIAP
        #
        # -------------------------------------------------

        pattern = (
            r"^DITSAMA\.PM-"
            r"\d+-"
            r"\d+-"
            r"\d{4}-"
            r".+"
        )

        if not re.match(
            pattern,
            sheet_name,
            re.IGNORECASE
        ):

            continue

        # -------------------------------------------------
        # Baca sheet
        #
        # header=None sengaja digunakan karena file kamu
        # mempunyai judul/header beberapa baris di atas.
        # -------------------------------------------------

        try:

            df = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                header=None,
                engine="openpyxl"
            )

            sheets[sheet_name] = df

        except Exception as e:

            print(
                f"Gagal membaca sheet "
                f"{sheet_name}: {e}"
            )

            continue

    return sheets
