<script lang="ts">
	import {X} from '@lucide/svelte';

	export let open: boolean = false;
	export let recipe: any = null;
	export let onclose: () => void;

	function close() {
		onclose();
	}

	function parseListField(field: any): string[] {
		if (!field) return [];
		if (typeof field === 'string') {
			try {
				const parsed = JSON.parse(field);
				if (Array.isArray(parsed)) return parsed;
			} catch {
			}
			// Accept JSON array, newline, comma or pipe-separated lists
			return field.split(/[,|\n]+/).map(s => s.trim()).filter(Boolean);
		}
		if (Array.isArray(field)) return field;
		return [];
	}

	function parseIngredients(recipe: any): any[] {
		if (recipe.ingredients_json) {
			try {
				return JSON.parse(recipe.ingredients_json);
			} catch {
			}
		}
		// Fallback to raw ingredients
		const raw = parseListField(recipe.ingredients || recipe.ingredients_raw);
		return raw.map(ing => ({quantity: '', unit: '', name: ing, raw: ing}));
	}

	function getFirstImageForRecipe(r: any): string {
		if (!r) return '';
		// try parsing images field (could be JSON string or array or newline list)
		const imgs = parseListField(r.images || r.image_url || '');
		if (imgs.length) return imgs[0];
		// fallback to image_url if present
		if (typeof r.image_url === 'string' && r.image_url.trim()) return r.image_url.trim();
		return '';
	}
</script>

{#if open && recipe}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/55 backdrop-blur-[3px]">
		<div class="z-60 w-full max-w-[1200px] max-h-[95vh] overflow-auto bg-gradient-to-b from-white to-orange-50 rounded-xl shadow-2xl p-6 transform-origin-center scale-100 transition-transform duration-220">
			<header class="flex items-center justify-between gap-4 p-2">
				<div class="flex items-center gap-2">
					<h3 class="text-xl font-semibold m-0">{recipe.name}</h3>
					{#if recipe.recipe_quantity}
						<span class="bg-gradient-to-r from-orange-200 to-red-200 px-2 py-1 rounded-full font-semibold text-gray-800 ml-2">{recipe.recipe_quantity}</span>{/if}
				</div>
				<button class="bg-transparent border-none p-1 cursor-pointer" on:click={close} aria-label="Fermer">
					<X/>
				</button>
			</header>

			<div class="p-2">
				{#if getFirstImageForRecipe(recipe)}
					<img
						src={getFirstImageForRecipe(recipe)}
						alt={recipe.name || 'Recette'}
						class="w-full h-[300px] md:h-[200px] object-cover rounded-lg mb-3"
					/>
				{/if}

				<section class="grid grid-cols-[1fr_320px] md:grid-cols-1 gap-4">
					<div class="flex flex-col gap-4">
						<div class="bg-gradient-to-b from-white to-orange-50 rounded-lg p-3 shadow-sm">
							<h4 class="text-lg font-medium m-0 mb-2">Ingrédients</h4>
							<ul class="m-0 pl-4">
								{#each parseIngredients(recipe) as ing}
									<li>{ing.quantity} {ing.unit} {ing.name}</li>
								{/each}
							</ul>
						</div>

						<div class="bg-gradient-to-b from-white to-orange-50 rounded-lg p-3 shadow-sm">
							<h4 class="text-lg font-medium m-0 mb-2">Préparation</h4>
							<ol class="m-0 pl-4">
								{#each parseListField(recipe.steps) as step}
									<li>{step}</li>
								{/each}
							</ol>
						</div>
					</div>

					<aside class="flex flex-col gap-4">
						<div class="bg-gradient-to-b from-white to-orange-50 rounded-lg p-3 shadow-sm">
							{#if recipe.prep_time}
								<div><strong>Préparation:</strong> {recipe.prep_time}</div>
							{/if}
							{#if recipe.cook_time}
								<div><strong>Cuisson:</strong> {recipe.cook_time}</div>
							{/if}
							{#if recipe.total_time}
								<div><strong>Temps total:</strong> {recipe.total_time}</div>
							{/if}
							{#if recipe.difficulty}
								<div><strong>Difficulté:</strong> {recipe.difficulty}</div>
							{/if}
							{#if recipe.budget}
								<div><strong>Budget:</strong> {recipe.budget}</div>
							{/if}
							{#if recipe.rate}
								<div><strong>Note:</strong> ★ {recipe.rate}</div>
							{/if}
						</div>

						{#if recipe.description}
							<div class="bg-gradient-to-b from-white to-orange-50 rounded-lg p-3 shadow-sm">
								<h5 class="text-base font-medium">Description</h5>
								<p class="m-0">{recipe.description}</p>
							</div>
						{/if}

						{#if recipe.url}
							<div class="bg-gradient-to-b from-white to-orange-50 rounded-lg p-3 shadow-sm">
								<a
									href={recipe.url}
									target="_blank"
									rel="noopener noreferrer"
									class="inline-block text-orange-600 font-bold"
								>Ouvrir la source</a>
							</div>
						{/if}
					</aside>
				</section>
			</div>
		</div>
	</div>
{/if}
