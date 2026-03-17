# EIOPA

A simple Python utility to fetch EIOPA RSS data, find ZIP links, download the latest term structure Excel files, and extract EUR-related rates.

## Requirements

- Python 3.8+
- `pip` package manager
- `venv` (recommended)

## Setup

1. Clone repository.
2. Create and activate virtual environment:
   - Windows: `py -m venv venv && venv\Scripts\activate`
   - Unix: `python3 -m venv venv && source venv/bin/activate`
3. Install dependencies:
   - `pip install -r requirements.txt` (if you add one)
   - `pip install feedparser pandas python-dateutil openpyxl` (as currently used)

## Usage

1. Run `main.py`:
   - `python main.py`
2. The script:
   - reads RSS URL from `main.py`
   - finds ZIP links in feed entries
   - downloads ZIP file from first valid link
   - processes contained Excel sheet `RFR_spot_no_VA` in `local_data_handling.py`
   - writes output to `output_data/Euro.xlsx`

## Configuration

- `RSS_URL`, `OUTPUT_DIR`, `TARGET_SHEET`, and `COLUMN_FILTER` in `main.py` and `local_data_handling.py` are configurable.

## Notes

- Ensure VS Code uses the same interpreter where `feedparser` and other dependencies are installed.
- You can extend logic to process multiple ZIP files or change the output layout as needed.

