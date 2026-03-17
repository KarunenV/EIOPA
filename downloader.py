import requests
# ------------- CONFIG -------------
RSS_URL = "https://www.eiopa.europa.eu/feed/53/rss_en"
OUTPUT_DIR = "output_data"
TARGET_SHEET = "RFR-spot_with_VA"
COLUMN_FILTER = "EUR"
# ----------------------------------
def download_file(url: str) -> bytes:
    print(f"Downloading: {url}")
    res = requests.get(url)
    res.raise_for_status()
    return res.content