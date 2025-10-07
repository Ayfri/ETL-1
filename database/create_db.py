#!/usr/bin/env python3
"""
Script to create the OpenFoodFacts SQLite database and tables.
This script reads the schema.sql file and creates the database structure.
"""

import sqlite3
from pathlib import Path


def create_database(db_path: str | Path, schema_path: str | Path) -> None:
    """
    Create SQLite database with schema from SQL file.
    
    Args:
        db_path: Path to the SQLite database file
        schema_path: Path to the SQL schema file
    """
    db_path = Path(db_path)
    schema_path = Path(schema_path)
    
    # Create parent directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read schema
    print(f"Reading schema from {schema_path}...")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Create database and execute schema
    print(f"Creating database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Execute schema (split by semicolon for multiple statements)
        cursor.executescript(schema)
        conn.commit()
        print("✓ Database created successfully!")
        
        # List created tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nCreated tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # List created views
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
        views = cursor.fetchall()
        if views:
            print(f"\nCreated views:")
            for view in views:
                print(f"  - {view[0]}")
        
        # List created indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
        indexes = cursor.fetchall()
        if indexes:
            print(f"\nCreated indexes:")
            for index in indexes:
                print(f"  - {index[0]}")
        
    except sqlite3.Error as e:
        print(f"✗ Error creating database: {e}")
        raise
    finally:
        conn.close()


def main():
    # Define paths
    project_root = Path(__file__).parent.parent
    db_path = project_root / "database" / "openfoodfacts.db"
    schema_path = project_root / "database" / "schema.sql"
    
    print("=" * 60)
    print("OpenFoodFacts Database Creation")
    print("=" * 60)
    
    # Check if database already exists
    if db_path.exists():
        response = input(f"\nDatabase already exists at {db_path}.\nDo you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
        db_path.unlink()
        print("Existing database deleted.")
    
    # Create database
    create_database(db_path, schema_path)
    
    print("\n" + "=" * 60)
    print("Database creation completed!")
    print(f"Database location: {db_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
