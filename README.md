# ETL OpenFoodFacts

Projet ETL (Extract, Transform, Load) pour l'analyse des données alimentaires de la base OpenFoodFacts.

## 📋 Description

Ce projet implémente un pipeline ETL complet pour :
1. **Extraire** les données d'OpenFoodFacts (700 000+ produits)
2. **Transformer** et nettoyer les données
3. **Charger** dans une base de données SQLite pour analyse

## 🏗️ Structure du projet

```
etl-1/
├── data/
│   ├── raw/                          # Données brutes téléchargées
│   │   └── openfoodfacts.csv.gz
│   └── processed/                    # Données nettoyées
│       └── openfoodfacts_filtered.csv
├── database/
│   ├── schema.sql                    # Schéma de la base de données
│   ├── create_db.py                  # Script de création de la BDD
│   ├── openfoodfacts.db             # Base de données SQLite
│   └── README.md                     # Documentation de la BDD
├── scripts/
│   ├── extract/
│   │   └── download_open_food_facts.py  # Téléchargement des données
│   ├── transform/
│   │   └── filter_openfoodfacts.py     # Nettoyage et filtrage
│   └── load/
│       ├── load_to_sqlite.py           # Chargement dans SQLite
│       └── verify_data.py              # Vérification d'intégrité
├── notebooks/                        # Notebooks Jupyter pour l'analyse
├── website/                          # Interface web (SvelteKit)
├── pyproject.toml                    # Configuration du projet Python
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

Télécharger les données depuis OpenFoodFacts :

```bash
uv run python scripts/extract/download_open_food_facts.py
```

**Résultat** : `data/raw/openfoodfacts.csv.gz` (~700 000 produits, ~1.5 GB compressé)

### 2. Transformation (Transform)

Nettoyer et filtrer les données :

```bash
uv run python scripts/transform/filter_openfoodfacts.py
```

**Critères de filtrage** :
- Produits avec Nutri-Score valide
- Données nutritionnelles présentes
- Produits complets avec images

**Résultat** : `data/processed/openfoodfacts_filtered.csv` (~6 200 produits de qualité)

### 3. Chargement (Load)

Créer et remplir la base de données SQLite :

```bash
# 1. Créer la structure de la base de données
uv run python database/create_db.py

# 2. Charger les données
uv run python scripts/load/load_to_sqlite.py

# 3. Vérifier l'intégrité
uv run python scripts/load/verify_data.py
```

**Résultat** : `database/openfoodfacts.db` (base SQLite prête à l'emploi)

## 🗄️ Base de données

### Schéma

La base de données contient deux tables principales :

#### Table `products`
- Informations produit (nom, marque, catégorie)
- Emballage et origine
- Ingrédients et allergènes
- Scores de qualité (Nutri-Score, NOVA)
- Images et métadonnées

#### Table `nutrition_facts`
- Valeurs nutritionnelles pour 100g
- Macronutriments (protéines, lipides, glucides)
- Vitamines et minéraux
- Relation avec `products` via clé étrangère

### Vues pré-configurées

- `products_with_nutrition` : Jointure produits + nutrition
- `high_quality_products` : Produits ≥80% complets avec Nutri-Score

### Exemples de requêtes

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

Voir [database/README.md](database/README.md) pour plus d'exemples.

## 📈 Statistiques

Après le pipeline complet :

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

Une interface web SvelteKit est disponible pour visualiser et explorer les données interactivement.

### Lancement du site

```bash
# Aller dans le dossier website
cd website

# Installer les dépendances
pnpm install

# Lancer en mode développement
pnpm dev
```

Le site sera accessible sur `http://localhost:5173` (ou 5174 si 5173 est occupé).

### Fonctionnalités

- 🔍 **Recherche** par nom, marque ou catégorie
- 📊 **Tri** par Nutri-Score, calories, NOVA group
- 🎯 **Filtrage** par catégories multiples
- 📄 **Pagination** fluide
- 📷 **Images** des produits
- 📈 **Statistiques** globales

### API REST

Le site expose une API REST pour interroger la base de données :

```
GET /api/foods?page=1&limit=100&sort=nutriscore&order=asc
```

Voir [website/README.md](website/README.md) pour la documentation complète de l'API.

## 🌐 Interface Web (optionnel)

Une interface web SvelteKit est disponible dans le dossier `website/` pour visualiser les données.

```bash
cd website
pnpm install
pnpm dev
```

## 📝 Notes techniques

### Gestion des dépendances avec UV

Ce projet utilise `uv` comme gestionnaire de packages moderne pour Python :

- **Fichier de dépendances** : `pyproject.toml` (source unique)
- **Lock file** : `uv.lock` (versions exactes, committé)
- **Installation** : `uv sync` (reproductible)
- **Ajout de package** : `uv add <package>`
- **Exécution** : `uv run python script.py`

Voir [.github/copilot-instructions.md](.github/copilot-instructions.md) pour plus de détails.

### Format des données

- Les codes produits sont stockés en TEXT (barcode format)
- Les valeurs manquantes sont NULL dans la base
- Les données nutritionnelles sont pour 100g
- Encoding UTF-8 pour tous les fichiers

### Limitations connues

- Quelques valeurs nutritionnelles hors plages attendues (données source)
- Certaines incohérences mineures (ex: graisses saturées > graisses totales dans 18 cas)
- 1 produit CSV non chargé (problème de format du code)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -am 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📄 Licence

Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🔗 Ressources

- [OpenFoodFacts](https://world.openfoodfacts.org/) - Source des données
- [Documentation UV](https://docs.astral.sh/uv/) - Gestionnaire de packages
- [SQLite](https://www.sqlite.org/) - Base de données utilisée
- [Pandas](https://pandas.pydata.org/) - Manipulation de données

## 📧 Contact

Pour toute question ou suggestion, ouvrez une issue sur GitHub.

---

**Note** : Ce projet est réalisé dans un cadre éducatif pour démontrer un pipeline ETL complet avec Python et SQLite.
