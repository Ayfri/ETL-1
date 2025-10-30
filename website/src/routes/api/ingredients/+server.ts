import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getDatabase } from '$lib/db';

export const GET: RequestHandler = async ({ url }) => {
    try {
        const page = parseInt(url.searchParams.get('page') || '1', 10) || 1;
        const limit = parseInt(url.searchParams.get('limit') || '100', 10) || 100;
        const letterParam = url.searchParams.get('letter') || '';
        const q = (url.searchParams.get('q') || '').trim();

        const db = getDatabase();
        const offset = (page - 1) * limit;

        // Build where clause for filtering (case-insensitive)
        let whereClause = '';
        const params: any[] = [];
        if (letterParam) {
            whereClause = 'WHERE LOWER(name) LIKE ?';
            params.push(`${letterParam.toLowerCase()}%`);
        }
        if (q) {
            if (whereClause) whereClause += ' AND LOWER(name) LIKE ?';
            else whereClause = 'WHERE LOWER(name) LIKE ?';
            params.push(`%${q.toLowerCase()}%`);
        }

        const totalRow = db.prepare(`SELECT COUNT(*) as total FROM ingredients ${whereClause}`).get(...params);
        const total = totalRow ? totalRow.total : 0;

        // Get ingredients with recipe counts in a single query
        const query = `
            SELECT 
                i.id, 
                i.name, 
                i.image_url,
                COALESCE(COUNT(ri.recipe_id), 0) as recipeCount
            FROM ingredients i
            LEFT JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
            ${whereClause}
            GROUP BY i.id, i.name, i.image_url
            ORDER BY i.name
            LIMIT ? OFFSET ?
        `;
        
        console.log('Query:', query);
        console.log('Params:', [...params, limit, offset]);
        
        const rows = db.prepare(query).all(...params, limit, offset) as any[];
        
        console.log('Rows returned:', rows);
        console.log('First row:', rows[0]);
        console.log('Recipe count of first:', rows[0]?.recipeCount);

        return json({ data: rows, total, page, limit, letter: letterParam, q });
    } catch (err) {
        console.error('Error querying ingredients:', err);
        return json({ error: 'Failed to query ingredients' }, { status: 500 });
    }
};


