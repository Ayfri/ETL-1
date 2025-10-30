#!/usr/bin/env python3
"""
Match Marmiton recipes with ingredients.
Extracts ingredients from recipes and matches them with ingredient names.
"""

import sqlite3
import json
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
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    # Remove common french articles
    for article in ['d\'', 'de ', 'du ', 'la ', 'le ', 'les ', 'un ', 'une ', 'des ']:
        if name.startswith(article):
            name = name[len(article):]
    
    return name.strip()


def match_recipes_with_ingredients():
    """Match Marmiton recipes with ingredients."""
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing matches
        print("Clearing existing recipe-ingredient matches...")
        cursor.execute("DELETE FROM recipe_ingredients")
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
        
        # Process recipes
        print("\nMatching recipes with ingredients...")
        cursor.execute("""
            SELECT id, name, ingredients_raw, ingredients_json
            FROM recipes 
            WHERE (ingredients_raw IS NOT NULL AND ingredients_raw != '') 
               OR (ingredients_json IS NOT NULL AND ingredients_json != '')
        """)
        recipes = cursor.fetchall()
        
        matches_to_insert = []
        total_matches = 0
        recipes_matched = 0
        
        for recipe_id, recipe_name, ingredients_raw, ingredients_json in tqdm(recipes, desc="Matching recipes"):
            recipe_has_match = False
            
            # Try to parse JSON ingredients first (more structured)
            if ingredients_json:
                try:
                    ing_list = json.loads(ingredients_json)
                    if isinstance(ing_list, list):
                        for ing_obj in ing_list:
                            if isinstance(ing_obj, dict):
                                # Try different fields that might contain the ingredient name
                                ing_name = ing_obj.get('name') or ing_obj.get('ingredient') or ing_obj.get('nom') or ''
                                quantity = ing_obj.get('quantity') or ing_obj.get('quantite') or ''
                                unit = ing_obj.get('unit') or ing_obj.get('unite') or ''
                                raw_text = ing_obj.get('raw') or ''
                            else:
                                ing_name = str(ing_obj)
                                quantity = ''
                                unit = ''
                                raw_text = ''
                            
                            if ing_name:
                                normalized_name = normalize_ingredient_name(ing_name)
                                ingredient_id = ingredient_map.get(normalized_name)
                                
                                # If no exact match, try partial match
                                if not ingredient_id:
                                    for ing_key, ing_id in ingredient_map.items():
                                        if ing_key in normalized_name or normalized_name in ing_key:
                                            ingredient_id = ing_id
                                            break
                                
                                if ingredient_id:
                                    matches_to_insert.append((
                                        recipe_id,
                                        ingredient_id,
                                        quantity,
                                        unit,
                                        raw_text or ing_name
                                    ))
                                    total_matches += 1
                                    recipe_has_match = True
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # Fallback to raw text if JSON didn't work
            if not recipe_has_match and ingredients_raw:
                try:
                    # Parse pipe-separated ingredients
                    ingredients_list = [ing.strip() for ing in str(ingredients_raw).split('|')]
                    
                    for raw_ing in ingredients_list:
                        if not raw_ing:
                            continue
                        
                        # Try to extract quantity, unit, and name
                        # Format is typically: "quantity unit name" or just "name"
                        parts = raw_ing.split(None, 2)  # Split on whitespace, max 3 parts
                        
                        ing_name = raw_ing
                        quantity = ''
                        unit = ''
                        
                        # Simple heuristic: if first part is numeric, it's likely quantity
                        if parts and parts[0].replace('.', '', 1).replace(',', '', 1).isdigit():
                            quantity = parts[0]
                            if len(parts) > 1:
                                unit = parts[1]
                                ing_name = ' '.join(parts[2:]) if len(parts) > 2 else ''
                        
                        normalized_name = normalize_ingredient_name(ing_name)
                        if not normalized_name:
                            continue
                        
                        ingredient_id = ingredient_map.get(normalized_name)
                        
                        # If no exact match, try partial match
                        if not ingredient_id:
                            for ing_key, ing_id in ingredient_map.items():
                                if ing_key in normalized_name or (normalized_name in ing_key and len(normalized_name) > 3):
                                    ingredient_id = ing_id
                                    break
                        
                        if ingredient_id:
                            matches_to_insert.append((
                                recipe_id,
                                ingredient_id,
                                quantity,
                                unit,
                                raw_ing
                            ))
                            total_matches += 1
                            recipe_has_match = True
                except Exception:
                    pass
            
            if recipe_has_match:
                recipes_matched += 1
        
        # Insert all matches (using INSERT OR REPLACE to handle duplicates)
        print(f"\nInserting {len(matches_to_insert)} recipe-ingredient matches...")
        
        # Deduplicate matches before inserting
        unique_matches = {}
        for recipe_id, ingredient_id, quantity, unit, raw_text in matches_to_insert:
            key = (recipe_id, ingredient_id)
            # Keep the first match for each recipe-ingredient pair
            if key not in unique_matches:
                unique_matches[key] = (recipe_id, ingredient_id, quantity, unit, raw_text)
        
        matches_to_insert = list(unique_matches.values())
        print(f"  Deduped to {len(matches_to_insert)} unique matches")
        
        cursor.executemany(
            "INSERT OR REPLACE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, raw_text) VALUES (?, ?, ?, ?, ?)",
            matches_to_insert
        )
        conn.commit()
        
        print(f"✓ Successfully created {len(matches_to_insert)} matches for {recipes_matched} recipes")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM recipe_ingredients")
        total_links = cursor.fetchone()[0]
        print(f"✓ Total recipe_ingredients in database: {total_links}")
        
        # Show stats
        cursor.execute("""
            SELECT COUNT(DISTINCT recipe_id) 
            FROM recipe_ingredients
        """)
        recipes_with_matches = cursor.fetchone()[0]
        print(f"✓ Recipes with ingredients: {recipes_with_matches}")
        
        # Show top ingredients by recipe count
        print("\n📊 Top 10 ingredients by recipe count:")
        cursor.execute("""
            SELECT i.name, COUNT(DISTINCT ri.recipe_id) as recipe_count
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            GROUP BY ri.ingredient_id, i.name
            ORDER BY recipe_count DESC
            LIMIT 10
        """)
        for name, count in cursor.fetchall():
            print(f"  {name}: {count} recettes")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(match_recipes_with_ingredients())
