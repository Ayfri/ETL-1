# Schéma de la base de données OpenFoodFacts

## Diagramme Entité-Relations

```
┌──────────────────────────────────────────────────────────────┐
│                         PRODUCTS                              │
├──────────────────────────────────────────────────────────────┤
│ 🔑 code (TEXT) PRIMARY KEY                                   │
├──────────────────────────────────────────────────────────────┤
│ Informations produit:                                         │
│   • product_name, abbreviated_product_name, generic_name      │
│   • brands, brands_tags, brands_en, brand_owner               │
│                                                                │
│ Catégories:                                                   │
│   • categories, categories_tags, categories_en                │
│   • main_category, main_category_en                           │
│   • pnns_groups_1, pnns_groups_2                              │
│   • food_groups, food_groups_tags, food_groups_en            │
│                                                                │
│ Détails produit:                                             │
│   • quantity, product_quantity, packaging                     │
│   • packaging_tags, packaging_en, packaging_text              │
│                                                                │
│ Origine géographique:                                         │
│   • origins, origins_tags, origins_en                         │
│   • manufacturing_places, manufacturing_places_tags           │
│   • purchase_places, stores                                   │
│   • countries, countries_tags, countries_en                   │
│   • cities, cities_tags                                       │
│                                                                │
│ Labels et certifications:                                     │
│   • labels, labels_tags, labels_en                            │
│   • emb_codes, emb_codes_tags                                 │
│   • first_packaging_code_geo                                  │
│                                                                │
│ Ingrédients:                                                  │
│   • ingredients_text, ingredients_tags                        │
│   • ingredients_analysis_tags                                 │
│   • allergens, allergens_en                                   │
│   • traces, traces_tags, traces_en                            │
│   • serving_size, serving_quantity                            │
│                                                                │
│ Additifs:                                                     │
│   • additives_n (INTEGER)                                     │
│   • additives, additives_tags, additives_en                   │
│                                                                │
│ Scores de qualité:                                            │
│   • nutriscore_score (REAL), nutriscore_grade (TEXT)          │
│   • nova_group (REAL)                                         │
│   • environmental_score_score, environmental_score_grade      │
│   • nutrient_levels_tags                                      │
│   • nutrition_score_fr_100g, nutrition_score_uk_100g          │
│                                                                │
│ Complétude et qualité:                                        │
│   • states, states_tags, states_en                            │
│   • completeness (REAL)                                       │
│   • no_nutrition_data, data_quality_errors_tags               │
│                                                                │
│ Popularité:                                                   │
│   • unique_scans_n (INTEGER)                                  │
│   • popularity_tags                                           │
│                                                                │
│ Images:                                                        │
│   • image_url, image_small_url                                │
│   • image_ingredients_url, image_ingredients_small_url        │
│   • image_nutrition_url, image_nutrition_small_url            │
│                                                                │
│ Métadonnées:                                                  │
│   • url, creator, owner                                       │
│   • created_t, created_datetime                               │
│   • last_modified_t, last_modified_datetime, last_modified_by │
│   • last_updated_t, last_updated_datetime                     │
│   • last_image_t, last_image_datetime                         │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     NUTRITION_FACTS                           │
├──────────────────────────────────────────────────────────────┤
│ 🔑 id (INTEGER) PRIMARY KEY AUTOINCREMENT                    │
│ 🔗 product_code (TEXT) FOREIGN KEY → products.code           │
├──────────────────────────────────────────────────────────────┤
│ Énergie:                                                      │
│   • energy_kj_100g, energy_kcal_100g                          │
│   • energy_100g, energy_from_fat_100g                         │
│                                                                │
│ Lipides (REAL):                                               │
│   • fat_100g, saturated_fat_100g                              │
│   • butyric_acid_100g, caproic_acid_100g, caprylic_acid_100g │
│   • capric_acid_100g, lauric_acid_100g, myristic_acid_100g   │
│   • palmitic_acid_100g, stearic_acid_100g                     │
│   • arachidic_acid_100g, behenic_acid_100g                    │
│   • lignoceric_acid_100g, cerotic_acid_100g                   │
│   • montanic_acid_100g, melissic_acid_100g                    │
│   • unsaturated_fat_100g, monounsaturated_fat_100g            │
│   • polyunsaturated_fat_100g                                  │
│   • omega_3_fat_100g, omega_6_fat_100g, omega_9_fat_100g     │
│   • trans_fat_100g, cholesterol_100g                          │
│                                                                │
│ Acides gras (REAL):                                           │
│   • alpha_linolenic_acid_100g, eicosapentaenoic_acid_100g    │
│   • docosahexaenoic_acid_100g, linoleic_acid_100g             │
│   • arachidonic_acid_100g, gamma_linolenic_acid_100g          │
│   • dihomo_gamma_linolenic_acid_100g, oleic_acid_100g         │
│   • elaidic_acid_100g, gondoic_acid_100g, mead_acid_100g     │
│   • erucic_acid_100g, nervonic_acid_100g                      │
│                                                                │
│ Glucides (REAL):                                              │
│   • carbohydrates_100g, sugars_100g, added_sugars_100g        │
│   • sucrose_100g, glucose_100g, fructose_100g                 │
│   • lactose_100g, maltose_100g, maltodextrins_100g            │
│   • starch_100g, polyols_100g, erythritol_100g                │
│                                                                │
│ Fibres (REAL):                                                │
│   • fiber_100g, soluble_fiber_100g, insoluble_fiber_100g      │
│                                                                │
│ Protéines (REAL):                                             │
│   • proteins_100g, casein_100g                                │
│   • serum_proteins_100g, nucleotides_100g                     │
│                                                                │
│ Sel et sodium (REAL):                                         │
│   • salt_100g, added_salt_100g, sodium_100g                   │
│                                                                │
│ Alcool (REAL):                                                │
│   • alcohol_100g                                              │
│                                                                │
│ Vitamines (REAL):                                             │
│   • vitamin_a_100g, beta_carotene_100g                        │
│   • vitamin_d_100g, vitamin_e_100g, vitamin_k_100g            │
│   • vitamin_c_100g, vitamin_b1_100g, vitamin_b2_100g          │
│   • vitamin_pp_100g, vitamin_b6_100g, vitamin_b9_100g         │
│   • folates_100g, vitamin_b12_100g                            │
│   • biotin_100g, pantothenic_acid_100g                        │
│                                                                │
│ Minéraux (REAL):                                              │
│   • silica_100g, bicarbonate_100g                             │
│   • potassium_100g, chloride_100g                             │
│   • calcium_100g, phosphorus_100g                             │
│   • iron_100g, magnesium_100g, zinc_100g                      │
│   • copper_100g, manganese_100g, fluoride_100g                │
│   • selenium_100g, chromium_100g, molybdenum_100g, iodine_100g│
│                                                                │
│ Autres composés (REAL):                                       │
│   • caffeine_100g, taurine_100g, ph_100g                      │
│   • fruits_vegetables_nuts_100g                               │
│   • fruits_vegetables_nuts_dried_100g                         │
│   • fruits_vegetables_nuts_estimate_100g                      │
│   • fruits_vegetables_nuts_estimate_from_ingredients_100g     │
│   • collagen_meat_protein_ratio_100g                          │
│   • cocoa_100g, chlorophyl_100g                               │
│   • carbon_footprint_100g                                     │
│   • carbon_footprint_from_meat_or_fish_100g                   │
│   • glycemic_index_100g, water_hardness_100g                  │
│   • choline_100g, phylloquinone_100g, beta_glucan_100g        │
│   • inositol_100g, carnitine_100g                             │
└──────────────────────────────────────────────────────────────┘
```

## Index créés

Pour optimiser les performances des requêtes :

```sql
CREATE INDEX idx_products_brands ON products(brands);
CREATE INDEX idx_products_categories ON products(categories);
CREATE INDEX idx_products_countries ON products(countries);
CREATE INDEX idx_products_nutriscore ON products(nutriscore_grade);
CREATE INDEX idx_products_nova ON products(nova_group);
CREATE INDEX idx_nutrition_product_code ON nutrition_facts(product_code);
```

## Vues pré-configurées

### `products_with_nutrition`

Jointure simplifiée des informations produit avec leurs valeurs nutritionnelles principales :

```sql
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
LEFT JOIN nutrition_facts n ON p.code = n.product_code;
```

### `high_quality_products`

Filtre des produits de haute qualité :

```sql
SELECT *
FROM products
WHERE completeness >= 0.8
  AND nutriscore_grade IS NOT NULL
  AND image_url IS NOT NULL;
```

## Notes sur les types de données

- **TEXT** : Chaînes de caractères (codes, noms, descriptions, tags)
- **INTEGER** : Nombres entiers (compteurs, timestamps Unix)
- **REAL** : Nombres décimaux (valeurs nutritionnelles, scores)

Les valeurs manquantes sont représentées par `NULL`.

## Clés et relations

- **Clé primaire de `products`** : `code` (code-barres du produit)
- **Clé étrangère** : `nutrition_facts.product_code` → `products.code`
- **Contrainte** : `ON DELETE CASCADE` (suppression en cascade)

## Taille de la base

- **Produits** : ~6 263 entrées
- **Nutrition** : ~6 264 entrées
- **Taille du fichier** : ~10-15 MB (non compressé)

## Requêtes d'exemple

Voir le fichier [scripts/load/query_examples.py](../scripts/load/query_examples.py) pour des exemples complets de requêtes.
