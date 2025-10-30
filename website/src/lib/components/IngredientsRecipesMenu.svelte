<script lang="ts">
    import ScrollArea from './ScrollArea.svelte';

    export let show = false;
    export let selectedIngredient: string | null = null;
    export let recipes: any[] = [];
    export let recipesLoading = false;
    export let recipesError: string | null = null;
    export let onSelectRecipe: (recipe: any) => void = () => {};
    export let onClose: () => void = () => {};

    function getFirstImageForRecipe(r: any): string {
        if (!r) return '/favicon.svg';
        const imgsField = r.images;
        if (imgsField) {
            if (Array.isArray(imgsField) && imgsField.length) return String(imgsField[0]);

            if (typeof imgsField === 'string') {
                const s = imgsField.trim();
                if (!s) {
                    // continue to other fallbacks
                } else {
                    try {
                        const parsed = JSON.parse(s);
                        if (Array.isArray(parsed) && parsed.length) return String(parsed[0]);
                    } catch (e) {
                        const parts = s.split(/[,\n]+/).map((p) => p.trim()).filter(Boolean);
                        if (parts.length) return parts[0];
                    }
                }
            }
        }

        if (typeof r.image_url === 'string' && r.image_url.trim()) return r.image_url.trim();
        if (typeof r.image === 'string' && r.image.trim()) return r.image.trim();
        if (typeof r.image_small_url === 'string' && r.image_small_url.trim()) return r.image_small_url.trim();

        return '/favicon.svg';
    }

    function capitalize(str: string): string {
        if (!str) return str;
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }
</script>

<div
    class="fixed inset-y-0 right-0 z-50 w-80 bg-white shadow-2xl p-4 transition-all duration-500 ease-in-out {show
        ? 'translate-x-0 opacity-100'
        : 'translate-x-full opacity-0'}"
    aria-hidden={!show}
>
    <div class="flex items-center justify-between mb-3">
        <div>
            <h3 class="font-bold">{capitalize(selectedIngredient || '')}</h3>
            <p class="text-xs text-gray-500 mt-1">{recipes.length} {recipes.length === 1 ? 'recette' : 'recettes'}</p>
        </div>
        <button class="px-2 py-1 text-gray-600" {onClose} aria-label="Fermer">✕</button>
    </div>

    {#if recipesLoading}
        <div>Chargement...</div>
    {:else if recipesError}
        <div class="text-red-600">{recipesError}</div>
    {:else if recipes.length === 0}
        <div>Aucune recette trouvée.</div>
    {:else}
        <ScrollArea className="max-h-[calc(100vh-6rem)]" ariaLabel={`Recettes pour ${selectedIngredient}`}>
            <ul class="space-y-2 p-1">
                {#each recipes as r}
                    <li>
                        <button
                            type="button"
                            class="flex items-center gap-2 p-2 rounded hover:bg-gray-100 cursor-pointer w-full text-left"
                            onclick={() => onSelectRecipe(r)}
                        >
                            <img src={getFirstImageForRecipe(r)} alt={r.name} class="w-12 h-12 object-cover rounded" />
                            <div class="text-sm">{r.name}</div>
                        </button>
                    </li>
                {/each}
            </ul>
        </ScrollArea>
    {/if}
</div>
