<script lang="ts">
    import { onMount } from 'svelte';
    import RecipeModal from '$lib/components/RecipeModal.svelte';

    let ingredients = [] as any[];
    let loadError: string | null = null;
let page = 1;
let total = 0;
let limit = 48;
let selectedLetter: string | null = null;
let query: string = '';
let debouncedQuery: string = '';
let searchTimeout: any = null;
const letters = Array.from({ length: 26 }, (_, i) => String.fromCharCode(97 + i));

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
            const letterParam = selectedLetter ? `&letter=${selectedLetter}` : '';
            const queryParam = debouncedQuery ? `&q=${encodeURIComponent(debouncedQuery)}` : '';
            const res = await fetch(`/api/ingredients?page=${page}&limit=${limit}${letterParam}${queryParam}`);
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
        // When searching, behave like "Tous" — clear any selected letter
        selectedLetter = null;
        page = 1;
        loadIngredients();
    }, 350);
}
</script>

<div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Ingrédients</h1>

    <div class="mb-4 flex gap-2 items-center">
        <input placeholder="Rechercher..." class="px-3 py-2 border rounded w-full max-w-sm" value={query} on:input={onQueryInput} />
        <button class="px-2 py-1 rounded bg-gray-100" on:click={() => { selectedLetter = null; page = 1; loadIngredients(); }}>Tous</button>
        {#each letters as l}
            <button class="px-2 py-1 rounded {selectedLetter === l ? 'bg-emerald-500 text-white' : 'bg-white'}" on:click={() => { selectedLetter = l; page = 1; loadIngredients(); }}>{l.toUpperCase()}</button>
        {/each}
    </div>

    {#if loadError}
        <div class="text-red-600">{loadError}</div>
    {:else}
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {#each ingredients as ing}
                <button type="button" class="bg-white rounded shadow p-2 flex flex-col items-center gap-2 cursor-pointer" on:click={() => openIngredient(ing.name)}>
                    <img src={ing.image_url || '/favicon.svg'} alt={ing.name} class="w-20 h-20 object-cover rounded" />
                    <div class="text-sm text-center">{ing.name}</div>
                </button>
            {/each}
        </div>
        <div class="mt-4 flex items-center justify-center gap-2">
            <button class="px-3 py-1 bg-gray-100 rounded" on:click={() => { if (page > 1) { page -= 1; loadIngredients(); } }} disabled={page <= 1}>Préc</button>
            <div>Page {page} / {Math.max(1, Math.ceil(total / limit))}</div>
            <button class="px-3 py-1 bg-gray-100 rounded" on:click={() => { if (page < Math.max(1, Math.ceil(total / limit))) { page += 1; loadIngredients(); } }} disabled={page >= Math.max(1, Math.ceil(total / limit))}>Suiv</button>
        </div>
    {/if}

    {#if showRecipesMenu}
        <div class="fixed inset-y-0 right-0 z-40 w-80 bg-white shadow-lg p-4 overflow-auto">
            <div class="flex items-center justify-between mb-3">
                <h3 class="font-bold">Recettes: {selectedIngredient}</h3>
                <button class="px-2 py-1" on:click={closeRecipesMenu} aria-label="Fermer">✕</button>
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
    {/if}
</div>


