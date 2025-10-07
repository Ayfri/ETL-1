<script lang="ts">
    import { onMount } from 'svelte';
    import FoodCard from '$lib/components/FoodCard.svelte';
    import FoodDetails from '$lib/components/FoodDetails.svelte';
    import type { Food } from '$lib/types';

    let selectedFood = $state<Food | null>(null);

    // Données chargées dynamiquement depuis le CSV via l'endpoint avec pagination
    let foods = $state<Food[]>([]);
    let page = $state<number>(1);
    const limit = 100;
    let total = $state<number>(0);

    let loadError = $state<string | null>(null);

    // Filtres
    let selectedCategories = $state<Set<string>>(new Set());
    const categories = ['Bakery', 'Beverages', 'Dairy', 'Fruits', 'Meat', 'Snacks', 'Sweets', 'Vegetables'];

    // Tri
    let sortBy = $state<string>('name');
    let sortOrder = $state<'asc' | 'desc'>('asc');
    const sortOptions = [
        { value: 'name', label: 'Nom' },
        { value: 'calories', label: 'Calories' },
        { value: 'protein', label: 'Protéines' },
        { value: 'carbs', label: 'Glucides' },
        { value: 'fat', label: 'Lipides' }
    ];

    async function loadFoods() {
        loadError = null;
        try {
            const categoryParam = selectedCategories.size > 0 ? `&category=${Array.from(selectedCategories).join(',')}` : '';
            const sortParam = `&sort=${sortBy}&order=${sortOrder}`;
            const res = await fetch(`/api/foods?page=${page}&limit=${limit}${categoryParam}${sortParam}`);
            const text = await res.text();
            if (!res.ok) {
                let serverMsg = text;
                try {
                    const parsed = JSON.parse(text || '{}');
                    serverMsg = parsed.error || JSON.stringify(parsed);
                } catch (e) {
                    // keep raw text
                }
                console.error('API error', res.status, serverMsg);
                throw new Error(serverMsg || 'Échec du chargement des aliments');
            }
            const json = text ? JSON.parse(text) : {};
            foods = json.data || [];
            total = json.total || 0;
        } catch (err: unknown) {
            const msg = (err && typeof err === 'object' && 'message' in err) ? (err as any).message : String(err);
            console.error('Échec du chargement des aliments', msg);
            loadError = String(msg);
            foods = [];
            total = 0;
        }
    }

    onMount(loadFoods);

    function toggleCategory(category: string) {
        if (selectedCategories.has(category)) {
            selectedCategories.delete(category);
        } else {
            selectedCategories.add(category);
        }
        selectedCategories = new Set(selectedCategories); // trigger reactivity
        page = 1; // reset to first page
        loadFoods();
    }

    function changeSort(newSortBy: string) {
        if (sortBy === newSortBy) {
            sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            sortBy = newSortBy;
            sortOrder = 'asc';
        }
        page = 1; // reset to first page
        loadFoods();
    }

    function nextPage() {
        const maxPage = Math.max(1, Math.ceil(total / limit));
        if (page < maxPage) {
            page = page + 1;
            loadFoods();
        }
    }

    function prevPage() {
        if (page > 1) {
            page = page - 1;
            loadFoods();
        }
    }

    function goToPage(newPage: number) {
        const maxPage = Math.max(1, Math.ceil(total / limit));
        if (newPage >= 1 && newPage <= maxPage) {
            page = newPage;
            loadFoods();
        }
    }

    function selectFood(food: Food) {
        selectedFood = food;
    }

    function closeDetails() {
        selectedFood = null;
    }
</script>

<div class="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<header class="text-center mb-8">
			<h1 class="text-4xl font-bold text-gray-900 mb-2">Encyclopédie Nutritionnelle</h1>
			<p class="text-lg text-gray-600">
				Explorez les aliments et importez des données Open Food Facts
			</p>
		</header>

		<!-- Filters and Controls -->
		<div class="mb-8 space-y-6">
			<!-- Filters -->
			<div>
				<h2 class="text-xl font-semibold text-gray-800 mb-4">Filtres par catégorie</h2>
				<div class="flex flex-wrap gap-2">
					{#each categories as category}
						<button
							class="cursor-pointer px-4 py-2 rounded-full text-sm font-medium transition-all {selectedCategories.has(category)
								? 'bg-emerald-500 text-white shadow-md'
								: 'bg-white text-gray-700 border border-gray-300 hover:border-emerald-400 hover:bg-emerald-50'}"
							onclick={() => toggleCategory(category)}
						>
							{category}
						</button>
					{/each}
				</div>
			</div>

			<!-- Sort and Pagination Controls -->
			<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
				<!-- Sort Controls -->
				<div class="flex items-center gap-4">
					<span class="text-sm font-medium text-gray-700">Trier par:</span>
					<div class="flex gap-2">
						{#each sortOptions as option}
							<button
								class="cursor-pointer px-3 py-1 text-sm rounded-md transition-all {sortBy === option.value
									? 'bg-emerald-500 text-white'
									: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
								onclick={() => changeSort(option.value)}
							>
								{option.label} {sortBy === option.value ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
							</button>
						{/each}
					</div>
				</div>

				<!-- Product Count -->
				<div class="text-sm text-gray-600">
					{foods.length} produits affichés sur {total} au total
				</div>
			</div>

			<!-- Pagination -->
			<div class="flex items-center justify-center gap-4 bg-white/80 backdrop-blur-sm rounded-lg px-6 py-3 shadow-sm">
				<button onclick={prevPage} disabled={page <= 1} class="cursor-pointer px-4 py-2 bg-gray-100 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 transition-colors">
					Précédent
				</button>
				
				<div class="flex items-center gap-2">
					<span class="text-sm font-medium">Page</span>
					<input 
						type="number" 
						min="1" 
						max={Math.max(1, Math.ceil(total / limit))} 
						value={page} 
						onchange={(e) => goToPage(parseInt(e.target.value) || 1)}
						class="w-16 px-2 py-1 text-center border border-gray-300 rounded text-sm"
					/>
					<span class="text-sm">sur {Math.max(1, Math.ceil(total / limit))}</span>
				</div>
				
				<button onclick={nextPage} disabled={page >= Math.max(1, Math.ceil(total / limit))} class="cursor-pointer px-4 py-2 bg-gray-100 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 transition-colors">
					Suivant
				</button>
			</div>
		</div>

		<!-- Food Grid -->
		<div
			class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 {selectedFood
				? 'md:mr-96'
				: ''} transition-all duration-300"
		>
			{#each foods as food (food.id)}
				<FoodCard {food} selected={selectedFood?.id === food.id} onclick={() => selectFood(food)} />
			{/each}
		</div>
	</div>

	<!-- Details Panel -->
	<FoodDetails food={selectedFood} onclose={closeDetails} />
</div>
