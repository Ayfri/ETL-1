#!/usr/bin/env python3
"""
Script to verify data integrity and consistency in the OpenFoodFacts database.
This script runs various checks to ensure data quality.
"""

import sqlite3
from pathlib import Path
from typing import Any
import pandas as pd


class DatabaseValidator:
    """Validator for OpenFoodFacts database integrity."""
    
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.conn = None
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passed_checks: list[str] = []
    
    def connect(self):
        """Connect to the database."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def run_query(self, query: str) -> list[tuple[Any, ...]]:
        """Execute a query and return results."""
        if not self.conn:
            raise RuntimeError("Database connection is not established.")
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        result = self.run_query(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )
        return len(result) > 0
    
    def check_referential_integrity(self):
        """Check foreign key constraints."""
        print("\n🔍 Checking referential integrity...")
        
        # Check if all nutrition_facts.product_code references exist in products
        query = """
            SELECT COUNT(*) 
            FROM nutrition_facts n
            LEFT JOIN products p ON n.product_code = p.code
            WHERE p.code IS NULL
        """
        result = self.run_query(query)[0][0]
        
        if result == 0:
            self.passed_checks.append("✓ All nutrition records reference valid products")
        else:
            self.errors.append(f"✗ Found {result} nutrition records with invalid product references")
    
    def check_primary_keys(self):
        """Check for duplicate primary keys."""
        print("\n🔍 Checking primary key uniqueness...")
        
        # Check products
        query = "SELECT code, COUNT(*) as count FROM products GROUP BY code HAVING count > 1"
        result = self.run_query(query)
        
        if len(result) == 0:
            self.passed_checks.append("✓ No duplicate product codes found")
        else:
            self.errors.append(f"✗ Found {len(result)} duplicate product codes")
    
    def check_data_ranges(self):
        """Check if numerical values are within reasonable ranges."""
        print("\n🔍 Checking data value ranges...")
        
        checks = [
            ("Nutri-Score values", 
             "SELECT COUNT(*) FROM products WHERE nutriscore_score < -15 OR nutriscore_score > 40",
             "Nutri-Score should be between -15 and 40"),
            
            ("NOVA groups", 
             "SELECT COUNT(*) FROM products WHERE nova_group NOT IN (1, 2, 3, 4) AND nova_group IS NOT NULL",
             "NOVA group should be 1, 2, 3, or 4"),
            
            ("Energy values",
             "SELECT COUNT(*) FROM nutrition_facts WHERE energy_kcal_100g < 0 OR energy_kcal_100g > 900",
             "Energy should be between 0 and 900 kcal/100g"),
            
            ("Protein values",
             "SELECT COUNT(*) FROM nutrition_facts WHERE proteins_100g < 0 OR proteins_100g > 100",
             "Proteins should be between 0 and 100g/100g"),
            
            ("Fat values",
             "SELECT COUNT(*) FROM nutrition_facts WHERE fat_100g < 0 OR fat_100g > 100",
             "Fat should be between 0 and 100g/100g"),
            
            ("Carbs values",
             "SELECT COUNT(*) FROM nutrition_facts WHERE carbohydrates_100g < 0 OR carbohydrates_100g > 100",
             "Carbohydrates should be between 0 and 100g/100g"),
        ]
        
        for check_name, query, description in checks:
            result = self.run_query(query)[0][0]
            if result == 0:
                self.passed_checks.append(f"✓ {check_name}: All values in valid range")
            else:
                self.warnings.append(f"⚠ {check_name}: Found {result} values outside expected range ({description})")
    
    def check_completeness(self):
        """Check data completeness."""
        print("\n🔍 Checking data completeness...")
        
        # Essential fields that should not be NULL
        checks = [
            ("Product codes", "SELECT COUNT(*) FROM products WHERE code IS NULL"),
            ("Product names", "SELECT COUNT(*) FROM products WHERE product_name IS NULL OR product_name = ''"),
        ]
        
        for check_name, query in checks:
            result = self.run_query(query)[0][0]
            if result == 0:
                self.passed_checks.append(f"✓ {check_name}: No missing values")
            else:
                self.warnings.append(f"⚠ {check_name}: {result} missing values")
    
    def check_consistency(self):
        """Check data consistency."""
        print("\n🔍 Checking data consistency...")
        
        # Check if saturated fat <= total fat
        query = """
            SELECT COUNT(*) 
            FROM nutrition_facts 
            WHERE saturated_fat_100g > fat_100g 
            AND saturated_fat_100g IS NOT NULL 
            AND fat_100g IS NOT NULL
        """
        result = self.run_query(query)[0][0]
        
        if result == 0:
            self.passed_checks.append("✓ Saturated fat <= Total fat (consistent)")
        else:
            self.warnings.append(f"⚠ Found {result} records where saturated fat > total fat")
        
        # Check if sugars <= carbohydrates
        query = """
            SELECT COUNT(*) 
            FROM nutrition_facts 
            WHERE sugars_100g > carbohydrates_100g 
            AND sugars_100g IS NOT NULL 
            AND carbohydrates_100g IS NOT NULL
        """
        result = self.run_query(query)[0][0]
        
        if result == 0:
            self.passed_checks.append("✓ Sugars <= Carbohydrates (consistent)")
        else:
            self.warnings.append(f"⚠ Found {result} records where sugars > carbohydrates")
    
    def check_statistics(self):
        """Display database statistics."""
        print("\n📊 Database Statistics:")
        print("=" * 60)
        
        stats = [
            ("Total products", "SELECT COUNT(*) FROM products"),
            ("Total nutrition records", "SELECT COUNT(*) FROM nutrition_facts"),
            ("Products with images", "SELECT COUNT(*) FROM products WHERE image_url IS NOT NULL"),
            ("Products with Nutri-Score", "SELECT COUNT(*) FROM products WHERE nutriscore_grade IS NOT NULL"),
            ("Products with NOVA group", "SELECT COUNT(*) FROM products WHERE nova_group IS NOT NULL"),
            ("Complete products (≥80%)", "SELECT COUNT(*) FROM products WHERE completeness >= 0.8"),
            ("Products with ingredients", "SELECT COUNT(*) FROM products WHERE ingredients_text IS NOT NULL"),
        ]
        
        for stat_name, query in stats:
            result = self.run_query(query)[0][0]
            print(f"  {stat_name}: {result:,}")
    
    def check_csv_consistency(self, csv_path: Path):
        """Compare database with original CSV."""
        print("\n🔍 Checking consistency with source CSV...")
        
        if not csv_path.exists():
            self.warnings.append(f"⚠ CSV file not found for comparison: {csv_path}")
            return
        
        df = pd.read_csv(csv_path, low_memory=False)
        csv_count = len(df)
        
        db_count = self.run_query("SELECT COUNT(*) FROM products")[0][0]
        
        if csv_count == db_count:
            self.passed_checks.append(f"✓ Product count matches CSV ({csv_count} records)")
        else:
            self.warnings.append(f"⚠ Product count mismatch: CSV has {csv_count}, DB has {db_count}")
    
    def run_all_checks(self, csv_path: Path | None = None):
        """Run all validation checks."""
        print("=" * 60)
        print("OpenFoodFacts Database Integrity Check")
        print("=" * 60)
        
        try:
            self.connect()
            
            # Run checks
            self.check_primary_keys()
            self.check_referential_integrity()
            self.check_completeness()
            self.check_data_ranges()
            self.check_consistency()
            
            if csv_path:
                self.check_csv_consistency(csv_path)
            
            self.check_statistics()
            
            # Display results
            print("\n" + "=" * 60)
            print("Validation Results")
            print("=" * 60)
            
            print(f"\n✅ Passed Checks ({len(self.passed_checks)}):")
            for check in self.passed_checks:
                print(f"  {check}")
            
            if self.warnings:
                print(f"\n⚠️  Warnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"  {warning}")
            
            if self.errors:
                print(f"\n❌ Errors ({len(self.errors)}):")
                for error in self.errors:
                    print(f"  {error}")
            
            # Summary
            print("\n" + "=" * 60)
            if self.errors:
                print("❌ Validation FAILED - Critical errors found!")
                return False
            elif self.warnings:
                print("⚠️  Validation PASSED with warnings")
                return True
            else:
                print("✅ Validation PASSED - All checks successful!")
                return True
            
        finally:
            self.close()


def main():
    # Define paths
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "database" / "openfoodfacts.db"
    csv_path = project_root / "data" / "processed" / "openfoodfacts_filtered.csv"
    
    # Run validation
    validator = DatabaseValidator(db_path)
    success = validator.run_all_checks(csv_path)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
