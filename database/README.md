# Base de données OpenFoodFacts

Ce dossier contient la base de données SQLite pour le projet ETL OpenFoodFacts.

## Structure de la base de données

La base de données est organisée en deux tables principales :

### Table `products`
Contient toutes les informations produit :
- **Identifiants** : code, nom du produit, marques
- **Catégories** : catégories, groupes alimentaires
- **Emballage** : quantité, type d'emballage
- **Origine** : pays, lieux de fabrication, magasins
- **Ingrédients** : texte, allergènes, traces
- **Labels** : certifications, labels
- **Scores de qualité** : Nutri-Score, NOVA, score environnemental
- **Images** : URLs des photos du produit
- **Métadonnées** : dates de création/modification, complétude

### Table `nutrition_facts`
Contient les valeurs nutritionnelles pour 100g :
- Énergie (kJ, kcal)
- Lipides (total, saturés, acides gras)
- Glucides (total, sucres, amidon, fibres)
- Protéines
- Sel et sodium
- Vitamines (A, B, C, D, E, K)
- Minéraux (calcium, fer, magnésium, etc.)
- Autres composés (caféine, alcool, etc.)

### Vues
- **`products_with_nutrition`** : Jointure des produits avec leurs principales valeurs nutritionnelles
- **`high_quality_products`** : Produits avec au moins 80% de complétude et Nutri-Score

### Index
Des index sont créés sur les colonnes fréquemment recherchées :
- Marques
- Catégories
- Pays
- Nutri-Score
- NOVA group

## Fichiers

- `schema.sql` : Définition du schéma de la base de données
- `create_db.py` : Script pour créer la base de données et les tables
- `openfoodfacts.db` : Base de données SQLite (générée)

## Création de la base de données

```bash
# Créer la structure de la base de données
uv run python database/create_db.py
```

## Chargement des données

```bash
# Charger les données du CSV filtré dans la base
uv run python scripts/load/load_to_sqlite.py
```

## Vérification de l'intégrité

```bash
# Vérifier la cohérence et l'intégrité des données
uv run python scripts/load/verify_data.py
```

## Utilisation de la base de données

### Python avec sqlite3

```python
import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('database/openfoodfacts.db')
cursor = conn.cursor()

# Exemple : Obtenir les produits avec le meilleur Nutri-Score
cursor.execute("""
    SELECT product_name, brands, nutriscore_grade 
    FROM products 
    WHERE nutriscore_grade = 'a'
    LIMIT 10
""")
for row in cursor.fetchall():
    print(row)

conn.close()
```

### Python avec pandas

```python
import sqlite3
import pandas as pd

# Lire depuis la base de données
conn = sqlite3.connect('database/openfoodfacts.db')

# Exemple : Analyser les produits par Nutri-Score
df = pd.read_sql_query("""
    SELECT nutriscore_grade, COUNT(*) as count, 
           AVG(energy_kcal_100g) as avg_energy
    FROM products_with_nutrition
    WHERE nutriscore_grade IS NOT NULL
    GROUP BY nutriscore_grade
    ORDER BY nutriscore_grade
""", conn)

print(df)
conn.close()
```

### Requêtes SQL utiles

```sql
-- Top 10 des marques les plus présentes
SELECT brands, COUNT(*) as count 
FROM products 
WHERE brands IS NOT NULL 
GROUP BY brands 
ORDER BY count DESC 
LIMIT 10;

-- Produits végans avec bon Nutri-Score
SELECT product_name, brands, nutriscore_grade
FROM products
WHERE ingredients_analysis_tags LIKE '%en:vegan%'
  AND nutriscore_grade IN ('a', 'b')
LIMIT 20;

-- Moyennes nutritionnelles par groupe NOVA
SELECT nova_group,
       AVG(energy_kcal_100g) as avg_energy,
       AVG(fat_100g) as avg_fat,
       AVG(sugars_100g) as avg_sugars,
       AVG(proteins_100g) as avg_proteins,
       COUNT(*) as product_count
FROM products_with_nutrition
WHERE nova_group IS NOT NULL
GROUP BY nova_group
ORDER BY nova_group;

-- Produits avec le plus d'additifs
SELECT product_name, brands, additives_n, additives
FROM products
WHERE additives_n > 5
ORDER BY additives_n DESC
LIMIT 10;
```

## Statistiques de la base de données

Après chargement, la base contient :
- ~6,263 produits
- ~6,264 enregistrements nutritionnels
- Tous les produits ont un Nutri-Score
- ~78% des produits ont un groupe NOVA
- ~24% des produits sont hautement complets (≥80%)

## Intégrité référentielle

La base de données utilise des clés étrangères pour garantir l'intégrité :
- `nutrition_facts.product_code` → `products.code`

Les contraintes ON DELETE CASCADE assurent que la suppression d'un produit supprime aussi ses données nutritionnelles.

## Notes

- Les valeurs manquantes sont stockées comme NULL
- Les codes produits sont stockés en tant que TEXT
- Certaines valeurs nutritionnelles peuvent dépasser les plages attendues (données source)
- La base utilise SQLite 3, compatible avec la plupart des outils d'analyse
