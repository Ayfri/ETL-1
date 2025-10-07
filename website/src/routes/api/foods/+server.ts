// @ts-nocheck
import fs from 'fs';
import path from 'path';
import readline from 'readline';

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

function parseCSV(text: string) {
	const lines = text.split(/\r?\n/);
 	const headerLine = lines.shift();
 	if (!headerLine) return [];
 	const headers = splitCSVLine(headerLine).map(h => h.trim());
 	const rows = [] as Record<string, string>[];
 	for (const line of lines) {
 		if (!line) continue;
 		const values = splitCSVLine(line);
 		// skip malformed lines
 		if (values.length === 1 && values[0] === '') continue;
 		const obj: Record<string, string> = {};
 		for (let i = 0; i < headers.length; i++) {
 			obj[headers[i]] = values[i] ?? '';
 		}
 		rows.push(obj);
 	}
 	return rows;
}

export async function GET({ url }) {
  try {
    const page = parseInt(url.searchParams.get('page') || '1', 10) || 1;
    const limit = parseInt(url.searchParams.get('limit') || '100', 10) || 100;
    const start = (page - 1) * limit;

    // Try common locations for the CSV: project root `data/raw/...` or website parent
    const candidatePaths = [
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
    let rowIndex = 0; // zero-based index for data rows (excluding header)
    const selectedRows: Record<string, string>[] = [];

    for await (const line of rl) {
      if (!headers) {
        headers = splitCSVLine(line).map(h => h.trim());
        continue;
      }
      if (!line) continue;

      // only collect rows in the requested window
      if (rowIndex >= start && selectedRows.length < limit) {
        const values = splitCSVLine(line);
        const obj: Record<string, string> = {};
        for (let i = 0; i < headers.length; i++) obj[headers[i]] = values[i] ?? '';
        selectedRows.push(obj);
      }

      rowIndex++;
    }

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

    return new Response(JSON.stringify({ data: foods, total: rowIndex, page, limit }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), { status: 500 });
  }
}


