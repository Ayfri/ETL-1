#!/usr/bin/env python3
"""
Simple ingredient linking script.

Creates a view/cache that identifies OpenFoodFacts products
that can be used in Marmiton recipes by matching ingredient names.
"""

import sqlite3
from pathlib import Path


def get_marmiton_ingredient_keywords() -> set[str]:
    """Get keywords from Marmiton ingredients."""
    db_path = Path(__file__).parent.parent.parent / "database" / "openfoodfacts.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    keywords = set[str]()

    # Get all Marmiton ingredients
    cursor.execute("SELECT name FROM ingredients WHERE source = 'marmiton'")
    for row in cursor.fetchall():
        if row[0]:
            # Extract keywords (words) from ingredient names
            words = row[0].lower().split()
            for word in words:
                if len(word) > 2:  # Only words longer than 2 chars
                    keywords.add(word)
    
    conn.close()
    return keywords


def mark_products_usable_in_recipes() -> int:
    """
    Mark products that contain ingredients usable in Marmiton recipes.
    
    Uses a simple approach: if a product's ingredients mention 
    any Marmiton ingredient keyword, mark it as usable.
    """
    db_path = Path(__file__).parent.parent.parent / "database" / "openfoodfacts.db"
    
    print("Marking products usable in Marmiton recipes...")
    
    # Get Marmiton ingredient keywords
    keywords = get_marmiton_ingredient_keywords()
    print(f"   Found {len(keywords)} ingredient keywords from Marmiton recipes")
    
    if not keywords:
        print("   No keywords found")
        return 0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # For each product, check if it has matching ingredients
    cursor.execute("SELECT code, ingredients_text, ingredients_tags FROM products WHERE ingredients_text IS NOT NULL OR ingredients_tags IS NOT NULL LIMIT 5000")
    
    products = cursor.fetchall()
    marked = 0
    
    for product_code, ingredients_text, ingredients_tags in products:
        # Combine all ingredient info
        all_ingredients = (ingredients_text or "").lower() + " " + (ingredients_tags or "").lower()
        
        # Check if any Marmiton keyword appears in product ingredients
        has_marmiton_ingredient = False
        for keyword in keywords:
            if keyword in all_ingredients:
                has_marmiton_ingredient = True
                break
        
        # If product has Marmiton ingredients, add it to the cache
        if has_marmiton_ingredient:
            try:
                # Count how many keywords match
                matching_count = sum(1 for keyword in keywords if keyword in all_ingredients)
                total_keywords = len(keywords)
                match_percentage = matching_count / total_keywords if total_keywords > 0 else 0
                
                cursor.execute(
                    """INSERT OR REPLACE INTO products_marmiton_usable 
                       (product_code, matching_ingredients_count, total_ingredients_count, 
                        match_percentage, updated_at)
                       VALUES (?, ?, ?, ?, datetime('now'))""",
                    (product_code, matching_count, total_keywords, match_percentage)
                )
                marked += 1
            except sqlite3.Error as e:
                print(f"   Warning: Error marking product {product_code}: {e}")
    
    conn.commit()
    print(f"   Marked {marked} products as usable in recipes")
    conn.close()
    
    return marked


def main() -> int:
    """Main workflow."""
    db_path = Path(__file__).parent.parent.parent / "database" / "openfoodfacts.db"
    
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return 1
    
    print("=" * 60)
    print("Marking Products Usable in Marmiton Recipes")
    print("=" * 60)
    
    mark_products_usable_in_recipes()
    
    print("\n" + "=" * 60)
    print("Marking complete!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
