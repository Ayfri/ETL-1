"""
Match OpenFoodFacts products with Marmiton ingredients.
Uses ingredient tags from OpenFoodFacts and simple ingredient names from Marmiton.
Only matches ingredients that are actually used in recipes.
"""

import sqlite3
from pathlib import Path
from tqdm import tqdm

DB_PATH = Path(__file__).parent.parent.parent / "database" / "openfoodfacts.db"


def normalize_ingredient_name(name: str) -> str:
    """Normalize ingredient name for matching."""
    if not name:
        return ""
    
    # Remove language prefix from tags (en:, fr:, etc.)
    if ':' in name:
        name = name.split(':', 1)[1]
    
    # Lowercase and clean
    name = name.lower().strip()
    
    # Replace dashes and underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    return name


def is_simple_ingredient(name: str) -> bool:
    """Check if this is a simple ingredient name (not a phrase or description)."""
    if not name or len(name) < 3:
        return False
    
    # Count words
    words = name.split()
    
    # Too many words = it's a phrase/description, not an ingredient
    if len(words) > 3:
        return False
    
    # Check for common non-ingredient patterns
    bad_patterns = [
        'de ', 'du ', 'des ', 'la ', 'le ', 'les ',
        'ou ', 'et ', 'au ', 'aux ', 'pour ', 'avec ',
        'frais', 'séché', 'congelé', 'surgelé', 'pelé',
        'haché', 'coupé', 'râpé', 'moulu', 'entier',
        'boîte', 'bocal', 'sachet', 'paquet',
        'taille', 'moyenne', 'moyen', 'grosse', 'gros',
        'facultatif', 'optionnel', 'choix', 'préférence'
    ]
    
    name_lower = name.lower()
    for pattern in bad_patterns:
        if pattern in name_lower and len(words) > 1:
            return False
    
    # Must contain at least one letter (not just numbers)
    if not any(c.isalpha() for c in name):
        return False
    
    return True


def get_ingredients_used_in_recipes(cursor) -> set[int]:
    """Get IDs of ingredients actually used in recipes."""
    cursor.execute("""
        SELECT DISTINCT ingredient_id 
        FROM recipe_ingredients
    """)
    return {row[0] for row in cursor.fetchall()}


def match_products_with_ingredients():
    """Match products with ingredients using OpenFoodFacts tags."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🔍 Loading simple Marmiton ingredients...")
    cursor.execute("""
        SELECT id, name 
        FROM ingredients 
        ORDER BY name
    """)
    
    all_ingredients = cursor.fetchall()
    
    # Filter to simple ingredients only
    ingredients = []
    for ing in all_ingredients:
        if is_simple_ingredient(ing['name']):
            ingredients.append(ing)
    
    print(f"   Kept {len(ingredients)} simple ingredients (filtered from {len(all_ingredients)})")
    
    print("\n🎯 Matching products with ingredients...")
    
    # Clear old matches
    cursor.execute("DELETE FROM product_ingredient_matches")
    conn.commit()
    
    matches = []
    products_processed = 0
    
    # Get all products with ingredient tags
    cursor.execute("""
        SELECT code, product_name, ingredients_tags
        FROM products
        WHERE ingredients_tags IS NOT NULL AND ingredients_tags != ''
    """)
    products = cursor.fetchall()
    
    print(f"   Processing {len(products)} products...")
    
    for product in tqdm(products, desc="Matching", unit="product"):
        products_processed += 1
        
        if not product['ingredients_tags']:
            continue
        
        # Parse ingredient tags (comma separated)
        product_tags = [normalize_ingredient_name(tag.strip()) 
                       for tag in product['ingredients_tags'].split(',')]
        product_tags = [t for t in product_tags if t]
        
        if not product_tags:
            continue
        
        # Check each Marmiton ingredient
        for ingredient in ingredients:
            ingredient_name_norm = normalize_ingredient_name(ingredient['name'])
            
            # Direct match in tags
            if ingredient_name_norm in product_tags:
                matches.append((
                    product['code'],
                    ingredient['id'],
                    1.0,
                    'exact'
                ))
            else:
                # Partial match (ingredient name is in one of the tags)
                for tag in product_tags:
                    if ingredient_name_norm in tag or tag in ingredient_name_norm:
                        # Check it's not a substring match of a longer word
                        if len(ingredient_name_norm) >= 4:  # Only for longer ingredients
                            matches.append((
                                product['code'],
                                ingredient['id'],
                                0.8,
                                'partial'
                            ))
                        break
        
        # Batch insert every 1000 products
        if len(matches) >= 1000:
            cursor.executemany("""
                INSERT OR IGNORE INTO product_ingredient_matches 
                (product_code, ingredient_id, match_score, match_method)
                VALUES (?, ?, ?, ?)
            """, matches)
            conn.commit()
            matches = []
    
    # Insert remaining
    if matches:
        cursor.executemany("""
            INSERT OR IGNORE INTO product_ingredient_matches 
            (product_code, ingredient_id, match_score, match_method)
            VALUES (?, ?, ?, ?)
        """, matches)
        conn.commit()
    
    # Statistics
    print("\n📊 Results:")
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT product_code) as products,
            COUNT(DISTINCT ingredient_id) as ingredients,
            COUNT(*) as matches,
            AVG(match_score) as avg_score
        FROM product_ingredient_matches
    """)
    stats = cursor.fetchone()
    
    print(f"   ✅ Products with matches: {stats['products']}")
    print(f"   ✅ Ingredients matched: {stats['ingredients']}")
    print(f"   ✅ Total matches: {stats['matches']}")
    if stats['avg_score']:
        print(f"   ✅ Average score: {stats['avg_score']:.2f}")
    
    # Show top examples
    print("\n🔎 Top product matches:")
    cursor.execute("""
        SELECT 
            p.product_name,
            i.name as ingredient_name,
            m.match_score,
            m.match_method
        FROM product_ingredient_matches m
        JOIN products p ON m.product_code = p.code
        JOIN ingredients i ON m.ingredient_id = i.id
        ORDER BY m.match_score DESC, p.product_name
        LIMIT 15
    """)
    
    for row in cursor.fetchall():
        print(f"   • '{row['product_name'][:40]}...' ← '{row['ingredient_name']}' ({row['match_score']:.1f}, {row['match_method']})")
    
    conn.close()
    print("\n✨ Done!")


if __name__ == "__main__":
    match_products_with_ingredients()
