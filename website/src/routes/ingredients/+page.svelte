<script lang="ts">
    import { onMount } from 'svelte';

    let ingredients = [] as any[];
    let loadError: string | null = null;

    onMount(async () => {
        try {
            const res = await fetch('/api/ingredients');
            if (!res.ok) throw new Error('Failed to fetch');
            const json = await res.json();
            ingredients = json.data || [];
        } catch (e) {
            console.error(e);
            loadError = 'Erreur lors du chargement des ingrédients';
        }
    });
</script>

<div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Ingrédients</h1>

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
    {/if}
</div>


