import { json } from '@sveltejs/kit';
import { queryProducts, getCategories, getStatistics } from '$lib/db';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
	try {
		const page = parseInt(url.searchParams.get('page') || '1', 10) || 1;
		const limit = parseInt(url.searchParams.get('limit') || '100', 10) || 100;
		const category = url.searchParams.get('category') || '';
		const categories = category ? category.split(',').map(c => c.trim().toLowerCase()) : [];
		const sortBy = url.searchParams.get('sort') || 'name';
		const sortOrder = url.searchParams.get('order') || 'asc';
		const search = url.searchParams.get('search') || '';

		// Query products from database
		const result = queryProducts({
			page,
			limit,
			categories,
			sortBy,
			sortOrder,
			search
		});

		// Transform products to match the expected format
		const foods = result.products.map((product, idx) => ({
			id: (page - 1) * limit + idx + 1,
			name: product.product_name || 'Unknown',
			type: product.main_category_en || product.categories?.split(',')[0] || '',
			image: product.image_url || product.image_small_url || '',
			url: `https://world.openfoodfacts.org/product/${product.code}`,
			nutrition: {
				calories: product.energy_kcal_100g || 0,
				protein: product.proteins_100g || 0,
				carbs: product.carbohydrates_100g || 0,
				fat: product.fat_100g || 0,
				fiber: product.fiber_100g || 0
			},
			vitamins: [],
			minerals: [],
			benefits: product.categories?.split(',').map(s => s.trim()).filter(Boolean) || [],
			nutriScore: (product.nutriscore_grade || '').toUpperCase()
		}));

		// Get additional metadata if requested
		let stats = undefined;
		let availableCategories = undefined;

		if (url.searchParams.get('include_stats') === 'true') {
			stats = getStatistics();
		}

		if (url.searchParams.get('include_categories') === 'true') {
			availableCategories = getCategories();
		}

		return json({
			data: foods,
			total: result.total,
			page,
			limit,
			...(stats && { stats }),
			...(availableCategories && { categories: availableCategories })
		});
	} catch (error) {
		console.error('Error querying database:', error);
		return json(
			{
				error: 'Failed to query products',
				message: error instanceof Error ? error.message : 'Unknown error'
			},
			{ status: 500 }
		);
	}
};
