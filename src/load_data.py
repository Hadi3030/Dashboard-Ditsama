# import pandas as pd
# import requests
# import re
# from io import BytesIO
# from urllib.parse import quote


# # =========================================================
# # GET SPREADSHEET ID
# # =========================================================

# def get_spreadsheet_id(url):

#     """
#     Mengambil ID Google Spreadsheet dari URL.
#     """

#     match = re.search(
#         r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
#         url
#     )

#     if not match:

#         raise ValueError(
#             "URL Google Sheets tidak valid."
#         )

#     return match.group(1)


# # =========================================================
# # LOAD SEMUA SHEET
# # =========================================================

# def load_all_sheets(url):

#     """
#     Membaca SEMUA sheet dari Google Spreadsheet.

#     Google Sheets digunakan sebagai sumber data.
#     Tidak perlu upload file Excel ke GitHub.

#     Hanya sheet dengan format:

#         DITSAMA.PM-3-6-2026-SIAP

#     yang akan diproses.
#     """

#     # -----------------------------------------------------
#     # Ambil Spreadsheet ID
#     # -----------------------------------------------------

#     spreadsheet_id = get_spreadsheet_id(url)

#     # -----------------------------------------------------
#     # Gunakan endpoint export XLSX
#     # -----------------------------------------------------

#     xlsx_url = (
#         "https://docs.google.com/spreadsheets/d/"
#         f"{spreadsheet_id}/export?format=xlsx"
#     )

#     response = requests.get(
#         xlsx_url,
#         timeout=30
#     )

#     response.raise_for_status()

#     # -----------------------------------------------------
#     # Baca file Excel langsung dari memory
#     # -----------------------------------------------------

#     excel_file = pd.ExcelFile(
#         BytesIO(response.content),
#         engine="openpyxl"
#     )

#     # -----------------------------------------------------
#     # Ambil semua nama sheet
#     # -----------------------------------------------------

#     all_sheet_names = (
#         excel_file.sheet_names
#     )

#     sheets = {}

#     # =====================================================
#     # PROSES SETIAP SHEET
#     # =====================================================

#     for sheet_name in all_sheet_names:

#         # -------------------------------------------------
#         # Pastikan nama sheet string
#         # -------------------------------------------------

#         sheet_name = str(
#             sheet_name
#         ).strip()

#         # -------------------------------------------------
#         # Hanya proses format:
#         #
#         # DITSAMA.PM-3-6-2026-SIAP
#         #
#         # -------------------------------------------------

#         pattern = (
#             r"^DITSAMA\.PM-"
#             r"\d+-"
#             r"\d+-"
#             r"\d{4}-"
#             r".+"
#         )

#         if not re.match(
#             pattern,
#             sheet_name,
#             re.IGNORECASE
#         ):

#             continue

#         # -------------------------------------------------
#         # Baca sheet
#         #
#         # header=None sengaja digunakan karena file kamu
#         # mempunyai judul/header beberapa baris di atas.
#         # -------------------------------------------------

#         try:

#             df = pd.read_excel(
#                 excel_file,
#                 sheet_name=sheet_name,
#                 header=None,
#                 engine="openpyxl"
#             )

#             sheets[sheet_name] = df

#         except Exception as e:

#             print(
#                 f"Gagal membaca sheet "
#                 f"{sheet_name}: {e}"
#             )

#             continue

#     return sheets


# =========================================================
# LOAD DATA
# Dashboard Program Ditsama 2026
# =========================================================

import io
import requests
import pandas as pd


# =========================================================
# GOOGLE SHEETS
# =========================================================

def load_google_sheets(url):
    """
    Membaca Google Sheets sebagai file Excel.

    URL:
    Google Sheets biasa / sharing URL

    Output:
    Dictionary:
    {
        "nama_sheet": dataframe
    }

    DataFrame dibaca tanpa header agar
    struktur asli Excel tetap dipertahankan.
    """

    # -----------------------------------------------------
    # Ambil Spreadsheet ID
    # -----------------------------------------------------

    try:

        spreadsheet_id = (
            url
            .split("/d/")[1]
            .split("/")[0]
        )

    except Exception as e:

        raise ValueError(
            "URL Google Sheets tidak valid."
        ) from e


    # -----------------------------------------------------
    # URL export Excel
    # -----------------------------------------------------

    export_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/export?format=xlsx"
    )


    # -----------------------------------------------------
    # Request
    # -----------------------------------------------------

    response = requests.get(
        export_url,
        timeout=60
    )

    response.raise_for_status()


    # -----------------------------------------------------
    # Baca workbook
    # -----------------------------------------------------

    excel_file = io.BytesIO(
        response.content
    )


    # -----------------------------------------------------
    # Buka seluruh sheet
    # -----------------------------------------------------

    excel = pd.ExcelFile(
        excel_file,
        engine="openpyxl"
    )


    sheets = {}


    for sheet_name in excel.sheet_names:

        sheets[sheet_name] = pd.read_excel(
            excel,
            sheet_name=sheet_name,
            header=None
        )


    return sheets


# =========================================================
# SHAREPOINT EXCEL
# =========================================================

def load_sharepoint_excel(url):
    """
    Membaca file Excel dari SharePoint.

    File dibaca sebagai binary kemudian
    diproses menggunakan pandas/openpyxl.

    Output:
    Dictionary:
    {
        "SIAP": dataframe,
        "INSPIRASI": dataframe,
        ...
    }
    """

    # -----------------------------------------------------
    # Buat URL download
    # -----------------------------------------------------

    if "?" in url:

        download_url = (
            url + "&download=1"
        )

    else:

        download_url = (
            url + "?download=1"
        )


    # -----------------------------------------------------
    # Request ke SharePoint
    # -----------------------------------------------------

    response = requests.get(
        download_url,
        timeout=60,
        allow_redirects=True
    )

    response.raise_for_status()


    # -----------------------------------------------------
    # Validasi response
    # -----------------------------------------------------

    content_type = (
        response.headers
        .get("Content-Type", "")
        .lower()
    )


    # Jika SharePoint mengembalikan halaman HTML
    # biasanya berarti file tidak bisa diakses
    # secara anonymous/public.

    if (
        "text/html" in content_type
        and
        not response.content.startswith(
            b"PK"
        )
    ):

        raise ValueError(
            "SharePoint tidak mengembalikan "
            "file Excel. Pastikan link SharePoint "
            "dapat diakses tanpa login."
        )


    # -----------------------------------------------------
    # Baca sebagai Excel
    # -----------------------------------------------------

    excel_file = io.BytesIO(
        response.content
    )


    excel = pd.ExcelFile(
        excel_file,
        engine="openpyxl"
    )


    sheets = {}


    for sheet_name in excel.sheet_names:

        sheets[sheet_name] = pd.read_excel(
            excel,
            sheet_name=sheet_name,
            header=None
        )


    return sheets


# =========================================================
# LOAD ALL SHEETS
# =========================================================

def load_all_sheets(url):
    """
    Fungsi utama untuk membaca data.

    Fungsi ini otomatis mengenali:
    - Google Sheets
    - SharePoint Excel
    """

    url_lower = str(url).lower()


    # =====================================================
    # GOOGLE SHEETS
    # =====================================================

    if "docs.google.com/spreadsheets" in url_lower:

        return load_google_sheets(url)


    # =====================================================
    # SHAREPOINT
    # =====================================================

    if "sharepoint.com" in url_lower:

        return load_sharepoint_excel(url)


    # =====================================================
    # FORMAT TIDAK DIKENAL
    # =====================================================

    raise ValueError(
        "Sumber data tidak dikenali. "
        "Gunakan Google Sheets atau SharePoint."
    )
