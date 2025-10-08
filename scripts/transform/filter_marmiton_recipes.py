#!/usr/bin/env python3
"""Filter Marmiton recipes CSV and save processed output.

Usage:
  python scripts/transform/filter_marmiton_recipes.py

This script reads `data/raw/marmiton_recipes.csv` in chunks, removes rows that
do not have a non-empty value for the 'images' column, cleans special characters
from the 'name' column, and writes the filtered CSV to `data/processed/marmiton_recipes_filtered.csv`.

It is resilient to large files because it uses chunked reading.
"""

from pathlib import Path
import argparse
import pandas as pd
import re


def clean_title(title: str) -> str:
    """Clean special characters from recipe title, keeping letters, numbers, spaces, and common accents."""
    if not isinstance(title, str):
        return ""
    # Keep alphanumeric, spaces, and common French accents
    cleaned = re.sub(r'[^a-zA-Z0-9àâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ\s]', '', title)
    return cleaned.strip()


def filter_csv(input_path: Path, output_path: Path, chunksize: int = 50_000):
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        raise SystemExit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_in = 0
    total_out = 0
    first_write = True

    # Read in chunks
    reader = pd.read_csv(input_path, chunksize=chunksize, dtype=str, low_memory=False)
    try:
        chunk: pd.DataFrame
        for chunk_idx, chunk in enumerate(reader):
            total_in += len(chunk)

            # Ensure string type and strip spaces for relevant columns
            if 'images' in chunk.columns:
                chunk['images'] = chunk['images'].fillna('').str.strip()
            if 'name' in chunk.columns:
                chunk['name'] = chunk['name'].fillna('').str.strip()

            # Clean the name column
            if 'name' in chunk.columns:
                chunk['name'] = chunk['name'].apply(clean_title)

            # Keep rows where images column is non-empty
            mask = chunk['images'] != '' if 'images' in chunk.columns else pd.Series([False] * len(chunk))

            # Skip rows with default image
            if 'images' in chunk.columns:
                mask &= ~chunk['images'].str.contains('https://static.afcdn.com/relmrtn/Front/Vendor/img/default-recipe-picture_80x80.jpg')

            kept = chunk[mask]
            total_out += len(kept)

            # Write to output
            if first_write:
                kept.to_csv(output_path, index=False, mode='w', encoding='utf-8')
                first_write = False
            else:
                kept.to_csv(output_path, index=False, header=False, mode='a', encoding='utf-8')

            print(f"Chunk {chunk_idx+1}: read={len(chunk):,} kept={len(kept):,}")

    except pd.errors.EmptyDataError:
        print("Le fichier source est vide ou mal formé.")
        raise

    print(f"Finished. Processed {total_in:,} rows, kept {total_out:,}. Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Filter Marmiton recipes CSV by images and clean titles")
    parser.add_argument('--input', '-i', default='data/raw/marmiton_recipes.csv')
    parser.add_argument('--output', '-o', default='data/processed/marmiton_recipes_filtered.csv')
    parser.add_argument('--chunksize', '-c', type=int, default=50000)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    filter_csv(input_path, output_path, chunksize=args.chunksize)


if __name__ == '__main__':
    main()
