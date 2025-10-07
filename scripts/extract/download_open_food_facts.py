#!/usr/bin/env python3
"""
Script to download Open Food Facts data.
Downloads the complete product database as a compressed CSV file.
"""

import requests
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import gzip

# URL for Open Food Facts CSV export
DATA_URL = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"

# Local paths
RAW_DATA_DIR = Path("data/raw")
OUTPUT_FILE = RAW_DATA_DIR / "openfoodfacts_sample.csv"
EXTRACTED_COUNT = 1_000_000

def download_open_food_facts():
    """Download the Open Food Facts dataset and extract first 100k products."""
    # Create raw data directory if it doesn't exist
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = RAW_DATA_DIR / "openfoodfacts.csv.gz"

    if cache_file.exists():
        print(f"Raw data file {cache_file} already exists. Skipping download.")
    else:
        print(f"Downloading Open Food Facts data to temporary file... {cache_file}")
        print("This may take several minutes as the file is quite large (~2-3 GB)")

        # Download with progress
        response = requests.get(DATA_URL, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        with open(cache_file, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

    print(f"Download complete! Now extracting first {EXTRACTED_COUNT:,} products using pandas...")
    
    # Count total rows in the file
    print("Counting total rows in dataset...")
    with gzip.open(cache_file, 'rt', encoding='utf-8') as f:
        total_rows = sum(1 for _ in f)
    print(f"Total rows in dataset: {total_rows:,}")
    
    # Optimized chunk reading with pandas
    chunk_size = 50_000  # Larger chunks for better performance
    
    print(f"Reading data in chunks of {chunk_size:,} rows...")
    
    # Collect all chunks first, then concatenate
    chunks = []
    rows_read = 0
    
    with tqdm(total=EXTRACTED_COUNT, unit='rows', unit_scale=True, desc="Reading chunks") as pbar:
        for chunk in pd.read_csv(
            cache_file, 
            chunksize=chunk_size, 
            sep='\t',
            engine='c',  # Faster C engine
            low_memory=True,  # More memory efficient
            dtype=str  # Read everything as string to avoid dtype inference issues
        ):
            if rows_read >= EXTRACTED_COUNT:
                break
                
            # Take only what we need for this chunk
            remaining = EXTRACTED_COUNT - rows_read
            if len(chunk) > remaining:
                chunk = chunk.head(remaining)
            
            chunks.append(chunk)
            rows_read += len(chunk)
            pbar.update(len(chunk))
    
    # Concatenate all chunks at once and write to file
    print(f"Concatenating {len(chunks)} chunks...")
    df_final = pd.concat(chunks, ignore_index=True)
    
    print(f"Writing {len(df_final):,} rows to output file...")
    df_final.to_csv(OUTPUT_FILE, index=False)

    # Check file size
    file_size = OUTPUT_FILE.stat().st_size
    print(f"\nExtracted sample file size: {file_size / (1024**2):.2f} MB")
    print(f"Sample contains {len(df_final):,} products from Open Food Facts")

if __name__ == "__main__":
    download_open_food_facts()