# ETL Alimentaire - OpenFoodFacts & Marmiton

Projet ETL complet pour l'analyse des données alimentaires combinant les produits OpenFoodFacts et les recettes Marmiton.

## 📋 Description

Ce projet implémente un pipeline ETL complet pour :
1. **Extraire** les données de produits alimentaires d'OpenFoodFacts (700 000+ produits)
2. **Extraire** les recettes et ingrédients de Marmiton
3. **Transformer** et nettoyer les données
4. **Charger** dans une base de données SQLite relationnelle
5. **Explorer** les données via une interface web interactive

## 🏗️ Structure du projet

```
etl-1/
├── data/
│   ├── raw/                          # Données brutes téléchargées
│   │   ├── openfoodfacts_sample.csv  # Échantillon OpenFoodFacts
│   │   ├── marmiton_recipes.csv      # Recettes Marmiton
│   │   └── ingredients_raw.csv       # Ingrédients bruts
│   └── processed/                    # Données nettoyées
│       ├── openfoodfacts_filtered.csv
│       └── marmiton_recipes_filtered.csv
├── database/
│   ├── schema.sql                    # Schéma complet de la BDD
│   ├── create_db.py                  # Script de création de la BDD
│   ├── db_manager.py                 # Gestionnaire de base de données
│   ├── openfoodfacts.db              # Base de données SQLite
│   └── README.md                     # Documentation de la BDD
├── scripts/
│   ├── extract/
│   │   ├── download_open_food_facts.py    # Téléchargement OpenFoodFacts
│   │   └── scrape_marmiton_ingredients.py # Scraping Marmiton
│   ├── transform/
│   │   ├── filter_openfoodfacts.py         # Nettoyage OpenFoodFacts
│   │   └── filter_marmiton_recipes.py      # Nettoyage Marmiton
│   └── load/
│       ├── load_to_sqlite.py               # Chargement des données
│       ├── match_recipes_with_ingredients.py # Association recettes-ingrédients
│       ├── query_examples.py               # Exemples de requêtes
│       └── verify_data.py                  # Vérification d'intégrité
├── notebooks/                        # Notebooks Jupyter pour l'analyse
├── website/                          # Interface web SvelteKit
│   ├── src/
│   │   ├── routes/
│   │   │   ├── ingredients/           # Exploration des ingrédients
│   │   │   └── recipes/               # Exploration des recettes
│   │   └── lib/
│   │       └── components/            # Composants Svelte
│   └── package.json
├── pyproject.toml                    # Configuration Python (UV)
├── uv.lock                          # Lock file des dépendances
└── README.md
```

## 🚀 Installation

Ce projet utilise [uv](https://docs.astral.sh/uv/) pour la gestion des dépendances Python.

### Prérequis

- Python ≥ 3.13
- uv (installé automatiquement si absent)

### Installation des dépendances

```bash
# Synchroniser l'environnement (créer venv + installer dépendances)
uv sync

# Activer l'environnement virtuel (optionnel avec uv)
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

## 📊 Pipeline ETL

### 1. Extraction (Extract)

#### Données OpenFoodFacts
Télécharger et échantillonner les données produits :

```bash
uv run python scripts/extract/download_open_food_facts.py
```

**Résultat** : `data/raw/openfoodfacts_sample.csv` (~1 million produits échantillonnés)

#### Données Marmiton
Scraper les recettes et ingrédients :

```bash
uv run python scripts/extract/scrape_marmiton_ingredients.py
```

**Résultat** :
- `data/raw/marmiton_recipes.csv` (recettes avec ingrédients)
- `data/raw/ingredients_raw.csv` (liste des ingrédients)

### 2. Transformation (Transform)

#### Nettoyage OpenFoodFacts
```bash
uv run python scripts/transform/filter_openfoodfacts.py
```

**Critères de filtrage** :
- Produits avec Nutri-Score valide
- Données nutritionnelles présentes
- Produits complets avec images

**Résultat** : `data/processed/openfoodfacts_filtered.csv` (~6 200 produits)

#### Nettoyage Marmiton
```bash
uv run python scripts/transform/filter_marmiton_recipes.py
```

**Résultat** : `data/processed/marmiton_recipes_filtered.csv`

### 3. Chargement (Load)

#### Création de la base de données
```bash
# Créer la structure complète
uv run python database/create_db.py
```

#### Chargement des données
```bash
# Charger les produits OpenFoodFacts
uv run python scripts/load/load_to_sqlite.py

# Charger les recettes et ingrédients Marmiton
uv run python scripts/load/match_recipes_with_ingredients.py
```

#### Vérification
```bash
uv run python scripts/load/verify_data.py
```

**Résultat** : `database/openfoodfacts.db` (base SQLite avec toutes les données)

## 🗄️ Base de données

### Schéma

La base de données contient quatre tables principales interconnectées :

#### Table `products` (OpenFoodFacts)
- Informations produit (nom, marque, catégorie)
- Emballage et origine géographique
- Ingrédients et allergènes
- Scores de qualité (Nutri-Score, NOVA, Eco-Score)
- Images et métadonnées
- Valeurs nutritionnelles pour 100g

#### Table `nutrition_facts`
- Valeurs nutritionnelles détaillées
- Macronutriments (protéines, lipides, glucides)
- Vitamines et minéraux
- Relation avec `products` via clé étrangère

#### Table `recipes` (Marmiton)
- Informations de recette (nom, URL, difficulté, budget)
- Temps de préparation et cuisson
- Ingrédients bruts et parsés (JSON)
- Étapes de préparation
- Images et tags
- Auteur et description

#### Table `ingredients` (Marmiton)
- Liste des ingrédients extraits des recettes
- Noms normalisés et images
- Source (Marmiton)

#### Table `recipe_ingredients` (relation many-to-many)
- Association recettes-ingrédients
- Quantités et unités extraites
- Texte brut original

### Vues et index

- `products_with_nutrition` : Jointure produits + nutrition
- `high_quality_products` : Produits ≥80% complets avec Nutri-Score
- Index sur noms, URLs, et relations pour des requêtes optimisées

### Exemples de requêtes

#### Produits OpenFoodFacts
```sql
-- Top 10 des produits avec le meilleur Nutri-Score
SELECT product_name, brands, nutriscore_grade, energy_kcal_100g
FROM products_with_nutrition
WHERE nutriscore_grade = 'a'
ORDER BY completeness DESC
LIMIT 10;

-- Moyennes nutritionnelles par groupe NOVA
SELECT nova_group,
       AVG(energy_kcal_100g) as avg_energy,
       AVG(sugars_100g) as avg_sugars,
       COUNT(*) as count
FROM products_with_nutrition
WHERE nova_group IS NOT NULL
GROUP BY nova_group
ORDER BY nova_group;
```

#### Recettes Marmiton
```sql
-- Recettes faciles avec moins de 30 min de préparation
SELECT name, prep_time, difficulty, rate
FROM recipes
WHERE difficulty = 'très facile'
  AND prep_time LIKE '%min%'
  AND CAST(REPLACE(REPLACE(prep_time, ' min', ''), ' h ', '60') AS INTEGER) < 30
ORDER BY rate DESC;

-- Ingrédients les plus utilisés
SELECT i.name, COUNT(ri.recipe_id) as recipe_count
FROM ingredients i
JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
GROUP BY i.id, i.name
ORDER BY recipe_count DESC
LIMIT 20;
```

#### Requêtes croisées
```sql
-- Recettes utilisant des ingrédients sains (Nutri-Score A/B)
SELECT DISTINCT r.name as recipe_name, r.difficulty, r.prep_time,
                p.product_name, p.nutriscore_grade
FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
JOIN ingredients i ON ri.ingredient_id = i.id
JOIN products p ON LOWER(p.product_name) LIKE '%' || LOWER(i.name) || '%'
WHERE p.nutriscore_grade IN ('a', 'b')
  AND p.main_category_en LIKE '%vegetables%'
LIMIT 10;
```

Voir [database/README.md](database/README.md) pour plus d'exemples.

## 📈 Statistiques

Après le pipeline complet :

### Produits OpenFoodFacts
- **Produits totaux** : 6 263
- **Avec Nutri-Score** : 100%
- **Avec groupe NOVA** : 78%
- **Haute qualité** (≥80% complet) : 24%
- **Avec images** : 100%

### Distribution Nutri-Score

| Grade | Nombre | Pourcentage |
|-------|--------|-------------|
| A     | 1 208  | 19.3%       |
| B     | 754    | 12.0%       |
| C     | 1 295  | 20.7%       |
| D     | 1 334  | 21.3%       |
| E     | 1 249  | 19.9%       |

### Recettes Marmiton
- **Recettes totales** : ~10 000+ (dépend du scraping)
- **Ingrédients extraits** : ~1 000+ ingrédients uniques
- **Associations recette-ingrédient** : ~50 000+

### Base de données complète
- **Tables** : 5 principales + vues
- **Relations** : Many-to-many entre recettes et ingrédients
- **Index** : Optimisés pour les recherches fréquentes

## 🛠️ Utilisation avec Python

```python
import sqlite3
import pandas as pd

# Connexion à la base de données
conn = sqlite3.connect('database/openfoodfacts.db')

# Requête avec pandas
df = pd.read_sql_query("""
    SELECT product_name, brands, nutriscore_grade, 
           energy_kcal_100g, proteins_100g, sugars_100g
    FROM products_with_nutrition
    WHERE countries LIKE '%France%'
    LIMIT 100
""", conn)

print(df.head())
conn.close()
```

## 🔍 Vérification de la qualité des données

Le script de vérification effectue plusieurs contrôles :

- ✅ Unicité des clés primaires
- ✅ Intégrité référentielle
- ✅ Plages de valeurs nutritionnelles
- ✅ Cohérence des données (ex: sucres ≤ glucides)
- ✅ Complétude des champs essentiels

```bash
uv run python scripts/load/verify_data.py
```

## 📦 Dépendances

Principales dépendances Python (définies dans `pyproject.toml`) :

- `pandas` : Manipulation de données
- `requests` : Téléchargement HTTP
- `beautifulsoup4` : Parsing HTML pour le scraping
- `aiohttp` : Requêtes HTTP asynchrones
- `python-marmiton` : Client API Marmiton
- `recipe-scrapers` : Extraction de recettes
- `tqdm` : Barres de progression

Installation :
```bash
# Ajouter une dépendance
uv add <package-name>

# Ajouter une dépendance dev
uv add --dev <package-name>

# Synchroniser après modification
uv sync
```

## 🌐 Interface Web

Une interface web SvelteKit complète permet d'explorer interactivement les données.

### Lancement du site

```bash
# Aller dans le dossier website
cd website

# Installer les dépendances
pnpm install

# Lancer en mode développement
pnpm dev
```

Le site sera accessible sur `http://localhost:5173`.

### Fonctionnalités

#### Exploration des Produits
- 🔍 **Recherche** par nom, marque ou catégorie
- 📊 **Tri** par Nutri-Score, calories, NOVA group
- 🎯 **Filtrage** par catégories multiples
- 📄 **Pagination** fluide
- 📷 **Images** des produits
- 📈 **Statistiques** globales

#### Exploration des Recettes
- 👨‍🍳 **Recettes** avec ingrédients et étapes détaillées
- 🥕 **Ingrédients** et leurs utilisations dans les recettes
- ⏱️ **Temps** de préparation et cuisson
- 💰 **Budget** et difficulté
- ⭐ **Notes** et commentaires

#### Navigation croisée
- 🔗 **Lien ingrédients-recettes** : Voir toutes les recettes utilisant un ingrédient
- 📊 **Analyse** des associations produits-recettes
- 🎨 **Interface moderne** avec animations fluides

### API REST

Le site expose une API REST complète :

```
GET /api/foods?page=1&limit=100&sort=nutriscore&order=asc
GET /api/ingredients?page=1&limit=50&query=tomate
GET /api/recipes?page=1&limit=20&ingredient=farine
```

Voir [website/README.md](website/README.md) pour la documentation complète de l'API.

## 📝 Notes techniques

### Gestion des dépendances avec UV

Ce projet utilise `uv` comme gestionnaire de packages moderne pour Python :

- **Fichier de dépendances** : `pyproject.toml` (source unique)
- **Lock file** : `uv.lock` (versions exactes, committé)
- **Installation** : `uv sync` (reproductible)
- **Ajout de package** : `uv add <package>`
- **Exécution** : `uv run python script.py`

Voir [.github/copilot-instructions.md](.github/copilot-instructions.md) pour plus de détails.

### Sources de données

#### OpenFoodFacts
- **Format** : CSV compressé (~2-3 GB)
- **Échantillonnage** : 1 million de produits pour les tests
- **Filtrage** : ~6 200 produits de haute qualité
- **Encoding** : UTF-8

#### Marmiton
- **Scraping** : Asyncio + BeautifulSoup4
- **Rate limiting** : 40 requêtes concurrentes max, 0.05s delay
- **Parsing** : Expressions régulières pour ingrédients
- **Normalisation** : Suppression des articles français

### Format des données

- Les codes produits sont stockés en TEXT (barcode format)
- Les valeurs manquantes sont NULL dans la base
- Les données nutritionnelles sont pour 100g
- Les ingrédients des recettes sont stockés en JSON parsé
- Encoding UTF-8 pour tous les fichiers

### Limitations connues

- Quelques valeurs nutritionnelles hors plages attendues (données source)
- Certaines incohérences mineures (ex: graisses saturées > graisses totales)
- Données Marmiton dépendent de la disponibilité du site
- Scraping soumis aux conditions d'utilisation de Marmiton

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -am 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📄 Licence

Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🔗 Ressources

- [OpenFoodFacts](https://world.openfoodfacts.org/) - Base de données produits alimentaires
- [Marmiton](https://www.marmiton.org/) - Recettes et ingrédients culinaires
- [Documentation UV](https://docs.astral.sh/uv/) - Gestionnaire de packages Python
- [SQLite](https://www.sqlite.org/) - Base de données utilisée
- [Pandas](https://pandas.pydata.org/) - Manipulation de données
- [SvelteKit](https://kit.svelte.dev/) - Framework web
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - Parsing HTML

## 📧 Contact

Pour toute question ou suggestion, ouvrez une issue sur GitHub.

---

**Note** : Ce projet est réalisé dans un cadre éducatif pour démontrer un pipeline ETL complet combinant scraping web, nettoyage de données et interface utilisateur moderne.
