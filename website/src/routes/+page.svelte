<script lang="ts">
    import { flip } from 'svelte/animate';
    import { fly } from 'svelte/transition';
    import FoodCard from '$lib/components/FoodCard.svelte';
    import FoodDetails from '$lib/components/FoodDetails.svelte';
    import { ChevronLeft, ChevronRight, ArrowUp, ArrowDown, BookOpen, Filter, ArrowUpDown } from '@lucide/svelte';
    import type { Food } from '$lib/types';
    import type { PageData } from './$types.js';

    interface Props {
        data: PageData;
    }

    let { data }: Props = $props();

    let selectedFood = $state<Food | null>(null);

    // Données chargées dynamiquement depuis le CSV via l'endpoint avec pagination
    let foods = $state<Food[]>([]);
    let page = $state<number>(data.page);
    let total = $state<number>(0);

    let loadError = $state<string | null>(null);

    // Filtres
    let selectedCategories = $state<Set<string>>(new Set(data.categories));
    const categories = ['Bakery', 'Beverages', 'Dairy', 'Fruits', 'Meat', 'Snacks', 'Sweets', 'Vegetables'];

    // Tri
    let sortBy = $state<string>(data.sortBy);
    let sortOrder = $state<'asc' | 'desc'>(data.sortOrder as 'asc' | 'desc');

    const sortOptions = [
        { value: 'name', label: 'Nom' },
        { value: 'calories', label: 'Calories' },
        { value: 'protein', label: 'Protéines' },
        { value: 'carbs', label: 'Glucides' },
        { value: 'fat', label: 'Lipides' }
    ];

    let loadTimeout: ReturnType<typeof setTimeout> | null = null;
    const appearDelayBase = 35; // ms per item
    function computeDelay(index: number) {
        return index * appearDelayBase;
    }

    async function loadFoods() {
        loadError = null;
        try {
            const categoryParam = selectedCategories.size > 0 ? `&category=${Array.from(selectedCategories).join(',')}` : '';
            const sortParam = `&sort=${sortBy}&order=${sortOrder}`;
            const res = await fetch(`/api/foods?page=${page}&limit=${data.limit}${categoryParam}${sortParam}`);
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

    function debouncedLoadFoods() {
        if (loadTimeout) clearTimeout(loadTimeout);
        loadTimeout = setTimeout(() => {
            loadFoods();
        }, 300); // 300ms debounce
    }

    // Charger les données initiales depuis le load avec streaming
    $effect(() => {
        if (data.foods) {
            data.foods.then((result: any) => {
                foods = result.data || [];
                total = result.total || 0;
            }).catch((err: any) => {
                console.error('Erreur chargement initial', err);
                loadError = 'Erreur de chargement initial';
            });
        }
    });

    function toggleCategory(category: string) {
        if (selectedCategories.has(category)) {
            selectedCategories.delete(category);
        } else {
            selectedCategories.add(category);
        }
        selectedCategories = new Set(selectedCategories); // trigger reactivity
        page = 1; // reset to first page
        debouncedLoadFoods();
    }

    function changeSort(newSortBy: string) {
        if (sortBy === newSortBy) {
            sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            sortBy = newSortBy;
            sortOrder = 'asc';
        }
        page = 1; // reset to first page
        debouncedLoadFoods();
    }

    function nextPage() {
        const maxPage = Math.max(1, Math.ceil(total / data.limit));
        if (page < maxPage) {
            page += 1;
            loadFoods();
        }
    }

    function prevPage() {
        if (page > 1) {
            page -= 1;
            loadFoods();
        }
    }

    function goToPage(newPage: number) {
        const maxPage = Math.max(1, Math.ceil(total / data.limit));
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
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 transition-transform duration-500 ease-in-out {selectedFood ? '-translate-x-64' : 'translate-x-0'}">
		<!-- Header -->
		<header class="text-center mb-8">
			<div class="flex items-center justify-center gap-3 mb-2">
				<BookOpen size={40} class="text-emerald-600" />
				<h1 class="text-4xl font-bold text-gray-900">Encyclopédie Nutritionnelle</h1>
			</div>
			<p class="text-lg text-gray-600">
				Explorez les aliments et importez des données Open Food Facts
			</p>
		</header>

		<!-- Filters and Controls -->
		<div class="mb-8 space-y-6">
			<!-- Filters -->
			<div>
				<div class="flex items-center gap-2 mb-4">
					<Filter size={20} class="text-gray-600" />
					<h2 class="text-xl font-semibold text-gray-800">Filtres par catégorie</h2>
				</div>
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
					<div class="flex items-center gap-2">
						<ArrowUpDown size={16} class="text-gray-600" />
						<span class="text-sm font-medium text-gray-700">Trier par:</span>
					</div>
					<div class="flex gap-2">
						{#each sortOptions as option}
							<button
								class="cursor-pointer px-3 py-1 text-sm rounded-md transition-all flex items-center gap-1 {sortBy === option.value
									? 'bg-emerald-500 text-white'
									: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
								onclick={() => changeSort(option.value)}
							>
								<span>{option.label}</span>
								{#if sortBy === option.value}
									{#if sortOrder === 'asc'}
										<ArrowUp size={14} />
									{:else}
										<ArrowDown size={14} />
									{/if}
								{/if}
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
					<ChevronLeft size={16} />
				</button>

				<div class="flex items-center gap-2">
					<span class="text-sm font-medium">Page</span>
                    <input
                        type="number"
                        min="1"
                        max={Math.max(1, Math.ceil(total / data.limit))}
                        value={page}
                        onchange={(e: Event) => goToPage(parseInt((e.target as HTMLInputElement).value) || 1)}
                        class="w-16 px-2 py-1 text-center border border-gray-300 rounded text-sm"
                    />
					<span class="text-sm">sur {Math.max(1, Math.ceil(total / data.limit))}</span>
				</div>

				<button onclick={nextPage} disabled={page >= Math.max(1, Math.ceil(total / data.limit))} class="cursor-pointer px-4 py-2 bg-gray-100 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 transition-colors">
					<ChevronRight size={16} />
				</button>
			</div>
		</div>

		<!-- Food Grid -->
		<div
			class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
		>
            {#each foods as food, i (food.id)}
                <div animate:flip={{ duration: 300 }} in:fly={{ y: 8, duration: 260, delay: computeDelay(i) }}>
                    <FoodCard {food} selected={selectedFood?.id === food.id} onclick={() => selectFood(food)} />
                </div>
            {/each}
		</div>
	</div>

	<!-- Details Panel -->
	<div class="fixed inset-y-0 right-0 w-96 bg-white shadow-2xl z-50 transition-all duration-500 ease-in-out {selectedFood ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}">
		{#if selectedFood}
			<FoodDetails food={selectedFood} onclose={closeDetails} />
		{/if}
	</div>
</div>
