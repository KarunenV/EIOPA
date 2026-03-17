# import feedparser
import pandas as pd
from datetime import datetime
from dateutil import parser as dateparser
import feedparser

## Local imports
from downloader import download_file
from local_data_handling import process_zip

# ------------- CONFIG -------------
RSS_URL = "https://www.eiopa.europa.eu/feed/53/rss_en"
OUTPUT_DIR = "output_data"
TARGET_SHEET = "RFR-spot_with_VA"
COLUMN_FILTER = "EUR"
# ----------------------------------

def main():
    # Parse RSS
    print(f"Fetching RSS feed…")
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries:
        links = entry.get("links", [])
        date_published = entry.get("published", entry.get("updated", ""))

        for link in links:
            href = link.get("href", "")
            if href.lower().endswith(".zip"):
                print(f"Found ZIP link: {href} (published: {date_published})")
                try:
                    zip_data = download_file(href)
                    process_zip(zip_data, date_published)
                except Exception as e:
                    print(f"Failed to process {href} → {str(e)}")

if __name__ == "__main__":
    main()