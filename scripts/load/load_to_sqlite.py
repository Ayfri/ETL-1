#!/usr/bin/env python3
"""
Script to load cleaned OpenFoodFacts data into SQLite database.
This script reads the filtered CSV file and populates the database tables.
"""

import sqlite3
from pathlib import Path
import pandas as pd
from tqdm import tqdm


# Define column mappings for each table
PRODUCTS_COLUMNS = [
    'code', 'product_name', 'abbreviated_product_name', 'generic_name',
    'brands', 'brands_tags', 'brands_en', 'brand_owner',
    'categories', 'categories_tags', 'categories_en', 'main_category', 'main_category_en',
    'quantity', 'product_quantity', 'packaging', 'packaging_tags', 'packaging_en', 'packaging_text',
    'origins', 'origins_tags', 'origins_en', 'manufacturing_places', 'manufacturing_places_tags',
    'purchase_places', 'stores', 'countries', 'countries_tags', 'countries_en',
    'cities', 'cities_tags',
    'labels', 'labels_tags', 'labels_en', 'emb_codes', 'emb_codes_tags', 'first_packaging_code_geo',
    'ingredients_text', 'ingredients_tags', 'ingredients_analysis_tags',
    'allergens', 'allergens_en', 'traces', 'traces_tags', 'traces_en',
    'serving_size', 'serving_quantity',
    'additives_n', 'additives', 'additives_tags', 'additives_en',
    'nutriscore_score', 'nutriscore_grade', 'nova_group',
    'environmental_score_score', 'environmental_score_grade', 'nutrient_levels_tags',
    'nutrition-score-fr_100g', 'nutrition-score-uk_100g',
    'pnns_groups_1', 'pnns_groups_2', 'food_groups', 'food_groups_tags', 'food_groups_en',
    'states', 'states_tags', 'states_en', 'completeness',
    'no_nutrition_data', 'data_quality_errors_tags',
    'unique_scans_n', 'popularity_tags',
    'image_url', 'image_small_url', 'image_ingredients_url', 'image_ingredients_small_url',
    'image_nutrition_url', 'image_nutrition_small_url',
    'url', 'creator', 'owner',
    'created_t', 'created_datetime', 'last_modified_t', 'last_modified_datetime', 'last_modified_by',
    'last_updated_t', 'last_updated_datetime', 'last_image_t', 'last_image_datetime'
]

NUTRITION_COLUMNS = [
    'energy-kj_100g', 'energy-kcal_100g', 'energy_100g', 'energy-from-fat_100g',
    'fat_100g', 'saturated-fat_100g',
    'butyric-acid_100g', 'caproic-acid_100g', 'caprylic-acid_100g', 'capric-acid_100g',
    'lauric-acid_100g', 'myristic-acid_100g', 'palmitic-acid_100g', 'stearic-acid_100g',
    'arachidic-acid_100g', 'behenic-acid_100g', 'lignoceric-acid_100g', 'cerotic-acid_100g',
    'montanic-acid_100g', 'melissic-acid_100g',
    'unsaturated-fat_100g', 'monounsaturated-fat_100g', 'polyunsaturated-fat_100g',
    'omega-3-fat_100g', 'omega-6-fat_100g', 'omega-9-fat_100g',
    'trans-fat_100g', 'cholesterol_100g',
    'alpha-linolenic-acid_100g', 'eicosapentaenoic-acid_100g', 'docosahexaenoic-acid_100g',
    'linoleic-acid_100g', 'arachidonic-acid_100g', 'gamma-linolenic-acid_100g',
    'dihomo-gamma-linolenic-acid_100g', 'oleic-acid_100g', 'elaidic-acid_100g',
    'gondoic-acid_100g', 'mead-acid_100g', 'erucic-acid_100g', 'nervonic-acid_100g',
    'carbohydrates_100g', 'sugars_100g', 'added-sugars_100g',
    'sucrose_100g', 'glucose_100g', 'fructose_100g', 'lactose_100g', 'maltose_100g',
    'maltodextrins_100g', 'starch_100g', 'polyols_100g', 'erythritol_100g',
    'fiber_100g', 'soluble-fiber_100g', 'insoluble-fiber_100g',
    'proteins_100g', 'casein_100g', 'serum-proteins_100g', 'nucleotides_100g',
    'salt_100g', 'added-salt_100g', 'sodium_100g',
    'alcohol_100g',
    'vitamin-a_100g', 'beta-carotene_100g', 'vitamin-d_100g', 'vitamin-e_100g',
    'vitamin-k_100g', 'vitamin-c_100g', 'vitamin-b1_100g', 'vitamin-b2_100g',
    'vitamin-pp_100g', 'vitamin-b6_100g', 'vitamin-b9_100g', 'folates_100g',
    'vitamin-b12_100g', 'biotin_100g', 'pantothenic-acid_100g',
    'silica_100g', 'bicarbonate_100g', 'potassium_100g', 'chloride_100g',
    'calcium_100g', 'phosphorus_100g', 'iron_100g', 'magnesium_100g',
    'zinc_100g', 'copper_100g', 'manganese_100g', 'fluoride_100g',
    'selenium_100g', 'chromium_100g', 'molybdenum_100g', 'iodine_100g',
    'caffeine_100g', 'taurine_100g', 'ph_100g',
    'fruits-vegetables-nuts_100g', 'fruits-vegetables-nuts-dried_100g',
    'fruits-vegetables-nuts-estimate_100g', 'fruits-vegetables-nuts-estimate-from-ingredients_100g',
    'collagen-meat-protein-ratio_100g', 'cocoa_100g', 'chlorophyl_100g',
    'carbon-footprint_100g', 'carbon-footprint-from-meat-or-fish_100g',
    'glycemic-index_100g', 'water-hardness_100g', 'choline_100g',
    'phylloquinone_100g', 'beta-glucan_100g', 'inositol_100g', 'carnitine_100g'
]


def normalize_column_name(col: str) -> str:
    """
    Normalize column name from CSV to database format.
    Replace hyphens with underscores and remove _100g suffix for mapping.
    """
    return col.replace('-', '_')


def load_data(csv_path: str | Path, db_path: str | Path) -> None:
    """
    Load data from CSV into SQLite database.
    
    Args:
        csv_path: Path to the filtered CSV file
        db_path: Path to the SQLite database
    """
    csv_path = Path(csv_path)
    db_path = Path(db_path)
    
    # Check if files exist
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}. Run create_db.py first.")
    
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"✓ Loaded {len(df)} rows with {len(df.columns)} columns")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Insert products
        print("\nInserting products...")
        products_data = df[PRODUCTS_COLUMNS].copy()
        
        # Rename columns to match database schema
        products_data.columns = [normalize_column_name(col) for col in products_data.columns]
        
        # Ensure code is string (not float)
        products_data['code'] = products_data['code'].astype(str)
        
        # Replace NaN with None for proper NULL handling
        products_data = products_data.where(pd.notna(products_data), None)
        
        # Insert products
        for idx, row in tqdm(products_data.iterrows(), total=len(products_data), desc="Products"):
            placeholders = ','.join(['?' for _ in row])
            columns = ','.join(row.index)
            sql = f"INSERT OR REPLACE INTO products ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row))
        
        print(f"✓ Inserted {len(products_data)} products")
        
        # Insert nutrition facts
        print("\nInserting nutrition facts...")
        nutrition_data = df[['code'] + NUTRITION_COLUMNS].copy()
        
        # Rename columns
        nutrition_data.columns = ['product_code'] + [normalize_column_name(col) for col in NUTRITION_COLUMNS]
        
        # Ensure product_code is string (not float)
        nutrition_data['product_code'] = nutrition_data['product_code'].astype(str)
        
        # Replace NaN with None
        nutrition_data = nutrition_data.where(pd.notna(nutrition_data), None)
        
        # Insert nutrition facts
        for idx, row in tqdm(nutrition_data.iterrows(), total=len(nutrition_data), desc="Nutrition"):
            # Skip if all nutrition values are None
            if all(v is None for k, v in row.items() if k != 'product_code'):
                continue
            
            placeholders = ','.join(['?' for _ in row])
            columns = ','.join(row.index)
            sql = f"INSERT INTO nutrition_facts ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row))
        
        # Get count of inserted nutrition facts
        cursor.execute("SELECT COUNT(*) FROM nutrition_facts")
        nutrition_count = cursor.fetchone()[0]
        print(f"✓ Inserted {nutrition_count} nutrition fact records")
        
        # Commit transaction
        conn.commit()
        print("\n✓ All data committed successfully!")
        
        # Display statistics
        print("\n" + "=" * 60)
        print("Database Statistics:")
        print("=" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM products")
        print(f"Total products: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM nutrition_facts")
        print(f"Total nutrition records: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE nutriscore_grade IS NOT NULL")
        print(f"Products with Nutri-Score: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE nova_group IS NOT NULL")
        print(f"Products with NOVA group: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE completeness >= 0.8")
        print(f"High quality products (≥80% complete): {cursor.fetchone()[0]}")
        
        cursor.execute("""
            SELECT nutriscore_grade, COUNT(*) 
            FROM products 
            WHERE nutriscore_grade IS NOT NULL 
            GROUP BY nutriscore_grade 
            ORDER BY nutriscore_grade
        """)
        print("\nNutri-Score distribution:")
        for grade, count in cursor.fetchall():
            print(f"  Grade {grade}: {count} products")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error loading data: {e}")
        raise
    finally:
        conn.close()


def main():
    # Define paths
    project_root = Path(__file__).parent.parent.parent
    csv_path = project_root / "data" / "processed" / "openfoodfacts_filtered.csv"
    db_path = project_root / "database" / "openfoodfacts.db"
    
    print("=" * 60)
    print("OpenFoodFacts Data Loading")
    print("=" * 60)
    
    load_data(csv_path, db_path)
    
    print("\n" + "=" * 60)
    print("Data loading completed!")
    print(f"Database location: {db_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
