<script lang="ts">
    import { onMount } from 'svelte';
    import RecipeModal from '$lib/components/RecipeModal.svelte';
    import { Search } from '@lucide/svelte';

    let ingredients = [] as any[];
    let loadError: string | null = null;
let page = 1;
let total = 0;
let limit = 48;
let query: string = '';
let debouncedQuery: string = '';
let searchTimeout: any = null;

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

function getFirstImageForRecipeLocal(r: any): string {
    if (!r) return '';
    // try parsing images field
    if (r.images) {
        try {
            if (typeof r.images === 'string') {
                const parsed = JSON.parse(r.images);
                if (Array.isArray(parsed) && parsed.length) return parsed[0];
            } else if (Array.isArray(r.images) && r.images.length) return r.images[0];
        } catch {}
    }
    if (typeof r.image_url === 'string' && r.image_url.trim()) return r.image_url.trim();
    return '/favicon.svg';
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
                    <input placeholder="Rechercher..." class="outline-none w-full text-sm" value={query} on:input={onQueryInput} />
                    {#if query}
                        <button type="button" class="ml-2 text-sm text-gray-500" on:click={() => { query = ''; debouncedQuery = ''; page = 1; loadIngredients(); }}>Effacer</button>
                    {/if}
                </div>
            </div>

            <!-- removed letter buttons: search-only UI -->
        </div>

    {#if loadError}
        <div class="text-red-600">{loadError}</div>
    {:else}
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {#each ingredients as ing}
                <button
                    type="button"
                    class="bg-white rounded shadow p-2 flex flex-col items-center gap-2 cursor-pointer transition-shadow duration-200 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-emerald-300 {selectedIngredient === ing.name ? 'ring-4 ring-emerald-400' : ''}"
                    on:click={() => openIngredient(ing.name)}
                >
                    <img src={ing.image_url || '/favicon.svg'} alt={ing.name} class="w-20 h-20 object-cover rounded" />
                    <div class="text-sm text-center text-gray-800">{ing.name}</div>
                </button>
            {/each}
        </div>
        <div class="mt-6 flex items-center justify-center gap-2">
            <button class="px-3 py-1 bg-white border border-gray-200 rounded shadow-sm hover:bg-gray-50" on:click={() => { if (page > 1) { page -= 1; loadIngredients(); } }} disabled={page <= 1}>Préc</button>
            <div class="text-sm text-gray-700">Page {page} / {Math.max(1, Math.ceil(total / limit))}</div>
            <button class="px-3 py-1 bg-white border border-gray-200 rounded shadow-sm hover:bg-gray-50" on:click={() => { if (page < Math.max(1, Math.ceil(total / limit))) { page += 1; loadIngredients(); } }} disabled={page >= Math.max(1, Math.ceil(total / limit))}>Suiv</button>
        </div>
    {/if}

        <div class="relative">
            <div class="fixed inset-y-0 right-0 z-50 w-80 bg-white shadow-2xl p-4 overflow-auto transition-all duration-500 ease-in-out {showRecipesMenu ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}" aria-hidden={!showRecipesMenu}>
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-bold">Recettes: {selectedIngredient}</h3>
                    <button class="px-2 py-1 text-gray-600" on:click={closeRecipesMenu} aria-label="Fermer">✕</button>
                </div>

                {#if recipesLoading}
                    <div>Chargement...</div>
                {:else if recipesError}
                    <div class="text-red-600">{recipesError}</div>
                {:else if recipes.length === 0}
                    <div>Aucune recette trouvée.</div>
                {:else}
                    <ul class="space-y-2">
                        {#each recipes as r}
                            <li>
                                <button type="button" class="flex items-center gap-2 p-2 rounded hover:bg-gray-100 cursor-pointer w-full text-left" on:click={() => { selectedRecipe = r; showRecipeModal = true; }}>
                                    <img src={getFirstImageForRecipeLocal(r)} alt={r.name} class="w-12 h-12 object-cover rounded" />
                                    <div class="text-sm">{r.name}</div>
                                </button>
                            </li>
                        {/each}
                    </ul>
                {/if}
            </div>

            <RecipeModal open={showRecipeModal} recipe={selectedRecipe} on:close={closeRecipe} />
        </div>
    </div>
</div>


