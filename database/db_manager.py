#!/usr/bin/env python3
"""
Utility script to manage the OpenFoodFacts database.
Provides a command-line interface for common database operations.
"""

import sys
import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    """Get the database path."""
    return Path(__file__).parent / "openfoodfacts.db"


def info():
    """Display database information."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("❌ Database not found!")
        print(f"Expected location: {db_path}")
        print("\nRun: uv run python database/create_db.py")
        return 1
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("OpenFoodFacts Database Information")
    print("=" * 60)
    
    # Database size
    size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"\n📁 File: {db_path}")
    print(f"   Size: {size_mb:.2f} MB")
    
    # Tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\n📊 Tables ({len(tables)}):")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   • {table}: {count:,} rows")
    
    # Views
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
    views = [row[0] for row in cursor.fetchall()]
    if views:
        print(f"\n👁  Views ({len(views)}):")
        for view in views:
            print(f"   • {view}")
    
    # Indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    indexes = [row[0] for row in cursor.fetchall()]
    if indexes:
        print(f"\n🔍 Indexes ({len(indexes)}):")
        for index in indexes:
            print(f"   • {index}")
    
    # Quick stats
    print("\n📈 Quick Statistics:")
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE nutriscore_grade IS NOT NULL")
    print(f"   • Products with Nutri-Score: {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE nova_group IS NOT NULL")
    print(f"   • Products with NOVA group: {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE completeness >= 0.8")
    print(f"   • High quality products (≥80%): {cursor.fetchone()[0]:,}")
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE image_url IS NOT NULL")
    print(f"   • Products with images: {cursor.fetchone()[0]:,}")
    
    conn.close()
    print("\n" + "=" * 60)
    return 0


def schema():
    """Display database schema."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("❌ Database not found!")
        return 1
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("Database Schema")
    print("=" * 60)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        print(f"\n📋 Table: {table}")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        print(f"   Columns ({len(columns)}):")
        for col in columns:
            col_id, name, type_, not_null, default, pk = col
            pk_marker = " 🔑" if pk else ""
            not_null_marker = " NOT NULL" if not_null else ""
            default_marker = f" DEFAULT {default}" if default else ""
            print(f"      • {name} ({type_}){pk_marker}{not_null_marker}{default_marker}")
    
    conn.close()
    return 0


def query(sql: str):
    """Execute a custom SQL query."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("❌ Database not found!")
        return 1
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        
        if cursor.description:  # SELECT query
            # Print column names
            columns = [desc[0] for desc in cursor.description]
            print(" | ".join(columns))
            print("-" * (len(" | ".join(columns))))
            
            # Print rows
            for row in cursor.fetchall():
                print(" | ".join(str(val) for val in row))
        else:  # Non-SELECT query
            conn.commit()
            print(f"✓ Query executed. Rows affected: {cursor.rowcount}")
        
    except sqlite3.Error as e:
        print(f"❌ SQL Error: {e}")
        return 1
    finally:
        conn.close()
    
    return 0


def vacuum():
    """Optimize database (VACUUM)."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("❌ Database not found!")
        return 1
    
    print("🔧 Optimizing database...")
    
    # Get size before
    size_before = db_path.stat().st_size / (1024 * 1024)
    
    conn = sqlite3.connect(db_path)
    conn.execute("VACUUM")
    conn.close()
    
    # Get size after
    size_after = db_path.stat().st_size / (1024 * 1024)
    saved = size_before - size_after
    
    print(f"✓ Database optimized!")
    print(f"   Size before: {size_before:.2f} MB")
    print(f"   Size after:  {size_after:.2f} MB")
    print(f"   Saved:       {saved:.2f} MB ({saved/size_before*100:.1f}%)")
    
    return 0


def usage():
    """Display usage information."""
    print("=" * 60)
    print("OpenFoodFacts Database Manager")
    print("=" * 60)
    print("\nUsage: python database/db_manager.py <command> [args]")
    print("\nCommands:")
    print("  info                Display database information")
    print("  schema              Display database schema")
    print("  query <sql>         Execute a SQL query")
    print("  vacuum              Optimize database (VACUUM)")
    print("  help                Show this help message")
    print("\nExamples:")
    print("  python database/db_manager.py info")
    print("  python database/db_manager.py query 'SELECT COUNT(*) FROM products'")
    print("  python database/db_manager.py vacuum")
    print("=" * 60)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        usage()
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "info":
        return info()
    elif command == "schema":
        return schema()
    elif command == "query":
        if len(sys.argv) < 3:
            print("❌ Missing SQL query!")
            print("Usage: python database/db_manager.py query '<sql>'")
            return 1
        return query(sys.argv[2])
    elif command == "vacuum":
        return vacuum()
    elif command == "help":
        usage()
        return 0
    else:
        print(f"❌ Unknown command: {command}")
        usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
