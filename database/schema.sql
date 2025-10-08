-- Schema for OpenFoodFacts Database
-- This database stores cleaned food product information from OpenFoodFacts

-- Main products table with core information
CREATE TABLE IF NOT EXISTS products (
    -- Primary identifiers
    code TEXT PRIMARY KEY,
    product_name TEXT,
    abbreviated_product_name TEXT,
    generic_name TEXT,
    
    -- Brand and origin information
    brands TEXT,
    brands_tags TEXT,
    brands_en TEXT,
    brand_owner TEXT,
    
    -- Categories
    categories TEXT,
    categories_tags TEXT,
    categories_en TEXT,
    main_category TEXT,
    main_category_en TEXT,
    
    -- Product details
    quantity TEXT,
    product_quantity REAL,
    packaging TEXT,
    packaging_tags TEXT,
    packaging_en TEXT,
    packaging_text TEXT,
    
    -- Geographic information
    origins TEXT,
    origins_tags TEXT,
    origins_en TEXT,
    manufacturing_places TEXT,
    manufacturing_places_tags TEXT,
    purchase_places TEXT,
    stores TEXT,
    countries TEXT,
    countries_tags TEXT,
    countries_en TEXT,
    cities TEXT,
    cities_tags TEXT,
    
    -- Labels and certifications
    labels TEXT,
    labels_tags TEXT,
    labels_en TEXT,
    emb_codes TEXT,
    emb_codes_tags TEXT,
    first_packaging_code_geo TEXT,
    
    -- Ingredients
    ingredients_text TEXT,
    ingredients_tags TEXT,
    ingredients_analysis_tags TEXT,
    allergens TEXT,
    allergens_en TEXT,
    traces TEXT,
    traces_tags TEXT,
    traces_en TEXT,
    serving_size TEXT,
    serving_quantity REAL,
    
    -- Additives
    additives_n INTEGER,
    additives TEXT,
    additives_tags TEXT,
    additives_en TEXT,
    
    -- Quality scores
    nutriscore_score REAL,
    nutriscore_grade TEXT,
    nova_group REAL,
    environmental_score_score REAL,
    environmental_score_grade TEXT,
    nutrient_levels_tags TEXT,
    nutrition_score_fr_100g REAL,
    nutrition_score_uk_100g REAL,
    
    -- Groups and classifications
    pnns_groups_1 TEXT,
    pnns_groups_2 TEXT,
    food_groups TEXT,
    food_groups_tags TEXT,
    food_groups_en TEXT,
    
    -- Completeness
    states TEXT,
    states_tags TEXT,
    states_en TEXT,
    completeness REAL,
    
    -- Data quality
    no_nutrition_data TEXT,
    data_quality_errors_tags TEXT,
    
    -- Popularity
    unique_scans_n INTEGER,
    popularity_tags TEXT,
    
    -- Images
    image_url TEXT,
    image_small_url TEXT,
    image_ingredients_url TEXT,
    image_ingredients_small_url TEXT,
    image_nutrition_url TEXT,
    image_nutrition_small_url TEXT,
    
    -- Metadata
    url TEXT,
    creator TEXT,
    owner TEXT,
    created_t INTEGER,
    created_datetime TEXT,
    last_modified_t INTEGER,
    last_modified_datetime TEXT,
    last_modified_by TEXT,
    last_updated_t INTEGER,
    last_updated_datetime TEXT,
    last_image_t INTEGER,
    last_image_datetime TEXT
);

-- Nutritional values table (per 100g)
CREATE TABLE IF NOT EXISTS nutrition_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code TEXT NOT NULL,
    
    -- Energy
    energy_kj_100g REAL,
    energy_kcal_100g REAL,
    energy_100g REAL,
    energy_from_fat_100g REAL,
    
    -- Fats
    fat_100g REAL,
    saturated_fat_100g REAL,
    butyric_acid_100g REAL,
    caproic_acid_100g REAL,
    caprylic_acid_100g REAL,
    capric_acid_100g REAL,
    lauric_acid_100g REAL,
    myristic_acid_100g REAL,
    palmitic_acid_100g REAL,
    stearic_acid_100g REAL,
    arachidic_acid_100g REAL,
    behenic_acid_100g REAL,
    lignoceric_acid_100g REAL,
    cerotic_acid_100g REAL,
    montanic_acid_100g REAL,
    melissic_acid_100g REAL,
    unsaturated_fat_100g REAL,
    monounsaturated_fat_100g REAL,
    polyunsaturated_fat_100g REAL,
    omega_3_fat_100g REAL,
    omega_6_fat_100g REAL,
    omega_9_fat_100g REAL,
    trans_fat_100g REAL,
    cholesterol_100g REAL,
    
    -- Fatty acids
    alpha_linolenic_acid_100g REAL,
    eicosapentaenoic_acid_100g REAL,
    docosahexaenoic_acid_100g REAL,
    linoleic_acid_100g REAL,
    arachidonic_acid_100g REAL,
    gamma_linolenic_acid_100g REAL,
    dihomo_gamma_linolenic_acid_100g REAL,
    oleic_acid_100g REAL,
    elaidic_acid_100g REAL,
    gondoic_acid_100g REAL,
    mead_acid_100g REAL,
    erucic_acid_100g REAL,
    nervonic_acid_100g REAL,
    
    -- Carbohydrates
    carbohydrates_100g REAL,
    sugars_100g REAL,
    added_sugars_100g REAL,
    sucrose_100g REAL,
    glucose_100g REAL,
    fructose_100g REAL,
    lactose_100g REAL,
    maltose_100g REAL,
    maltodextrins_100g REAL,
    starch_100g REAL,
    polyols_100g REAL,
    erythritol_100g REAL,
    
    -- Fiber
    fiber_100g REAL,
    soluble_fiber_100g REAL,
    insoluble_fiber_100g REAL,
    
    -- Proteins
    proteins_100g REAL,
    casein_100g REAL,
    serum_proteins_100g REAL,
    nucleotides_100g REAL,
    
    -- Salt and sodium
    salt_100g REAL,
    added_salt_100g REAL,
    sodium_100g REAL,
    
    -- Alcohol
    alcohol_100g REAL,
    
    -- Vitamins
    vitamin_a_100g REAL,
    beta_carotene_100g REAL,
    vitamin_d_100g REAL,
    vitamin_e_100g REAL,
    vitamin_k_100g REAL,
    vitamin_c_100g REAL,
    vitamin_b1_100g REAL,
    vitamin_b2_100g REAL,
    vitamin_pp_100g REAL,
    vitamin_b6_100g REAL,
    vitamin_b9_100g REAL,
    folates_100g REAL,
    vitamin_b12_100g REAL,
    biotin_100g REAL,
    pantothenic_acid_100g REAL,
    
    -- Minerals
    silica_100g REAL,
    bicarbonate_100g REAL,
    potassium_100g REAL,
    chloride_100g REAL,
    calcium_100g REAL,
    phosphorus_100g REAL,
    iron_100g REAL,
    magnesium_100g REAL,
    zinc_100g REAL,
    copper_100g REAL,
    manganese_100g REAL,
    fluoride_100g REAL,
    selenium_100g REAL,
    chromium_100g REAL,
    molybdenum_100g REAL,
    iodine_100g REAL,
    
    -- Other compounds
    caffeine_100g REAL,
    taurine_100g REAL,
    ph_100g REAL,
    fruits_vegetables_nuts_100g REAL,
    fruits_vegetables_nuts_dried_100g REAL,
    fruits_vegetables_nuts_estimate_100g REAL,
    fruits_vegetables_nuts_estimate_from_ingredients_100g REAL,
    collagen_meat_protein_ratio_100g REAL,
    cocoa_100g REAL,
    chlorophyl_100g REAL,
    carbon_footprint_100g REAL,
    carbon_footprint_from_meat_or_fish_100g REAL,
    glycemic_index_100g REAL,
    water_hardness_100g REAL,
    choline_100g REAL,
    phylloquinone_100g REAL,
    beta_glucan_100g REAL,
    inositol_100g REAL,
    carnitine_100g REAL,
    
    FOREIGN KEY (product_code) REFERENCES products(code) ON DELETE CASCADE
);

-- Index for better query performance
CREATE INDEX IF NOT EXISTS idx_products_brands ON products(brands);
CREATE INDEX IF NOT EXISTS idx_products_categories ON products(categories);
CREATE INDEX IF NOT EXISTS idx_products_countries ON products(countries);
CREATE INDEX IF NOT EXISTS idx_products_nutriscore ON products(nutriscore_grade);
CREATE INDEX IF NOT EXISTS idx_products_nova ON products(nova_group);
CREATE INDEX IF NOT EXISTS idx_nutrition_product_code ON nutrition_facts(product_code);

-- Views for common queries
CREATE VIEW IF NOT EXISTS products_with_nutrition AS
SELECT
    p.*,
    n.energy_kcal_100g,
    n.fat_100g,
    n.saturated_fat_100g,
    n.carbohydrates_100g,
    n.sugars_100g,
    n.proteins_100g,
    n.salt_100g,
    n.fiber_100g
FROM products p
LEFT JOIN (
    -- Ensure one nutrition row per product_code to avoid duplicating products
    SELECT
        product_code,
        MAX(energy_kcal_100g) AS energy_kcal_100g,
        MAX(fat_100g) AS fat_100g,
        MAX(saturated_fat_100g) AS saturated_fat_100g,
        MAX(carbohydrates_100g) AS carbohydrates_100g,
        MAX(sugars_100g) AS sugars_100g,
        MAX(proteins_100g) AS proteins_100g,
        MAX(salt_100g) AS salt_100g,
        MAX(fiber_100g) AS fiber_100g
    FROM nutrition_facts
    GROUP BY product_code
) n ON p.code = n.product_code;

CREATE VIEW IF NOT EXISTS high_quality_products AS
SELECT *
FROM products
WHERE completeness >= 0.8
  AND nutriscore_grade IS NOT NULL
  AND image_url IS NOT NULL;

-- Recipes table to store scraped recipes from Marmiton
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    rate TEXT,
    nb_comments TEXT,
    difficulty TEXT,
    budget TEXT,
    prep_time TEXT,
    cook_time TEXT,
    total_time TEXT,
    recipe_quantity TEXT,
    ingredients_raw TEXT, -- Pipe-separated raw ingredient text
    ingredients_json TEXT, -- JSON array of parsed ingredients
    steps TEXT, -- Pipe-separated steps
    images TEXT, -- Image URL
    tags TEXT, -- Pipe-separated tags
    author_tip TEXT,
    description TEXT,
    source TEXT DEFAULT 'marmiton', -- Source of the recipe
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name);
CREATE INDEX IF NOT EXISTS idx_recipes_url ON recipes(url);

-- Ingredients table (scraped from Marmiton)
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    image_url TEXT,
    source TEXT DEFAULT 'marmiton', -- e.g. 'marmiton'
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);

-- Junction table for many-to-many relationship between recipes and ingredients
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity TEXT, -- e.g. "350"
    unit TEXT, -- e.g. "g", "cuillères à soupe"
    raw_text TEXT, -- Original ingredient text
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    UNIQUE(recipe_id, ingredient_id)
);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient ON recipe_ingredients(ingredient_id);

