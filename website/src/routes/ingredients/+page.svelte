<script lang="ts">
    import { onMount } from 'svelte';

    let ingredients = [] as any[];
    let loadError: string | null = null;
let page = 1;
let total = 0;
let limit = 48;
let selectedLetter: string | null = null;
const letters = Array.from({ length: 26 }, (_, i) => String.fromCharCode(97 + i));

    async function loadIngredients() {
        loadError = null;
        try {
            const letterParam = selectedLetter ? `&letter=${selectedLetter}` : '';
            const res = await fetch(`/api/ingredients?page=${page}&limit=${limit}${letterParam}`);
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
</script>

<div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Ingrédients</h1>

    <div class="mb-4 flex gap-2 items-center">
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
                <div class="bg-white rounded shadow p-2 flex flex-col items-center gap-2">
                    <img src={ing.image_url || '/favicon.svg'} alt={ing.name} class="w-20 h-20 object-cover rounded" />
                    <div class="text-sm text-center">{ing.name}</div>
                </div>
            {/each}
        </div>
        <div class="mt-4 flex items-center justify-center gap-2">
            <button class="px-3 py-1 bg-gray-100 rounded" on:click={() => { if (page > 1) { page -= 1; loadIngredients(); } }} disabled={page <= 1}>Préc</button>
            <div>Page {page} / {Math.max(1, Math.ceil(total / limit))}</div>
            <button class="px-3 py-1 bg-gray-100 rounded" on:click={() => { if (page < Math.max(1, Math.ceil(total / limit))) { page += 1; loadIngredients(); } }} disabled={page >= Math.max(1, Math.ceil(total / limit))}>Suiv</button>
        </div>
    {/if}
</div>


