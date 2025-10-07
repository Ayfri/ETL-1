#!/usr/bin/env python3
"""Filter OpenFoodFacts CSV and save processed output.

Usage:
  python scripts/transform/filter_openfoodfacts.py

This script reads `data/raw/openfoodfacts_sample.csv` in chunks, removes rows that
do not have a non-empty value for ALL required columns, and writes the filtered
CSV to `data/processed/openfoodfacts_filtered.csv`.

It is resilient to large files because it uses chunked reading.
"""

from pathlib import Path
import argparse
import sys
import pandas as pd


REQUIRED_COLS_PREFERRED = [
    'product_name',
    'image_url',
    'energy-kcal_100g',
    # some files may use energy-kj_100g or energy-kj_100 (tolerate both)
    'energy-kj_100g',
    'energy_100g',
    'proteins_100g',
    'carbohydrates_100g',
    'fat_100g',
    'fiber_100g',
    'sugars_100g',
    'salt_100g',
    'sodium_100g',
    'categories_en',
]


def resolve_columns(df_columns):
    """Return the list of actual column names to check, mapping tolerant variants.

    If a preferred column name is not present but a close alias exists, prefer it.
    """
    cols = []
    available = set(df_columns)
    for col in REQUIRED_COLS_PREFERRED:
        if col in available:
            cols.append(col)
            continue

        # tolerate common variants
        if col == 'energy-kj_100g':
            if 'energy-kj_100' in available:
                cols.append('energy-kj_100')
                continue
        # fallback: try without trailing g
        alt = col.replace('_100g', '_100')
        if alt != col and alt in available:
            cols.append(alt)
            continue

        # no matching column found
        cols.append(col)  # still append; caller will detect missing columns

    return cols


def filter_csv(input_path: Path, output_path: Path, chunksize: int = 50_000):
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        raise SystemExit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_in = 0
    total_out = 0
    first_write = True

    # Read first chunk to detect column names and resolve variants
    reader = pd.read_csv(input_path, chunksize=chunksize, dtype=str, low_memory=False)
    try:
        for chunk_idx, chunk in enumerate(reader):
            if chunk_idx == 0:
                actual_cols = resolve_columns(chunk.columns)
                missing = [c for c in actual_cols if c not in chunk.columns]
                if missing:
                    print("Erreur: colonnes requises manquantes dans le CSV:", missing)
                    print("Vérifie les en-têtes du fichier source.")
                    raise SystemExit(2)
                check_cols = actual_cols

            total_in += len(chunk)

            # ensure string type and strip spaces
            chunk = chunk.astype({c: 'string' for c in check_cols})
            for c in check_cols:
                chunk[c] = chunk[c].fillna('').str.strip()

            # Keep rows where ALL required columns are non-empty
            mask = None
            for c in check_cols:
                if mask is None:
                    mask = chunk[c] != ''
                else:
                    mask &= (chunk[c] != '')

            kept = chunk[mask]
            total_out += len(kept)

            # write
            if first_write:
                kept.to_csv(output_path, index=False, mode='w')
                first_write = False
            else:
                kept.to_csv(output_path, index=False, header=False, mode='a')

            print(f"Chunk {chunk_idx+1}: read={len(chunk):,} kept={len(kept):,}")

    except pd.errors.EmptyDataError:
        print("Le fichier source est vide ou mal formé.")
        raise

    print(f"Finished. Processed {total_in:,} rows, kept {total_out:,}. Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Filter OpenFoodFacts CSV by required columns")
    parser.add_argument('--input', '-i', default='data/raw/openfoodfacts_sample.csv')
    parser.add_argument('--output', '-o', default='data/processed/openfoodfacts_filtered.csv')
    parser.add_argument('--chunksize', '-c', type=int, default=50000)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    filter_csv(input_path, output_path, chunksize=args.chunksize)


if __name__ == '__main__':
    main()


