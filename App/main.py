# import feedparser
import os
import re
import pandas as pd
from datetime import datetime
from dateutil import parser as dateparser
import feedparser
import toml
import calendar

## Local imports
from download_handler import download_file, process_zip
from local_data_handling import edit_local_Excel

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}

def month_key(dt):
    return (dt.year, dt.month)

def month_diff(d1, d2):
    return (d1.year - d2.year) * 12 + (d1.month - d2.month)

def extract_date(filename):
    filename_lower = filename.lower()

    # Find year (4 digits)
    year_match = re.search(r"(19|20)\d{2}", filename_lower)
    if not year_match:
        return None

    year = int(year_match.group())

    # Find month name
    for month_name, month_number in MONTHS.items():
        if month_name in filename_lower:
            last_day = calendar.monthrange(year, month_number)[1]
            return datetime(year, month_number, last_day)

    return None
def main():
    # Load config
    config = toml.load("config.toml")

    # # Parse RSS
    feed = feedparser.parse(config["rss_url"])

    for entry in feed.entries:
        links = entry.get("links", [])
        title = entry.get("title", "No Title")

        for link in links:
            href = link.get("href", "")
            if href.lower().endswith(".zip"):
                print(f"Found ZIP link, under {title}: {href}")
                
                try:
                    zip_data = download_file(href, config, extract_date(title))
                    edit_local_Excel(zip_data, config)
                except Exception as e:
                    print(f"Failed to process {href} → {str(e)}")

    # Parse local files 
    manual_dir =  "ManualZippedFiles"

    if not os.path.isdir(manual_dir):
        print(f"Manual directory not found: {manual_dir}")
        return

    zip_files = [os.path.join(manual_dir, f) for f in os.listdir(manual_dir) if f.lower().endswith(".zip")]

    dated_files = []

    for f in zip_files:
        dt = extract_date(f)
        if not dt:
            print(f"WARNING: Could not extract date from filename → {f}")
            continue
        dated_files.append((f, dt))

    # ---- Remove duplicates (same month + year) ----
    unique = {}
    for f, dt in dated_files:
        key = month_key(dt)
        if key in unique:
            print(f"WARNING: Duplicate month found, removing → {f}")
        else:
            unique[key] = (f, dt)

    sorted_files = sorted(
        unique.values(),
        key=lambda x: x[1],
        reverse=True
    )

    # ---- Check for missing months ----
    for i in range(len(sorted_files) - 1):
        current_dt = sorted_files[i][1]
        next_dt = sorted_files[i + 1][1]

        if month_diff(current_dt, next_dt) > 1:
            print(
                f"WARNING: Missing month between "
                f"{current_dt.strftime('%B %Y')} and "
                f"{next_dt.strftime('%B %Y')}"    
            )
            answer = input("Do you wish to continue? (y/n): ").strip().lower()
            if answer.lower() != "n":
                print("Stopping.")
                return  

    for f,_ in sorted_files:   
        print(f"Found local ZIP file: {f}")
        try:
            with open(f, "rb") as file:
                content = file.read()
            zip_data = process_zip(content, config, extract_date(f))
            edit_local_Excel(zip_data, config, usingLocalFiles=True)
        except Exception as e:
            print(f"Failed to process {f} → {e}")



if __name__ == "__main__":
    main()