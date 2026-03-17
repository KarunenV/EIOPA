# import feedparser
import pandas as pd
from datetime import datetime
from dateutil import parser as dateparser
import feedparser
import toml

## Local imports
from download_handler import download_file
from local_data_handling import edit_local_Excel

def main():
    # Load config
    config = toml.load("config.toml")
    # Parse RSS
    print(f"Fetching RSS feed…")
    feed = feedparser.parse(config["rss_url"])

    for entry in feed.entries:
        links = entry.get("links", [])

        for link in links:
            href = link.get("href", "")
            if href.lower().endswith(".zip"):
                print(f"Found ZIP link: {href}")
                try:
                    zip_data = download_file(href, config)
                    stored_data = edit_local_Excel(zip_data, config)
                except Exception as e:
                    print(f"Failed to process {href} → {str(e)}")

if __name__ == "__main__":
    main()