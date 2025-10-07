// @ts-nocheck
import fs from 'fs';
import path from 'path';
import readline from 'readline';

let cachedData: Record<string, string>[] | null = null;

function splitCSVLine(line: string) {
	const result: string[] = [];
	let cur = '';
	let inQuotes = false;
	for (let i = 0; i < line.length; i++) {
		const ch = line[i];
		if (ch === '"') {
			if (inQuotes && line[i + 1] === '"') {
				cur += '"';
				i++; // skip escaped quote
			} else {
				inQuotes = !inQuotes;
			}
		} else if (ch === ',' && !inQuotes) {
			result.push(cur);
			cur = '';
		} else {
			cur += ch;
		}
	}
	result.push(cur);
	return result;
}

async function loadCSVData(): Promise<Record<string, string>[]> {
	if (cachedData) return cachedData;

	const candidatePaths = [
		path.resolve(process.cwd(), 'data', 'processed', 'openfoodfacts_filtered.csv'),
		path.resolve(process.cwd(), '..', 'data', 'processed', 'openfoodfacts_filtered.csv'),
		path.resolve(process.cwd(), 'data', 'raw', 'openfoodfacts_sample.csv'),
		path.resolve(process.cwd(), '..', 'data', 'raw', 'openfoodfacts_sample.csv')
	];
	let csvPath: string | null = null;
	for (const p of candidatePaths) {
		if (fs.existsSync(p)) {
			csvPath = p;
			break;
		}
	}
	if (!csvPath) throw new Error(`CSV file not found in ${candidatePaths.join(' or ')}`);

	const stream = fs.createReadStream(csvPath, { encoding: 'utf8' });
	const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });

	let headers: string[] | null = null;
	const rows: Record<string, string>[] = [];

	for await (const line of rl) {
		if (!headers) {
			headers = splitCSVLine(line).map(h => h.trim());
			continue;
		}
		if (!line) continue;

		const values = splitCSVLine(line);
		const obj: Record<string, string> = {};
		for (let i = 0; i < headers.length; i++) obj[headers[i]] = values[i] ?? '';
		rows.push(obj);
	}

	cachedData = rows;
	return rows;
}

export async function GET({ url }) {
  try {
    const page = parseInt(url.searchParams.get('page') || '1', 10) || 1;
    const limit = parseInt(url.searchParams.get('limit') || '100', 10) || 100;
    const category = url.searchParams.get('category') || '';
    const categories = category ? category.split(',').map(c => c.trim().toLowerCase()) : [];
    const sortBy = url.searchParams.get('sort') || 'name';
    const sortOrder = url.searchParams.get('order') || 'asc';
    const start = (page - 1) * limit;

    const allRows = await loadCSVData();

    // Filter by category if specified
    const allFilteredRows = categories.length > 0
      ? allRows.filter(obj => {
          const productCategories = (obj['categories'] || '').toLowerCase();
          return categories.some(cat => productCategories.includes(cat));
        })
      : allRows;

    // Sort the filtered rows
    allFilteredRows.sort((a, b) => {
      let aVal: any, bVal: any;
      switch (sortBy) {
        case 'name':
          aVal = (a['product_name'] || a['generic_name'] || 'Unknown').toLowerCase();
          bVal = (b['product_name'] || b['generic_name'] || 'Unknown').toLowerCase();
          break;
        case 'calories':
          aVal = parseFloat(a['energy-kcal_100g'] || a['energy_100g'] || '0') || 0;
          bVal = parseFloat(b['energy-kcal_100g'] || b['energy_100g'] || '0') || 0;
          break;
        case 'protein':
          aVal = parseFloat(a['proteins_100g'] || '0') || 0;
          bVal = parseFloat(b['proteins_100g'] || '0') || 0;
          break;
        case 'carbs':
          aVal = parseFloat(a['carbohydrates_100g'] || '0') || 0;
          bVal = parseFloat(b['carbohydrates_100g'] || '0') || 0;
          break;
        case 'fat':
          aVal = parseFloat(a['fat_100g'] || '0') || 0;
          bVal = parseFloat(b['fat_100g'] || '0') || 0;
          break;
        default:
          aVal = (a['product_name'] || a['generic_name'] || 'Unknown').toLowerCase();
          bVal = (b['product_name'] || b['generic_name'] || 'Unknown').toLowerCase();
      }
      
      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    // Apply pagination
    const selectedRows = allFilteredRows.slice(start, start + limit);
    const totalRows = allFilteredRows.length;

    const foods = selectedRows.map((r, idx) => {
      const calories = parseFloat(r['energy-kcal_100g'] || r['energy_100g'] || '0') || 0;
      return {
        id: start + idx + 1,
        name: r['product_name'] || r['generic_name'] || 'Unknown',
        type: (r['categories'] || '').split(',')[0] || '',
        image: r['image_url'] || r['image_small_url'] || '',
        url: r['url'] || '',
        nutrition: {
          calories,
          protein: parseFloat(r['proteins_100g'] || '0') || 0,
          carbs: parseFloat(r['carbohydrates_100g'] || '0') || 0,
          fat: parseFloat(r['fat_100g'] || '0') || 0,
          fiber: parseFloat(r['fiber_100g'] || '0') || 0
        },
        vitamins: Object.keys(r)
          .filter(k => k.startsWith('vitamin-') && r[k])
          .map(k => `${k.replace('vitamin-', 'Vitamin ').replace(/_100g$/, '')}: ${r[k]}`),
        minerals: ['potassium_100g', 'sodium_100g', 'calcium_100g', 'iron_100g']
          .filter(k => r[k])
          .map(k => `${k.split('_')[0]}: ${r[k]}`),
        benefits: ((r['categories_en'] || r['categories'] || '') as string)
          .split(',')
          .map((s: string) => s.trim())
          .filter(Boolean),
        nutriScore: (r['nutriscore_grade'] || '').toUpperCase()
      };
    });

    return new Response(JSON.stringify({ data: foods, total: totalRows, page, limit }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), { status: 500 });
  }
}


