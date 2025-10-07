#!/usr/bin/env python3
"""
Example script demonstrating how to query the OpenFoodFacts database.
This can be converted to a Jupyter notebook for interactive analysis.
"""

import sqlite3
import pandas as pd
from pathlib import Path


def connect_to_db():
    """Connect to the OpenFoodFacts database."""
    db_path = Path(__file__).parent.parent.parent / "database" / "openfoodfacts.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    return sqlite3.connect(db_path)


def example_1_basic_queries():
    """Example 1: Basic queries to explore the database."""
    print("=" * 60)
    print("Example 1: Basic Database Queries")
    print("=" * 60)
    
    conn = connect_to_db()
    
    # Query 1: Count products by Nutri-Score
    print("\n1. Products by Nutri-Score:")
    df = pd.read_sql_query("""
        SELECT nutriscore_grade, COUNT(*) as count
        FROM products
        WHERE nutriscore_grade IS NOT NULL
        GROUP BY nutriscore_grade
        ORDER BY nutriscore_grade
    """, conn)
    print(df.to_string(index=False))
    
    # Query 2: Top 10 brands
    print("\n2. Top 10 brands by product count:")
    df = pd.read_sql_query("""
        SELECT brands, COUNT(*) as count
        FROM products
        WHERE brands IS NOT NULL
        GROUP BY brands
        ORDER BY count DESC
        LIMIT 10
    """, conn)
    print(df.to_string(index=False))
    
    # Query 3: Products with highest energy
    print("\n3. Top 5 products with highest energy:")
    df = pd.read_sql_query("""
        SELECT product_name, brands, energy_kcal_100g, nutriscore_grade
        FROM products_with_nutrition
        WHERE energy_kcal_100g IS NOT NULL
        ORDER BY energy_kcal_100g DESC
        LIMIT 5
    """, conn)
    print(df.to_string(index=False))
    
    conn.close()


def example_2_nutritional_analysis():
    """Example 2: Nutritional analysis by NOVA groups."""
    print("\n" + "=" * 60)
    print("Example 2: Nutritional Analysis by NOVA Groups")
    print("=" * 60)
    
    conn = connect_to_db()
    
    df = pd.read_sql_query("""
        SELECT 
            nova_group,
            COUNT(*) as product_count,
            ROUND(AVG(energy_kcal_100g), 2) as avg_energy_kcal,
            ROUND(AVG(fat_100g), 2) as avg_fat_g,
            ROUND(AVG(saturated_fat_100g), 2) as avg_saturated_fat_g,
            ROUND(AVG(sugars_100g), 2) as avg_sugars_g,
            ROUND(AVG(proteins_100g), 2) as avg_proteins_g,
            ROUND(AVG(salt_100g), 2) as avg_salt_g,
            ROUND(AVG(fiber_100g), 2) as avg_fiber_g
        FROM products_with_nutrition
        WHERE nova_group IS NOT NULL
        GROUP BY nova_group
        ORDER BY nova_group
    """, conn)
    
    print("\nAverage nutritional values by NOVA group (per 100g):")
    print(df.to_string(index=False))
    
    print("\nNOVA Groups:")
    print("  1 = Unprocessed/minimally processed foods")
    print("  2 = Processed culinary ingredients")
    print("  3 = Processed foods")
    print("  4 = Ultra-processed foods")
    
    conn.close()


def example_3_filtering_products():
    """Example 3: Find healthy products based on criteria."""
    print("\n" + "=" * 60)
    print("Example 3: Find Healthy Products")
    print("=" * 60)
    
    conn = connect_to_db()
    
    # Healthy criteria: Nutri-Score A or B, low NOVA group
    df = pd.read_sql_query("""
        SELECT 
            product_name,
            brands,
            nutriscore_grade,
            nova_group,
            energy_kcal_100g,
            proteins_100g,
            fiber_100g,
            sugars_100g
        FROM products_with_nutrition
        WHERE nutriscore_grade IN ('a', 'b')
          AND nova_group <= 2
          AND energy_kcal_100g IS NOT NULL
        ORDER BY nutriscore_grade, energy_kcal_100g
        LIMIT 10
    """, conn)
    
    print("\nTop 10 healthy products (Nutri-Score A/B, NOVA ≤2):")
    print(df.to_string(index=False))
    
    conn.close()


def example_4_category_analysis():
    """Example 4: Analyze products by category."""
    print("\n" + "=" * 60)
    print("Example 4: Category Analysis")
    print("=" * 60)
    
    conn = connect_to_db()
    
    # Count products in main categories
    df = pd.read_sql_query("""
        SELECT 
            main_category_en as category,
            COUNT(*) as count,
            ROUND(AVG(CASE WHEN nutriscore_grade IN ('a', 'b') THEN 1 ELSE 0 END) * 100, 1) as pct_healthy
        FROM products
        WHERE main_category_en IS NOT NULL
        GROUP BY main_category_en
        HAVING count >= 50
        ORDER BY count DESC
        LIMIT 15
    """, conn)
    
    print("\nTop categories with % of healthy products (Nutri-Score A/B):")
    print(df.to_string(index=False))
    
    conn.close()


def example_5_additives_analysis():
    """Example 5: Analyze products with many additives."""
    print("\n" + "=" * 60)
    print("Example 5: Products with Most Additives")
    print("=" * 60)
    
    conn = connect_to_db()
    
    df = pd.read_sql_query("""
        SELECT 
            product_name,
            brands,
            additives_n,
            nutriscore_grade,
            nova_group
        FROM products
        WHERE additives_n IS NOT NULL
          AND additives_n > 0
        ORDER BY additives_n DESC
        LIMIT 10
    """, conn)
    
    print("\nTop 10 products with most additives:")
    print(df.to_string(index=False))
    
    # Average additives by NOVA group
    df2 = pd.read_sql_query("""
        SELECT 
            nova_group,
            ROUND(AVG(COALESCE(additives_n, 0)), 2) as avg_additives
        FROM products
        WHERE nova_group IS NOT NULL
        GROUP BY nova_group
        ORDER BY nova_group
    """, conn)
    
    print("\nAverage number of additives by NOVA group:")
    print(df2.to_string(index=False))
    
    conn.close()


def example_6_export_to_csv():
    """Example 6: Export a subset of data to CSV."""
    print("\n" + "=" * 60)
    print("Example 6: Export Data to CSV")
    print("=" * 60)
    
    conn = connect_to_db()
    
    # Export high quality products
    df = pd.read_sql_query("""
        SELECT 
            code,
            product_name,
            brands,
            categories,
            nutriscore_grade,
            nova_group,
            energy_kcal_100g,
            fat_100g,
            sugars_100g,
            proteins_100g,
            salt_100g,
            fiber_100g
        FROM products_with_nutrition
        WHERE completeness >= 0.8
          AND nutriscore_grade IS NOT NULL
    """, conn)
    
    output_path = Path(__file__).parent.parent.parent / "data" / "processed" / "high_quality_products.csv"
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Exported {len(df)} high quality products to:")
    print(f"  {output_path}")
    
    conn.close()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("OpenFoodFacts Database Query Examples")
    print("=" * 60)
    
    try:
        example_1_basic_queries()
        example_2_nutritional_analysis()
        example_3_filtering_products()
        example_4_category_analysis()
        example_5_additives_analysis()
        example_6_export_to_csv()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except FileNotFoundError:
        print("\n❌ Error: Database not found!")
        print("Please run the following commands first:")
        print("  1. uv run python database/create_db.py")
        print("  2. uv run python scripts/load/load_to_sqlite.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
