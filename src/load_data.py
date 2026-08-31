import pandas as pd


def get_sheet_data(spreadsheet_id, sheet_name):
    """
    Membaca satu sheet Google Sheets sebagai DataFrame.
    """

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/gviz/tq"
        f"?tqx=out:csv&sheet={sheet_name}"
    )

    return pd.read_csv(url)


def get_all_sheets(spreadsheet_id):
    """
    Mengambil daftar nama sheet dari Google Sheets.
    """

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/edit"
    )

    # Daftar sheet akan kita masukkan/ambil secara otomatis
    # setelah koneksi spreadsheet berhasil.
    return url
