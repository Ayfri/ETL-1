<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { fly } from 'svelte/transition';
    import RecipeModal from '$lib/components/RecipeModal.svelte';
    import IngredientsRecipesMenu from '$lib/components/IngredientsRecipesMenu.svelte';
    import { Search } from '@lucide/svelte';

    let ingredients = [] as any[];
    let loadError: string | null = null;
    let page = 1;
    let total = 0;
    let limit = 48;
    let query: string = '';
    let debouncedQuery: string = '';
    let searchTimeout: any = null;
    let appearDelayBase = 35; // ms per item

    // recipes menu state
    let showRecipesMenu = false;
    let selectedIngredient: string | null = null;
    let recipes = [] as any[];
    let recipesLoading = false;
    let recipesError: string | null = null;
    let selectedRecipe: any = null;
    let showRecipeModal = false;

    function closeRecipe() {
        showRecipeModal = false;
        selectedRecipe = null;
    }

    async function openIngredient(ingName: string) {
        selectedIngredient = ingName;
        showRecipesMenu = true;
        recipes = [];
        recipesError = null;
        recipesLoading = true;
        try {
            const res = await fetch(`/api/recipes?ingredient=${encodeURIComponent(ingName)}&limit=50`);
            if (!res.ok) throw new Error('Failed to fetch recipes');
            const json = await res.json();
            recipes = json.data || [];
        } catch (e) {
            console.error(e);
            recipesError = 'Erreur lors du chargement des recettes';
        } finally {
            recipesLoading = false;
        }
    }

    function closeRecipesMenu() {
        showRecipesMenu = false;
        selectedIngredient = null;
        recipes = [];
        recipesError = null;
    }

        async function loadIngredients() {
            loadError = null;
            try {
                const queryParam = debouncedQuery ? `&q=${encodeURIComponent(debouncedQuery)}` : '';
                const res = await fetch(`/api/ingredients?page=${page}&limit=${limit}${queryParam}`);
                if (!res.ok) throw new Error('Failed to fetch');
                const json = await res.json();
                ingredients = json.data || [];
                total = json.total || 0;
            } catch (e) {
                console.error(e);
                loadError = 'Erreur lors du chargement des ingrédients';
            }
        }

        onMount(() => loadIngredients());
    function computeDelay(index: number) {
        return index * appearDelayBase;
    }

    function capitalize(str: string): string {
        if (!str) return str;
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }

    function onQueryInput(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        query = target.value;
        if (searchTimeout) clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            debouncedQuery = query.trim();
            page = 1;
            loadIngredients();
        }, 350);
    }
</script>

<div class="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <header class="mb-6">
            <h1 class="text-3xl font-extrabold text-gray-900 flex items-center gap-3">
                <span class="inline-block w-2 h-8 bg-emerald-500 rounded"></span>
                Ingrédients
            </h1>
            <p class="text-sm text-gray-600 mt-1">Parcourez et cherchez les ingrédients — sélectionnez-en un pour voir les recettes associées.</p>
        </header>

        <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div class="flex items-center gap-3 w-full sm:max-w-md">
                <div class="flex items-center gap-2 bg-white border border-gray-200 px-3 py-2 rounded-full shadow-sm w-full">
                    <Search class="text-gray-400" />
                    <input placeholder="Rechercher..." class="outline-none w-full text-sm" value={query} oninput={onQueryInput} />
                    {#if query}
                        <button type="button" class="ml-2 text-sm text-gray-500" onclick={() => { query = ''; debouncedQuery = ''; page = 1; loadIngredients(); }}>Effacer</button>
                    {/if}
                </div>
            </div>

            <div class="flex items-center">
                <div class="bg-white/80 backdrop-blur-sm rounded-lg px-4 py-2 shadow-sm flex items-center gap-3">
                    <button type="button" class="px-3 py-1 bg-white border border-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50" onclick={() => { if (page > 1) { page -= 1; loadIngredients(); } }} disabled={page <= 1}>Préc</button>

                    <div class="flex items-center gap-2 text-sm text-gray-700">
                        <span>Page</span>
                        <input
                            type="number"
                            min="1"
                            max={Math.max(1, Math.ceil(total / limit))}
                            value={page}
                            onchange={(e) => { page = parseInt((e.target as HTMLInputElement).value) || 1; loadIngredients(); }}
                            class="w-16 px-2 py-1 text-center border border-gray-300 rounded text-sm"
                        />
                        <span>sur {Math.max(1, Math.ceil(total / limit))}</span>
                    </div>

                    <button type="button" class="px-3 py-1 bg-white border border-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50" onclick={() => { if (page < Math.max(1, Math.ceil(total / limit))) { page += 1; loadIngredients(); } }} disabled={page >= Math.max(1, Math.ceil(total / limit))}>Suiv</button>
                </div>
            </div>
        </div>

        {#if loadError}
            <div class="text-red-600">{loadError}</div>
        {:else}
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {#each ingredients as ing, i (ing.id)}
                    <button
                        type="button"
                        in:fly={{ y: 8, duration: 260, delay: computeDelay(i) }}
                        class="bg-white rounded shadow p-2 flex flex-col items-center gap-2 cursor-pointer transition-shadow duration-200 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-emerald-300 {selectedIngredient === ing.name ? 'ring-4 ring-emerald-400' : ''}"
                        onclick={() => openIngredient(ing.name)}
                    >
                        <img src={ing.image_url || '/favicon.svg'} alt={ing.name} class="w-20 h-20 object-cover rounded" />
                        <div class="text-sm text-center text-gray-800 font-medium">{capitalize(ing.name)}</div>
                        <div class="text-xs text-gray-500">{ing.recipeCount} {ing.recipeCount === 1 ? 'recette' : 'recettes'}</div>
                    </button>
                {/each}
            </div>
        {/if}

        <div class="relative">
            <IngredientsRecipesMenu
                show={showRecipesMenu}
                {selectedIngredient}
                {recipes}
                {recipesLoading}
                {recipesError}
                onSelectRecipe={(r) => {
                    selectedRecipe = r;
                    showRecipeModal = true;
                }}
                onClose={closeRecipesMenu}
            />

            <RecipeModal open={showRecipeModal} recipe={selectedRecipe} onclose={closeRecipe} />
        </div>
    </div>
</div>
