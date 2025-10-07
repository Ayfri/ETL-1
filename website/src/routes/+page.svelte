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

    async function loadFoods() {
        loadError = null;
        try {
            const res = await fetch(`/api/foods?page=${page}&limit=${limit}`);
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
		<header class="text-center mb-12">
			<h1 class="text-5xl font-bold text-gray-900 mb-3">Encyclopédie Nutritionnelle</h1>
			<p class="text-xl text-gray-600 mb-8">
				Explorez les aliments et importez des données Open Food Facts
			</p>

			<div class="flex flex-wrap justify-center gap-4">
				<button
					class="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-all shadow-sm hover:shadow-md"
				>
					<span class="text-2xl">📖</span>
					<span class="font-medium">Encyclopédie</span>
				</button>
				<button
					class="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-all shadow-sm hover:shadow-md"
				>
					<span class="text-2xl">📄</span>
					<span class="font-medium">Importer CSV</span>
				</button>
			</div>
		</header>

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

	<!-- Pagination -->
	<div class="fixed bottom-6 left-1/2 -translate-x-1/2 bg-white/80 backdrop-blur-md rounded-full px-4 py-2 shadow-lg flex items-center gap-3">
		<button onclick={prevPage} class="px-3 py-1 bg-gray-100 rounded-md">Préc</button>
		<span class="text-sm">Page {page} / {Math.max(1, Math.ceil(total / limit))}</span>
		<button onclick={nextPage} class="px-3 py-1 bg-gray-100 rounded-md">Suiv</button>
	</div>
</div>
