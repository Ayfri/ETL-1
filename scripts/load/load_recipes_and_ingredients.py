#!/usr/bin/env python3
"""
Load Marmiton recipes and ingredients into SQLite database.

This script:
1. Loads ingredients from ingredients_raw.csv into the ingredients table
2. Loads recipes from marmiton_recipes.csv into the recipes table
3. Creates relationships in the recipe_ingredients junction table by matching
   ingredient names from parsed JSON with the ingredients table

Usage: python scripts/load/load_recipes_and_ingredients.py
"""

import csv
import json
import sqlite3
from pathlib import Path


DB_PATH = Path("database/openfoodfacts.db")
INGREDIENTS_CSV = Path("data/raw/ingredients_raw.csv")
RECIPES_CSV = Path("data/raw/marmiton_recipes.csv")


def normalize_ingredient_name(name: str) -> str:
    """
    Normalize ingredient name for matching.
    
    Args:
        name: Raw ingredient name
        
    Returns:
        Normalized name (lowercase, stripped)
    """
    return name.strip().lower()


def load_ingredients(conn: sqlite3.Connection) -> dict[str, int]:
    """
    Load ingredients from CSV into database.
    
    Args:
        conn: Database connection
        
    Returns:
        Dictionary mapping normalized ingredient names to IDs
    """
    print("Loading ingredients...")
    
    cursor = conn.cursor()
    ingredient_map: dict[str, int] = {}
    
    if not INGREDIENTS_CSV.exists():
        print(f"⚠️  {INGREDIENTS_CSV} not found, skipping ingredient loading")
        return ingredient_map
    
    with open(INGREDIENTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            name = row.get("name", "").strip()
            image_url = row.get("image_url", "").strip()
            
            if not name:
                continue
            
            # Insert or get existing ingredient
            cursor.execute(
                """
                INSERT INTO ingredients (name, image_url, source)
                VALUES (?, ?, 'marmiton')
                ON CONFLICT(name) DO UPDATE SET image_url = excluded.image_url
                """,
                (name, image_url)
            )
            
            # Get the ingredient ID
            cursor.execute("SELECT id FROM ingredients WHERE name = ? COLLATE NOCASE", (name,))
            result = cursor.fetchone()
            
            if result:
                ingredient_map[normalize_ingredient_name(name)] = result[0]
    
    conn.commit()
    print(f"✓ Loaded {len(ingredient_map)} ingredients")
    
    return ingredient_map


def load_recipes(conn: sqlite3.Connection, ingredient_map: dict[str, int]) -> None:
    """
    Load recipes from CSV and create ingredient relationships.
    
    Args:
        conn: Database connection
        ingredient_map: Mapping of normalized ingredient names to IDs
    """
    print("\nLoading recipes...")
    
    cursor = conn.cursor()
    
    if not RECIPES_CSV.exists():
        print(f"⚠️  {RECIPES_CSV} not found")
        return
    
    recipes_loaded = 0
    relationships_created = 0
    
    with open(RECIPES_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            name = row.get("name", "").strip()
            url = row.get("url", "").strip()
            
            if not name or not url:
                continue
            
            # Insert recipe
            cursor.execute(
                """
                INSERT INTO recipes (
                    name, url, rate, nb_comments, difficulty, budget,
                    prep_time, cook_time, total_time, recipe_quantity,
                    ingredients_raw, ingredients_json, steps, images, tags
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    name = excluded.name,
                    rate = excluded.rate,
                    nb_comments = excluded.nb_comments,
                    difficulty = excluded.difficulty,
                    budget = excluded.budget,
                    prep_time = excluded.prep_time,
                    cook_time = excluded.cook_time,
                    total_time = excluded.total_time,
                    recipe_quantity = excluded.recipe_quantity,
                    ingredients_raw = excluded.ingredients_raw,
                    ingredients_json = excluded.ingredients_json,
                    steps = excluded.steps,
                    images = excluded.images,
                    tags = excluded.tags,
                    updated_at = datetime('now')
                """,
                (
                    name,
                    url,
                    row.get("rate", ""),
                    row.get("nb_comments", ""),
                    row.get("difficulty", ""),
                    row.get("budget", ""),
                    row.get("prep_time", ""),
                    row.get("cook_time", ""),
                    row.get("total_time", ""),
                    row.get("recipe_quantity", ""),
                    row.get("ingredients_raw", ""),
                    row.get("ingredients_json", ""),
                    row.get("steps", ""),
                    row.get("images", ""),
                    row.get("tags", "")
                )
            )
            
            # Get the recipe ID
            cursor.execute("SELECT id FROM recipes WHERE url = ?", (url,))
            result = cursor.fetchone()
            
            if not result:
                continue
            
            recipe_id = result[0]
            recipes_loaded += 1
            
            # Parse ingredients JSON and create relationships
            ingredients_json_str = row.get("ingredients_json", "")
            
            if ingredients_json_str:
                try:
                    ingredients_list = json.loads(ingredients_json_str)
                    
                    for ingredient_data in ingredients_list:
                        if not isinstance(ingredient_data, dict):
                            continue
                        
                        ingredient_name = ingredient_data.get("name", "").strip()
                        
                        if not ingredient_name:
                            continue
                        
                        # Normalize and look up ingredient ID
                        normalized_name = normalize_ingredient_name(ingredient_name)
                        ingredient_id = ingredient_map.get(normalized_name)
                        
                        if ingredient_id:
                            # Create relationship
                            cursor.execute(
                                """
                                INSERT INTO recipe_ingredients (
                                    recipe_id, ingredient_id, quantity, unit, raw_text
                                )
                                VALUES (?, ?, ?, ?, ?)
                                ON CONFLICT(recipe_id, ingredient_id) DO UPDATE SET
                                    quantity = excluded.quantity,
                                    unit = excluded.unit,
                                    raw_text = excluded.raw_text
                                """,
                                (
                                    recipe_id,
                                    ingredient_id,
                                    ingredient_data.get("quantity", ""),
                                    ingredient_data.get("unit", ""),
                                    ingredient_data.get("raw", "")
                                )
                            )
                            relationships_created += 1
                        else:
                            # Ingredient not found - create it on the fly
                            cursor.execute(
                                """
                                INSERT INTO ingredients (name, source)
                                VALUES (?, 'marmiton_recipe')
                                ON CONFLICT(name) DO NOTHING
                                """,
                                (ingredient_name,)
                            )
                            
                            cursor.execute(
                                "SELECT id FROM ingredients WHERE name = ? COLLATE NOCASE",
                                (ingredient_name,)
                            )
                            result = cursor.fetchone()
                            
                            if result:
                                ingredient_id = result[0]
                                ingredient_map[normalized_name] = ingredient_id
                                
                                cursor.execute(
                                    """
                                    INSERT INTO recipe_ingredients (
                                        recipe_id, ingredient_id, quantity, unit, raw_text
                                    )
                                    VALUES (?, ?, ?, ?, ?)
                                    ON CONFLICT(recipe_id, ingredient_id) DO NOTHING
                                    """,
                                    (
                                        recipe_id,
                                        ingredient_id,
                                        ingredient_data.get("quantity", ""),
                                        ingredient_data.get("unit", ""),
                                        ingredient_data.get("raw", "")
                                    )
                                )
                                relationships_created += 1
                
                except json.JSONDecodeError:
                    pass
    
    conn.commit()
    print(f"✓ Loaded {recipes_loaded} recipes")
    print(f"✓ Created {relationships_created} recipe-ingredient relationships")


def main() -> None:
    """Main entry point."""
    print("="*60)
    print("Loading Marmiton recipes and ingredients")
    print("="*60)
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("Please run database/create_db.py first")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Load ingredients first
        ingredient_map = load_ingredients(conn)
        
        # Load recipes and create relationships
        load_recipes(conn, ingredient_map)
        
        # Print statistics
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ingredients")
        ingredients_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes")
        recipes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipe_ingredients")
        relationships_count = cursor.fetchone()[0]
        
        print("\n" + "="*60)
        print("Database statistics:")
        print(f"  Ingredients: {ingredients_count}")
        print(f"  Recipes: {recipes_count}")
        print(f"  Recipe-Ingredient relationships: {relationships_count}")
        print("="*60)
        print("✓ Loading complete!")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
