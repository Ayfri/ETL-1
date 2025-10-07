# OpenFoodFacts Website

Interface web interactive pour explorer les données alimentaires d'OpenFoodFacts.

## 🚀 Fonctionnalités

- **Recherche et filtrage** : Recherchez des produits par nom, marque ou catégorie
- **Tri avancé** : Triez par nom, Nutri-Score, énergie, NOVA group
- **Pagination** : Navigation fluide à travers des milliers de produits
- **Détails produits** : Informations nutritionnelles complètes
- **Nutri-Score** : Indicateurs visuels de qualité nutritionnelle
- **Images** : Photos des produits (si disponibles)

## 📦 Technologies

- **SvelteKit** : Framework web moderne et performant
- **TypeScript** : Typage statique pour plus de robustesse
- **Better-SQLite3** : Accès rapide à la base de données SQLite
- **Vite** : Build tool ultra-rapide

## 🛠️ Installation

### Prérequis

- Node.js ≥ 18
- pnpm (recommandé) ou npm
- Base de données SQLite générée (voir README principal)

### Setup

```bash
# Installer les dépendances
pnpm install

# Lancer en mode développement
pnpm dev

# Builder pour la production
pnpm build

# Prévisualiser la version de production
pnpm preview
```

## 🗄️ Connexion à la base de données

Le site utilise automatiquement la base de données SQLite située dans `../database/openfoodfacts.db`.

**Important** : Assurez-vous d'avoir créé et rempli la base de données avant de lancer le site :

```bash
# Depuis la racine du projet
uv run python database/create_db.py
uv run python scripts/load/load_to_sqlite.py
```

## 📂 Structure

```
website/
├── src/
│   ├── lib/
│   │   ├── db.ts                    # Module de connexion SQLite
│   │   ├── components/              # Composants Svelte
│   │   │   ├── FoodCard.svelte
│   │   │   └── FoodDetails.svelte
│   │   ├── assets/
│   │   └── types/
│   │       └── index.ts
│   └── routes/
│       ├── +layout.svelte           # Layout principal
│       ├── +page.svelte             # Page d'accueil
│       ├── +page.server.ts          # Server-side logic
│       └── api/
│           └── foods/
│               └── +server.ts       # API endpoint
├── static/                          # Fichiers statiques
├── package.json
├── svelte.config.js
├── tsconfig.json
└── vite.config.ts
```

## 🔌 API Endpoints

### GET /api/foods

Récupère une liste paginée de produits.

**Paramètres de requête** :

- `page` (number, default: 1) : Numéro de page
- `limit` (number, default: 100) : Nombre de produits par page
- `category` (string) : Filtrer par catégorie (séparées par virgules)
- `sort` (string) : Trier par (`name`, `nutriscore`, `energy`, `nova`)
- `order` (string) : Ordre (`asc`, `desc`)
- `search` (string) : Recherche textuelle
- `include_stats` (boolean) : Inclure les statistiques globales
- `include_categories` (boolean) : Inclure la liste des catégories

**Exemple** :

```http
GET /api/foods?page=1&limit=50&sort=nutriscore&order=asc
```

**Réponse** :

```json
{
  "data": [
    {
      "id": 1,
      "name": "Product Name",
      "type": "Category",
      "image": "https://...",
      "url": "https://world.openfoodfacts.org/product/...",
      "nutrition": {
        "calories": 123,
        "protein": 10,
        "carbs": 20,
        "fat": 5,
        "fiber": 3
      },
      "nutriScore": "A"
    }
  ],
  "total": 6263,
  "page": 1,
  "limit": 50
}
```

## 🎨 Personnalisation

### Modifier le nombre de produits par page

Éditez `src/routes/+page.server.ts` :

```typescript
const limit = parseInt(url.searchParams.get('limit') || '100', 10) || 100;
```

### Ajouter de nouveaux filtres

1. Ajoutez le paramètre dans `src/lib/db.ts` (fonction `queryProducts`)
2. Modifiez la requête SQL pour inclure le filtre
3. Ajoutez l'interface dans `src/routes/+page.svelte`

### Personnaliser l'apparence

Les styles sont dans les fichiers `.svelte`. Modifiez les sections `<style>` de chaque composant.

## 🐛 Débogage

### Erreur "Database not found"

La base de données SQLite n'est pas trouvée. Vérifiez :

1. Que le fichier `../database/openfoodfacts.db` existe
2. Que vous avez exécuté les scripts de création et chargement
3. Le chemin dans `src/lib/db.ts` (fonction `getDatabase`)

### Erreur de type TypeScript

Régénérez les types SvelteKit :

```bash
pnpm run check
```

### Performance lente

- Vérifiez que les index sont créés dans la base de données
- Réduisez la limite de produits par page
- Activez le mode WAL de SQLite (déjà fait dans `db.ts`)

## 📊 Optimisations

### Mode production

```bash
# Builder
pnpm build

# Lancer
node build
```

### Optimisations SQLite

La connexion à la base utilise déjà :

- Mode WAL (Write-Ahead Logging) pour de meilleures performances en lecture
- Connexion read-only pour éviter les locks
- Index sur les colonnes fréquemment recherchées

## 🤝 Contribution

Pour ajouter des fonctionnalités :

1. Créez une branche : `git checkout -b feature/nom-feature`
2. Développez localement avec `pnpm dev`
3. Testez : `pnpm run check` et `pnpm run build`
4. Committez : `git commit -am 'Ajout feature'`
5. Push : `git push origin feature/nom-feature`
6. Créez une Pull Request

## 📝 Scripts disponibles

```bash
pnpm dev          # Serveur de développement
pnpm build        # Build de production
pnpm preview      # Prévisualiser le build
pnpm check        # Vérifier les types TypeScript
pnpm lint         # Linter le code
pnpm format       # Formatter le code
```

## 🔗 Ressources

- [SvelteKit Documentation](https://svelte.dev/docs/kit)
- [Better-SQLite3](https://github.com/WiseLibs/better-sqlite3)
- [OpenFoodFacts API](https://world.openfoodfacts.org/data)
- [Vite](https://vite.dev/)

## 📄 Licence

Voir le fichier [LICENSE](../LICENSE) à la racine du projet.

---

**Note** : Ce site web est une interface pour visualiser les données de la base SQLite. Il nécessite que le pipeline ETL soit exécuté au préalable.
