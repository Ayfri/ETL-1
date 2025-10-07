export async function load({ url, fetch }: { url: URL, fetch: typeof globalThis.fetch }) {
	const page = parseInt(url.searchParams.get('page') || '1', 10) || 1;
	const limit = parseInt(url.searchParams.get('limit') || '100', 10) || 100;
	const category = url.searchParams.get('category') || '';
	const categories = category ? category.split(',').map((c: string) => c.trim().toLowerCase()) : [];
	const sortBy = url.searchParams.get('sort') || 'name';
	const sortOrder = url.searchParams.get('order') || 'asc';

	// Retourner une promise pour le streaming
	const dataPromise = fetch(`/api/foods?page=${page}&limit=${limit}&category=${category}&sort=${sortBy}&order=${sortOrder}`)
		.then((res: Response) => res.json());

	return {
		foods: dataPromise,
		page,
		limit,
		categories,
		sortBy,
		sortOrder
	};
};