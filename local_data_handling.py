import zipfile
import io
import os
import pandas as pd
from dateutil import parser as dateparser
import re

# ------------- CONFIG -------------
RSS_URL = "https://www.eiopa.europa.eu/feed/53/rss_en"
OUTPUT_DIR = "output_data"
TARGET_SHEET = "RFR_spot_no_VA"
COLUMN_FILTER = ["Euro", "United Kingdom", "United States"]

# ----------------------------------

def process_zip(content: bytes, published_date: str):
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for fname in zf.namelist():
            if fname.endswith("_Term_Structures.xlsx"):
                print(f" → Processing Excel {fname}")

                file = zf.open(fname)
                df = pd.read_excel(file, sheet_name=TARGET_SHEET, header=1, engine="openpyxl")
                
                # Filter columns that contain "EUR" in the header
                eur_cols = [c for c in df.columns if COLUMN_FILTER[0].lower() in str(c).lower()]
                if not eur_cols:
                    print(f"   ⚠️ No EUR columns found in {fname}")
                    continue

                df_filtered = df[eur_cols].copy()


                first_col_val = str(df_filtered.iloc[0, 0])
                match = re.search(r'(\d{2}_\d{2}_\d{4})', first_col_val)
                published_date = match.group(1).replace('_', '-') if match else ""

                # Insert date row at the top
                date_obj = dateparser.parse(published_date)
                date_str = date_obj.strftime("%m-%Y")

                # Create a one-row date DataFrame aligned to filtered columns
                date_row = pd.DataFrame([pd.Series([date_str] * len(df_filtered.columns), index=df_filtered.columns)])

                # Prepend the date row to the filtered data
                df_out = pd.concat([date_row, df_filtered], ignore_index=True)

                # Save to own spreadsheet
                os.makedirs(OUTPUT_DIR, exist_ok=True)
                out_name = os.path.join(OUTPUT_DIR, 'Euro.xlsx')

                # Use write mode for first creation, append/replace for existing workbook
                # export without header to make first cell the date value instead of column label
                if not os.path.exists(out_name):
                    df_out.to_excel(out_name, sheet_name=TARGET_SHEET, index=False, header=False, startcol=0, engine="openpyxl")
                else:
                    with pd.ExcelWriter(out_name, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                        df_out.to_excel(writer, sheet_name=TARGET_SHEET, index=False, header=False, startcol=0)

                print(f"   ✔ Saved to {out_name}")
