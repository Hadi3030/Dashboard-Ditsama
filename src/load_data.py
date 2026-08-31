import pandas as pd
from pathlib import Path


DATA_FOLDER = Path("data")


def load_excel_file(file_path):

    return pd.read_excel(file_path)


def load_all_data():

    files = list(DATA_FOLDER.glob("*.xlsx"))

    data = {}

    for file in files:

        data[file.stem] = pd.read_excel(file)

    return data
