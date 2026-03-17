import requests
import zipfile
import io   
import os
import pandas as pd
from dateutil import parser as dateparser
import re

def download_file(url: str, config: dict) -> bytes:
    print(f"Downloading: {url}")
    res = requests.get(url)
    res.raise_for_status()
    return process_zip(res.content, config)

def process_zip(content: bytes, config: dict):
    """
    Processes all _Term_Structures.xlsx files inside the ZIP.
    Returns a dictionary with keys like:
    { "Euro_with_VA": df, "Euro_no_VA": df, ... }
    """
    TARGET_SHEETS = config.get("target_sheets", [])
    finances = config.get("finances", [])
    results = {}
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for fname in zf.namelist():
            if "_Term_Structures" in fname:
                print(f" → Processing Excel {fname}")

                file = zf.open(fname)
                xl = pd.ExcelFile(file, engine="openpyxl")
                available_sheets = xl.sheet_names

                # Match target sheets exactly or with optional _UP suffix
                matched_sheets = []
                for target in TARGET_SHEETS:
                    for sheet in available_sheets:
                        if sheet == target or sheet.startswith(f"{target}_"):
                            matched_sheets.append(sheet)

                if not matched_sheets:
                    print(f"   ⚠️ No target sheets found in {fname}")
                    continue

                for sheet in matched_sheets:
                    df = pd.read_excel(xl, sheet_name=sheet, header=1)

                    for finance in finances:
                        # Filter columns that contain "EUR" in the header
                        fin_cols = [c for c in df.columns if finance.lower() in str(c).lower()]
                        if not fin_cols:
                            print(f"   ⚠️ No {finance} columns found in {fname}")
                            continue

                        df_filtered = df[fin_cols].copy()

                        first_col_val = str(df_filtered.iloc[0, 0])
                        match = re.search(r'(\d{2}_\d{1,2}_\d{4})', first_col_val)
                        published_date = match.group(1).replace('_', '-') if match else ""

                        # Insert date row at the top
                        date_obj = dateparser.parse(published_date)
                        date_str = date_obj.strftime("%m-%Y")

                        # Create a one-row date DataFrame aligned to filtered columns
                        date_row = pd.DataFrame([pd.Series([date_str] * len(df_filtered.columns), index=df_filtered.columns)])

                        # Prepend the date row to the filtered data
                        results[f"{finance}_{target}"] = pd.concat([date_row, df_filtered], ignore_index=True)

    return results