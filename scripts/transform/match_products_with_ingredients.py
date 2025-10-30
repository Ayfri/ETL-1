#!/usr/bin/env python3
"""
Match OpenFoodFacts products with Marmiton ingredients.
Extracts ingredient tags from products and matches them with ingredient names.
"""

import sqlite3
import sys
from pathlib import Path
from tqdm import tqdm

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import get_db_path


def normalize_ingredient_name(name: str) -> str:
    """Normalize ingredient name for matching."""
    if not name:
        return ""
    
    # Lowercase and strip
    name = name.lower().strip()
    
    # Remove extra spaces and special characters
    name = ' '.join(name.split())
    
    # Remove language prefix (en:, fr:, etc.)
    if ':' in name:
        name = name.split(':', 1)[1]
    
    return name


def match_products_with_ingredients():
    """Match OpenFoodFacts products with Marmiton ingredients."""
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing matches
        print("Clearing existing product-ingredient matches...")
        cursor.execute("DELETE FROM product_ingredient_matches")
        conn.commit()
        
        # Load all ingredients into memory for fast lookup
        print("Loading ingredients...")
        cursor.execute("SELECT id, name FROM ingredients")
        ingredients = cursor.fetchall()
        
        # Create normalized name -> id mapping
        ingredient_map = {}
        for ing_id, name in ingredients:
            normalized = normalize_ingredient_name(name)
            if normalized:
                ingredient_map[normalized] = ing_id
        
        print(f"✓ Loaded {len(ingredient_map)} ingredients")
        
        # Process products
        print("\nMatching products with ingredients...")
        cursor.execute("""
            SELECT code, product_name, ingredients_tags 
            FROM products 
            WHERE ingredients_tags IS NOT NULL AND ingredients_tags != ''
            LIMIT 5000
        """)
        products = cursor.fetchall()
        
        matches_to_insert = []
        total_matches = 0
        
        for code, product_name, ingredients_tags_str in tqdm(products, desc="Matching products"):
            if not ingredients_tags_str:
                continue
            
            try:
                # Parse ingredient tags (comma-separated)
                tags = [tag.strip() for tag in str(ingredients_tags_str).split(',')]
                
                for tag in tags:
                    normalized_tag = normalize_ingredient_name(tag)
                    if not normalized_tag:
                        continue
                    
                    # Try exact match first
                    ingredient_id = ingredient_map.get(normalized_tag)
                    
                    # If no exact match, try partial match (tag contains ingredient name)
                    if not ingredient_id:
                        for ing_name, ing_id in ingredient_map.items():
                            if ing_name in normalized_tag or normalized_tag in ing_name:
                                ingredient_id = ing_id
                                break
                    
                    if ingredient_id:
                        matches_to_insert.append((code, ingredient_id, 1.0, 'exact' if normalized_tag in ingredient_map else 'partial'))
                        total_matches += 1
                        
            except Exception as e:
                continue
        
        # Insert all matches
        print(f"\nInserting {len(matches_to_insert)} product-ingredient matches...")
        cursor.executemany(
            "INSERT OR IGNORE INTO product_ingredient_matches (product_code, ingredient_id, match_score, match_method) VALUES (?, ?, ?, ?)",
            matches_to_insert
        )
        conn.commit()
        
        print(f"✓ Successfully created {len(matches_to_insert)} matches")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM product_ingredient_matches")
        total_links = cursor.fetchone()[0]
        print(f"✓ Total product_ingredient_matches in database: {total_links}")
        
        # Show stats
        cursor.execute("""
            SELECT COUNT(DISTINCT product_code) 
            FROM product_ingredient_matches
        """)
        products_with_matches = cursor.fetchone()[0]
        print(f"✓ Products with matches: {products_with_matches}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(match_products_with_ingredients())
