#!/usr/bin/env python3
"""
Link OpenFoodFacts ingredients with Marmiton ingredients.

Simplified version focusing on common ingredients.
"""

import json
import re
import sqlite3
from pathlib import Path
from collections import defaultdict

import pandas as pd


def normalize_ingredient_name(name: str) -> str:
    """Normalize ingredient name for matching."""
    name = name.lower().strip()
    # Remove common quantity indicators
    name = re.sub(r'\s*\(.*?\)\s*$', '', name)
    name = re.sub(r'\s*-.*?$', '', name)
    # Keep only letters, numbers, spaces
    name = re.sub(r'[^a-z0-9\sàâäéèêëïîôöùûüÿçæœ]', '', name)
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def extract_marmiton_ingredients(recipes_csv: Path) -> dict[str, int]:
    """Extract unique ingredients from Marmiton recipes."""
    ingredients_count: dict[str, int] = {}
    
    if not recipes_csv.exists():
        print(f"⚠️  Recipes CSV not found: {recipes_csv}")
        return ingredients_count
    
    print(f"📖 Reading Marmiton recipes from {recipes_csv}...")
    
    try:
        for chunk in pd.read_csv(recipes_csv, chunksize=5000, dtype=str, low_memory=False):
            for _, row in chunk.iterrows():
                if pd.isna(row.get('ingredients_json')):
                    continue
                
                try:
                    ingredients = json.loads(row['ingredients_json'])
                    for ing in ingredients:
                        ing_name = ing.get('name', '').strip()
                        if ing_name:
                            normalized = normalize_ingredient_name(ing_name)
                            if normalized and len(normalized) > 2:
                                ingredients_count[normalized] = ingredients_count.get(normalized, 0) + 1
                except (json.JSONDecodeError, KeyError, ValueError, AttributeError):
                    continue
    except Exception as e:
        print(f"❌ Error reading recipes CSV: {e}")
    
    print(f"   ✓ Found {len(ingredients_count)} unique ingredients")
    return ingredients_count


def load_marmiton_ingredients_to_db(db_path: Path, ingredients_count: dict[str, int]) -> int:
    """Load extracted ingredients into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"💾 Loading ingredients into database...")
    
    # Sort by frequency - keep only top 300 to avoid bloat
    sorted_ingredients = sorted(ingredients_count.items(), key=lambda x: x[1], reverse=True)[:300]
    
    loaded = 0
    for ing_name, count in sorted_ingredients:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO ingredients (name, source) VALUES (?, 'marmiton')",
                (ing_name,)
            )
            loaded += 1
        except sqlite3.Error as e:
            print(f"   ⚠️  Failed to insert '{ing_name}': {e}")
    
    conn.commit()
    print(f"   ✓ Loaded {loaded} ingredients")
    conn.close()
    
    return loaded


def similarity_ratio(a: str, b: str) -> float:
    """Simple word overlap ratio."""
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.8
    # Word-based overlap
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    intersection = len(words_a & words_b)
    union = len(words_a | words_b)
    return float(intersection) / float(union) if union > 0 else 0.0


def create_simple_mappings(db_path: Path) -> int:
    """Create simple mappings between OpenFoodFacts and Marmiton ingredients."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔗 Creating simple ingredient mappings...")
    
    # Get all Marmiton ingredients
    cursor.execute("SELECT id, name FROM ingredients WHERE source = 'marmiton'")
    marmiton_ingredients: list[tuple] = cursor.fetchall()
    print(f"   Found {len(marmiton_ingredients)} Marmiton ingredients")
    
    if not marmiton_ingredients:
        conn.close()
        return 0
    
    # Create a mapping of normalized names to Marmiton ingredient IDs
    marmiton_map: dict[str, int] = {}
    for ing_id, ing_name in marmiton_ingredients:
        normalized = normalize_ingredient_name(ing_name)
        if normalized:
            marmiton_map[normalized] = ing_id
    
    # Get unique ingredient tags from a sample of OpenFoodFacts products
    cursor.execute("""
        SELECT DISTINCT ingredients_tags
        FROM products
        WHERE ingredients_tags IS NOT NULL AND ingredients_tags != ''
        LIMIT 500
    """)
    
    all_off_tags = []
    for row in cursor.fetchall():
        tags = re.split(r'[,;|]', row[0])
        for tag in tags:
            tag = tag.strip()
            if tag and len(tag) > 2 and tag not in all_off_tags:
                all_off_tags.append(tag)
                if len(all_off_tags) > 200:  # Limit to 200 tags
                    break
        if len(all_off_tags) > 200:
            break
    
    print(f"   Sampling {len(all_off_tags)} OpenFoodFacts ingredient tags")
    
    # Create mappings
    mappings_created = 0
    
    for off_tag in all_off_tags:
        off_normalized = normalize_ingredient_name(off_tag)
        
        if not off_normalized or len(off_normalized) < 2:
            continue
        
        # Try exact match first
        if off_normalized in marmiton_map:
            marmiton_id = marmiton_map[off_normalized]
            try:
                cursor.execute(
                    """INSERT OR REPLACE INTO ingredient_mappings 
                       (off_ingredient_tag, marmiton_ingredient_id, match_type, confidence, is_active)
                       VALUES (?, ?, 'exact', 1.0, 1)""",
                    (off_tag, marmiton_id)
                )
                mappings_created += 1
            except sqlite3.Error:
                pass
        else:
            # Try substring matching with top 30 ingredients
            top_marmiton = sorted(marmiton_map.items(), key=lambda x: x[1])[:30]
            for marmiton_norm, marmiton_id in top_marmiton:
                similarity = similarity_ratio(off_normalized, marmiton_norm)
                if similarity > 0.75:
                    try:
                        cursor.execute(
                            """INSERT OR REPLACE INTO ingredient_mappings 
                               (off_ingredient_tag, marmiton_ingredient_id, match_type, confidence, is_active)
                               VALUES (?, ?, 'fuzzy', ?, 1)""",
                            (off_tag, marmiton_id, similarity)
                        )
                        mappings_created += 1
                        break
                    except sqlite3.Error:
                        pass
    
    conn.commit()
    print(f"   ✓ Created {mappings_created} ingredient mappings")
    conn.close()
    
    return mappings_created


def main() -> int:
    """Main workflow."""
    db_path = Path(__file__).parent.parent.parent / "database" / "openfoodfacts.db"
    recipes_csv = Path(__file__).parent.parent.parent / "data" / "processed" / "marmiton_recipes_filtered.csv"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 1
    
    print("=" * 60)
    print("🔗 Linking OpenFoodFacts and Marmiton Ingredients")
    print("=" * 60)
    
    # Step 1: Extract Marmiton ingredients
    print("\n📊 Step 1: Extracting Marmiton ingredients...")
    ingredients_count = extract_marmiton_ingredients(recipes_csv)
    
    if not ingredients_count:
        print("❌ No ingredients found in recipes CSV")
        return 1
    
    # Step 2: Load ingredients to database (only top 300)
    print("\n📊 Step 2: Loading ingredients to database...")
    load_marmiton_ingredients_to_db(db_path, ingredients_count)
    
    # Step 3: Create simple mappings
    print("\n📊 Step 3: Creating ingredient mappings...")
    create_simple_mappings(db_path)
    
    print("\n" + "=" * 60)
    print("✅ Ingredient linking complete!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
