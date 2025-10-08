import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { queryRecipes, createRecipe } from '$lib/db';

export const GET: RequestHandler = async ({ url }) => {
    try {
        const page = parseInt(url.searchParams.get('page') || '1', 10) || 1;
        const limit = parseInt(url.searchParams.get('limit') || '50', 10) || 50;
        const search = url.searchParams.get('search') || '';
        const ingredient = url.searchParams.get('ingredient') || '';
        const sortBy = url.searchParams.get('sort') || 'created_at';
        const sortOrder = (url.searchParams.get('order') || 'desc') as 'asc' | 'desc';
        const difficultyParam = url.searchParams.get('difficulty') || '';
        const budgetParam = url.searchParams.get('budget') || '';

        const difficulty = difficultyParam ? difficultyParam.split(',').filter(Boolean) : [];
        const budget = budgetParam ? budgetParam.split(',').filter(Boolean) : [];

        const result = queryRecipes({ page, limit, search, ingredient, sortBy, sortOrder, difficulty, budget });

        return json({ data: result.recipes, total: result.total, pages: result.pages, page, limit });
    } catch (error) {
        console.error('Error querying recipes:', error);
        return json({ error: 'Failed to query recipes', message: error instanceof Error ? error.message : 'Unknown' }, { status: 500 });
    }
};

export const POST: RequestHandler = async ({ request }) => {
    try {
        const body = await request.json();

        // Basic validation
        if (!body || !body.name) {
            return json({ error: 'Missing recipe name' }, { status: 400 });
        }

        const recipe = createRecipe(body);
        return json({ data: recipe }, { status: 201 });
    } catch (error) {
        console.error('Error creating recipe:', error);
        return json({ error: 'Failed to create recipe', message: error instanceof Error ? error.message : 'Unknown' }, { status: 500 });
    }
};
