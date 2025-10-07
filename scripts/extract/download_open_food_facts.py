#!/usr/bin/env python3
"""
Script to download Open Food Facts data.
Downloads the complete product database as a compressed CSV file.
"""

import os
import gzip
import requests
from pathlib import Path
from tqdm import tqdm
import pandas as pd

# URL for Open Food Facts CSV export
DATA_URL = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"

# Local paths
RAW_DATA_DIR = Path("data/raw")
OUTPUT_FILE = RAW_DATA_DIR / "openfoodfacts_sample.csv"

def download_open_food_facts():
    """Download the Open Food Facts dataset and extract first 100k products."""
    # Create raw data directory if it doesn't exist
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    temp_file = RAW_DATA_DIR / "temp_openfoodfacts.csv.gz"

    print(f"Downloading Open Food Facts data to temporary file...")
    print("This may take several minutes as the file is quite large (~2-3 GB)")

    # Download with progress
    response = requests.get(DATA_URL, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))

    with open(temp_file, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    print("Download complete! Now extracting first 100,000 products using pandas...")

    # Use pandas to read first 100k rows from the gzipped CSV
    df = pd.read_csv(temp_file, nrows=100000, low_memory=False)
    df.to_csv(OUTPUT_FILE, index=False)

    # Remove temp file
    temp_file.unlink()

    # Check file size
    file_size = OUTPUT_FILE.stat().st_size
    print(f"Extracted sample file size: {file_size / (1024**2):.2f} MB")
    print(f"Sample contains {len(df)} products from Open Food Facts")

if __name__ == "__main__":
    download_open_food_facts()