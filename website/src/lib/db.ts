import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

// Get directory name in ES module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let db: Database.Database | null = null;

/**
 * Get or create database connection
 */
export function getDatabase(): Database.Database {
	if (db) return db;

	// Try to find the database file
	const candidatePaths = [
		path.resolve(__dirname, '../../..', 'database', 'openfoodfacts.db'),
		path.resolve(__dirname, '../..', 'database', 'openfoodfacts.db'),
		path.resolve(__dirname, '..', 'database', 'openfoodfacts.db'),
		path.resolve(process.cwd(), '..', 'database', 'openfoodfacts.db')
	];

	let dbPath: string | null = null;
	for (const p of candidatePaths) {
		try {
			if (fs.existsSync(p)) {
				dbPath = p;
				break;
			}
		} catch {
			continue;
		}
	}

	if (!dbPath) {
		throw new Error(
			`Database not found in any of: ${candidatePaths.join(', ')}\n` +
			'Please run: uv run python database/create_db.py && uv run python scripts/load/load_to_sqlite.py'
		);
	}

	db = new Database(dbPath, { fileMustExist: true });

	// Enable WAL mode for better concurrent read performance
	db.pragma('journal_mode = WAL');

	console.log(`✓ Connected to database: ${dbPath}`);
	return db;
}

/**
 * Close database connection
 */
export function closeDatabase(): void {
	if (db) {
		db.close();
		db = null;
	}
}

/**
 * Food product interface
 */
export interface FoodProduct {
	code: string;
	product_name: string;
	brands?: string;
	categories?: string;
	main_category?: string;
	main_category_en?: string;
	nutriscore_grade?: string;
	nova_group?: number;
	image_url?: string;
	image_small_url?: string;
	energy_kcal_100g?: number;
	fat_100g?: number;
	saturated_fat_100g?: number;
	carbohydrates_100g?: number;
	sugars_100g?: number;
	proteins_100g?: number;
	salt_100g?: number;
	fiber_100g?: number;
	ingredients_text?: string;
	allergens?: string;
	additives_n?: number;
	completeness?: number;
}

/**
 * Recipe interface
 */
export interface Recipe {
    id?: number;
    name: string;
    author_tip?: string;
    budget?: string;
    cook_time?: string;
    difficulty?: string;
    images?: string; // JSON array serialized as string
    ingredients_raw?: string; // Pipe-separated raw ingredient text
    ingredients_json?: string; // JSON array serialized as string
    nb_comments?: string;
    prep_time?: string;
    rate?: string;
    recipe_quantity?: string;
    steps?: string; // JSON array serialized as string
    total_time?: string;
    url?: string;
    description?: string;
    created_at?: string;
    updated_at?: string;
}

/**
 * Query recipes (list)
 */
export function queryRecipes({
    page = 1,
    limit = 50,
    search = '',
    ingredient = '',
    sortBy = 'created_at',
    sortOrder = 'desc',
    difficulty = [] as string[],
    budget = [] as string[]
}: {
    page?: number;
    limit?: number;
    search?: string;
    ingredient?: string;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
    difficulty?: string[];
    budget?: string[];
}): { recipes: Recipe[]; total: number; pages: number } {
    const database = getDatabase();

    const whereClauses: string[] = [];
    const params: any[] = [];

    if (search) {
        whereClauses.push('(name LIKE ?)');
        params.push(`%${search}%`);
    }

    if (ingredient) {
        // simple substring match on the serialized ingredients field
        whereClauses.push('(ingredients LIKE ?)');
        params.push(`%${ingredient}%`);
    }

    if (difficulty.length > 0) {
        const placeholders = difficulty.map(() => '?').join(',');
        whereClauses.push(`difficulty IN (${placeholders})`);
        params.push(...difficulty);
    }

    if (budget.length > 0) {
        const placeholders = budget.map(() => '?').join(',');
        whereClauses.push(`budget IN (${placeholders})`);
        params.push(...budget);
    }

    const whereClause = whereClauses.length > 0 ? `WHERE ${whereClauses.join(' AND ')}` : '';

    const countQuery = `SELECT COUNT(*) as total FROM recipes ${whereClause}`;
    const countResult = database.prepare(countQuery).get(...params) as { total: number };
    const total = countResult.total;

    const offset = (page - 1) * limit;
    const orderClause = `ORDER BY ${sortBy} ${sortOrder.toUpperCase()}`;
    const query = `
        SELECT * FROM recipes
        ${whereClause}
        ${orderClause}
        LIMIT ? OFFSET ?
    `;

    const recipes = database.prepare(query).all(...params, limit, offset) as Recipe[];
    const pages = Math.ceil(total / limit);

    return { recipes, total, pages };
}

/**
 * Create a new recipe
 */
export function createRecipe(recipe: Recipe): Recipe {
    const database = getDatabase();

    const stmt = database.prepare(`
        INSERT INTO recipes (
            name, author_tip, budget, cook_time, difficulty, images, ingredients_raw, ingredients_json,
            nb_comments, prep_time, rate, recipe_quantity, steps, total_time, url, description, created_at, updated_at
        ) VALUES (
            @name, @author_tip, @budget, @cook_time, @difficulty, @images, @ingredients_raw, @ingredients_json,
            @nb_comments, @prep_time, @rate, @recipe_quantity, @steps, @total_time, @url, @description, datetime('now'), NULL
        )
    `);

    const info = stmt.run({
        name: recipe.name,
        author_tip: recipe.author_tip || null,
        budget: recipe.budget || null,
        cook_time: recipe.cook_time || null,
        difficulty: recipe.difficulty || null,
        images: recipe.images || null,
        ingredients_raw: (recipe as any).ingredients_raw || null,
        ingredients_json: (recipe as any).ingredients_json || null,
        nb_comments: recipe.nb_comments || null,
        prep_time: recipe.prep_time || null,
        rate: recipe.rate || null,
        recipe_quantity: recipe.recipe_quantity || null,
        steps: recipe.steps || null,
        total_time: recipe.total_time || null,
        url: recipe.url || null,
        description: recipe.description || null
    });

    const id = info.lastInsertRowid as number;
    return { ...recipe, id, created_at: new Date().toISOString() };
}

/**
 * Query products with filters and pagination
 */
export function queryProducts({
	page = 1,
	limit = 100,
	categories = [] as string[],
	sortBy = 'name',
	sortOrder = 'asc',
	search = ''
}: {
	page?: number;
	limit?: number;
	categories?: string[];
	sortBy?: string;
	sortOrder?: string;
	search?: string;
}): { products: FoodProduct[]; total: number; pages: number } {
	const database = getDatabase();

	// Build WHERE clause
	const whereClauses: string[] = [];
	const params: any[] = [];

	if (categories.length > 0) {
		const categoryConditions = categories.map(() => 'categories LIKE ?').join(' OR ');
		whereClauses.push(`(${categoryConditions})`);
		categories.forEach(cat => params.push(`%${cat}%`));
	}

	if (search) {
		whereClauses.push('(product_name LIKE ? OR brands LIKE ? OR categories LIKE ?)');
		params.push(`%${search}%`, `%${search}%`, `%${search}%`);
	}

	const whereClause = whereClauses.length > 0 ? `WHERE ${whereClauses.join(' AND ')}` : '';

	// Build ORDER BY clause
	let orderByClause = 'ORDER BY ';
	switch (sortBy) {
		case 'name':
			orderByClause += 'product_name';
			break;
		case 'nutriscore':
			orderByClause += 'nutriscore_grade';
			break;
		case 'energy':
			orderByClause += 'energy_kcal_100g';
			break;
		case 'nova':
			orderByClause += 'nova_group';
			break;
		default:
			orderByClause += 'product_name';
	}
	orderByClause += ` ${sortOrder.toUpperCase()} NULLS LAST`;

	// Get total count
	const countQuery = `SELECT COUNT(*) as total FROM products_with_nutrition ${whereClause}`;
	const countResult = database.prepare(countQuery).get(...params) as { total: number };
	const total = countResult.total;

	// Get paginated products
	const offset = (page - 1) * limit;
	const query = `
		SELECT 
			code,
			product_name,
			brands,
			categories,
			main_category,
			main_category_en,
			nutriscore_grade,
			nova_group,
			image_url,
			image_small_url,
			energy_kcal_100g,
			fat_100g,
			saturated_fat_100g,
			carbohydrates_100g,
			sugars_100g,
			proteins_100g,
			salt_100g,
			fiber_100g,
			ingredients_text,
			allergens,
			additives_n,
			completeness
		FROM products_with_nutrition
		${whereClause}
		${orderByClause}
		LIMIT ? OFFSET ?
	`;

	const products = database.prepare(query).all(...params, limit, offset) as FoodProduct[];
	const pages = Math.ceil(total / limit);

	return { products, total, pages };
}

/**
 * Get a single product by code
 */
export function getProductByCode(code: string): FoodProduct | null {
	const database = getDatabase();

	const query = `
		SELECT 
			code,
			product_name,
			brands,
			categories,
			main_category,
			main_category_en,
			nutriscore_grade,
			nova_group,
			image_url,
			image_small_url,
			energy_kcal_100g,
			fat_100g,
			saturated_fat_100g,
			carbohydrates_100g,
			sugars_100g,
			proteins_100g,
			salt_100g,
			fiber_100g,
			ingredients_text,
			allergens,
			additives_n,
			completeness
		FROM products_with_nutrition
		WHERE code = ?
	`;

	return database.prepare(query).get(code) as FoodProduct | null;
}

/**
 * Get available categories
 */
export function getCategories(): string[] {
	const database = getDatabase();

	const query = `
		SELECT DISTINCT main_category_en
		FROM products
		WHERE main_category_en IS NOT NULL
		ORDER BY main_category_en
	`;

	const results = database.prepare(query).all() as { main_category_en: string }[];
	return results.map(r => r.main_category_en);
}

/**
 * Get database statistics
 */
export function getStatistics(): {
	totalProducts: number;
	withNutriscore: number;
	withNova: number;
	highQuality: number;
} {
	const database = getDatabase();

	return {
		totalProducts: (database.prepare('SELECT COUNT(*) as count FROM products').get() as { count: number }).count,
		withNutriscore: (database.prepare('SELECT COUNT(*) as count FROM products WHERE nutriscore_grade IS NOT NULL').get() as { count: number }).count,
		withNova: (database.prepare('SELECT COUNT(*) as count FROM products WHERE nova_group IS NOT NULL').get() as { count: number }).count,
		highQuality: (database.prepare('SELECT COUNT(*) as count FROM products WHERE completeness >= 0.8').get() as { count: number }).count
	};
}
