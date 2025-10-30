-- Schema extensions for ingredient matching between OpenFoodFacts and Marmiton

-- Table to link OpenFoodFacts products with Marmiton ingredients
CREATE TABLE IF NOT EXISTS product_ingredient_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code TEXT NOT NULL,
    ingredient_id INTEGER NOT NULL,
    match_score REAL NOT NULL, -- Score de matching (0-1)
    match_method TEXT, -- 'exact', 'partial', 'manual'
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_code) REFERENCES products(code) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    UNIQUE(product_code, ingredient_id)
);

CREATE INDEX IF NOT EXISTS idx_product_ingredient_product ON product_ingredient_matches(product_code);
CREATE INDEX IF NOT EXISTS idx_product_ingredient_ingredient ON product_ingredient_matches(ingredient_id);
CREATE INDEX IF NOT EXISTS idx_product_ingredient_score ON product_ingredient_matches(match_score);

-- Table for tracking which OpenFoodFacts ingredients map to Marmiton ingredients
CREATE TABLE IF NOT EXISTS ingredient_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- OpenFoodFacts ingredient tag (e.g., "en:butter", "fr:beurre")
    off_ingredient_tag TEXT NOT NULL,
    
    -- Marmiton ingredient name (normalized)
    marmiton_ingredient_id INTEGER NOT NULL,
    
    -- Match type: 'exact' (same word), 'fuzzy' (similar), 'manual' (hand-mapped)
    match_type TEXT NOT NULL DEFAULT 'fuzzy',
    
    -- Confidence score (0-1): how sure we are about the mapping
    confidence REAL NOT NULL DEFAULT 0.8,
    
    -- Whether this mapping is active
    is_active INTEGER NOT NULL DEFAULT 1,
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT,
    
    FOREIGN KEY (marmiton_ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    UNIQUE(off_ingredient_tag, marmiton_ingredient_id)
);

CREATE INDEX IF NOT EXISTS idx_ingredient_mappings_off_tag ON ingredient_mappings(off_ingredient_tag);
CREATE INDEX IF NOT EXISTS idx_ingredient_mappings_marmiton_id ON ingredient_mappings(marmiton_ingredient_id);
CREATE INDEX IF NOT EXISTS idx_ingredient_mappings_active ON ingredient_mappings(is_active);

-- Table to cache which products are usable in Marmiton recipes
-- This denormalizes data for faster queries on the homepage
CREATE TABLE IF NOT EXISTS products_marmiton_usable (
    product_code TEXT PRIMARY KEY,
    
    -- Number of matching Marmiton ingredients found in this product
    matching_ingredients_count INTEGER NOT NULL DEFAULT 0,
    
    -- Total unique ingredients in this product
    total_ingredients_count INTEGER NOT NULL DEFAULT 0,
    
    -- Percentage of product ingredients that can be used in Marmiton recipes
    match_percentage REAL NOT NULL DEFAULT 0.0,
    
    -- List of matching ingredient IDs (comma-separated for easy querying)
    matching_ingredient_ids TEXT,
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT,
    
    FOREIGN KEY (product_code) REFERENCES products(code) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_products_marmiton_usable_match_pct ON products_marmiton_usable(match_percentage DESC);
CREATE INDEX IF NOT EXISTS idx_products_marmiton_usable_count ON products_marmiton_usable(matching_ingredients_count DESC);
