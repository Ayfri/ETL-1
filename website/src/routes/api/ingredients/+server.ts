import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getDatabase } from '$lib/db';

export const GET: RequestHandler = async ({ url }) => {
    try {
        const page = parseInt(url.searchParams.get('page') || '1', 10) || 1;
        const limit = parseInt(url.searchParams.get('limit') || '100', 10) || 100;
        const letterParam = url.searchParams.get('letter') || '';

        const db = getDatabase();
        const offset = (page - 1) * limit;

        // Build where clause for letter filtering (case-insensitive)
        let whereClause = '';
        const params: any[] = [];
        if (letterParam) {
            whereClause = 'WHERE LOWER(name) LIKE ?';
            params.push(`${letterParam.toLowerCase()}%`);
        }

        const totalRow = db.prepare(`SELECT COUNT(*) as total FROM ingredients ${whereClause}`).get(...params);
        const total = totalRow ? totalRow.total : 0;

        const rows = db.prepare(`SELECT id, name, image_url FROM ingredients ${whereClause} ORDER BY name LIMIT ? OFFSET ?`).all(...params, limit, offset);

        return json({ data: rows, total, page, limit, letter: letterParam });
    } catch (err) {
        console.error('Error querying ingredients:', err);
        return json({ error: 'Failed to query ingredients' }, { status: 500 });
    }
};


