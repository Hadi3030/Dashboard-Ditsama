# def calculate_dashboard(data):

#     return {
#         "total_program": 0,
#         "progress": 0,
#         "budget_usage": 0,
#         "alert_count": 0,
#         "financial_chart": None,
#         "budget_chart": None,
#         "progress_chart": None,
#         "alerts": []
#     }

# import pandas as pd


def extract_financial_performance(sheets):

    results = []

    for sheet_name, df in sheets.items():

        # Ambil nama program dari nama sheet
        parts = sheet_name.split("-")

        if len(parts) > 0:
            program = parts[-1].strip()
        else:
            program = sheet_name

        # Cari baris Nilai PKS
        target_rows = df[
            df.astype(str)
              .apply(
                  lambda row: row.str.contains(
                      "Nilai PKS",
                      case=False,
                      na=False
                  ).any(),
                  axis=1
              )
        ]

        # Cari kolom yang kemungkinan berisi nilai
        # sementara menggunakan seluruh angka pada baris
        target = 0

        if not target_rows.empty:

            row = target_rows.iloc[0]

            numeric_values = pd.to_numeric(
                row,
                errors="coerce"
            ).dropna()

            if not numeric_values.empty:
                target = numeric_values.max()

        results.append({
            "Program": program,
            "Target": target
        })

    return pd.DataFrame(results)
