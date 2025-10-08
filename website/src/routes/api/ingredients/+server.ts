import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getDatabase } from '$lib/db';

export const GET: RequestHandler = async ({ url }) => {
    try {
        const page = parseInt(url.searchParams.get('page') || '1', 10) || 1;
        const limit = parseInt(url.searchParams.get('limit') || '100', 10) || 100;

        const db = getDatabase();
        const offset = (page - 1) * limit;

        const totalRow = db.prepare('SELECT COUNT(*) as total FROM ingredients').get();
        const total = totalRow ? totalRow.total : 0;

        const rows = db.prepare('SELECT id, name, image_url FROM ingredients ORDER BY name LIMIT ? OFFSET ?').all(limit, offset);

        return json({ data: rows, total, page, limit });
    } catch (err) {
        console.error('Error querying ingredients:', err);
        return json({ error: 'Failed to query ingredients' }, { status: 500 });
    }
};


