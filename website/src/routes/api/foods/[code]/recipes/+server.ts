import { json } from '@sveltejs/kit';
import { getRecipesForProduct, getMatchedIngredientsForProduct } from '$lib/db';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params }) => {
	try {
		const productCode = params.code;

		if (!productCode) {
			return json({ error: 'Product code is required' }, { status: 400 });
		}

		const recipes = getRecipesForProduct(productCode);
		const matchedIngredients = getMatchedIngredientsForProduct(productCode);

		return json({
			recipes,
			matchedIngredients
		});
	} catch (error) {
		console.error('Error fetching product recipes:', error);
		return json(
			{ error: 'Failed to fetch product recipes' },
			{ status: 500 }
		);
	}
};
