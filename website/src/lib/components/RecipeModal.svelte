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
	<!-- Backdrop -->
	<button 
		onclick={close}
		class="fixed inset-0 z-[60] bg-black/60 backdrop-blur-sm cursor-pointer"
		aria-label="Fermer"
	></button>

	<!-- Modal full-screen -->
	<div class="fixed inset-0 z-[60] flex items-center justify-center p-4 pointer-events-none">
		<div class="w-full h-full max-w-5xl max-h-[calc(100vh-2rem)] bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col pointer-events-auto">
			<!-- Header -->
			<header class="sticky top-0 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-4 flex items-center justify-between gap-4 shadow-md z-10">
				<div class="flex items-center gap-3 flex-1 min-w-0">
					<h3 class="text-2xl font-bold m-0 truncate">{recipe.name}</h3>
					{#if recipe.recipe_quantity}
						<span class="bg-white/20 backdrop-blur px-3 py-1.5 rounded-full font-semibold text-white text-sm whitespace-nowrap">{recipe.recipe_quantity}</span>
					{/if}
				</div>
				<button 
					class="bg-white/20 hover:bg-white/30 border-none p-2 rounded-lg cursor-pointer transition-colors flex-shrink-0" 
					onclick={close} 
					aria-label="Fermer"
				>
					<X size={24}/>
				</button>
			</header>

			<!-- Content scrollable -->
			<div class="flex-1 overflow-y-auto bg-gradient-to-b from-white to-green-50/30">
				<div class="max-w-6xl mx-auto p-6">
					{#if getFirstImageForRecipe(recipe)}
						<img
							src={getFirstImageForRecipe(recipe)}
							alt={recipe.name || 'Recette'}
							class="w-full h-[400px] object-cover rounded-xl mb-6 shadow-lg"
						/>
					{/if}

					<section class="grid grid-cols-[2fr_1fr] lg:grid-cols-1 gap-6">
						<!-- Left column: Ingredients & Steps -->
						<div class="flex flex-col gap-6">
							<div class="bg-white rounded-xl p-6 shadow-md border border-green-100">
								<h4 class="text-2xl font-semibold m-0 mb-4 text-green-600 flex items-center gap-2">
									<span>🥘</span> Ingrédients
								</h4>
								<ul class="m-0 pl-6 space-y-2">
									{#each parseIngredients(recipe) as ing}
										<li class="text-gray-700 text-lg">
											{#if ing.quantity || ing.unit}
												<span class="font-semibold text-green-600">{ing.quantity} {ing.unit}</span>
											{/if}
											{ing.name}
										</li>
									{/each}
								</ul>
							</div>

							<div class="bg-white rounded-xl p-6 shadow-md border border-green-100">
								<h4 class="text-2xl font-semibold m-0 mb-4 text-green-600 flex items-center gap-2">
									<span>👨‍🍳</span> Préparation
								</h4>
								<ol class="m-0 pl-6 space-y-3">
									{#each parseListField(recipe.steps) as step, index}
										<li class="text-gray-700 text-lg leading-relaxed">
											<span class="font-semibold text-green-600">Étape {index + 1}:</span> {step}
										</li>
									{/each}
								</ol>
							</div>
						</div>

						<!-- Right column: Info & Metadata -->
						<aside class="flex flex-col gap-6">
							<div class="bg-white rounded-xl p-6 shadow-md border border-green-100">
								<h4 class="text-xl font-semibold m-0 mb-4 text-green-600">📊 Informations</h4>
								<div class="space-y-3">
									{#if recipe.prep_time}
										<div class="flex items-center gap-2">
											<span class="text-2xl">⏱️</span>
											<div>
												<div class="text-sm text-gray-500">Préparation</div>
												<div class="font-semibold text-gray-800">{recipe.prep_time}</div>
											</div>
										</div>
									{/if}
									{#if recipe.cook_time}
										<div class="flex items-center gap-2">
											<span class="text-2xl">🔥</span>
											<div>
												<div class="text-sm text-gray-500">Cuisson</div>
												<div class="font-semibold text-gray-800">{recipe.cook_time}</div>
											</div>
										</div>
									{/if}
									{#if recipe.total_time}
										<div class="flex items-center gap-2">
											<span class="text-2xl">⌛</span>
											<div>
												<div class="text-sm text-gray-500">Temps total</div>
												<div class="font-semibold text-gray-800">{recipe.total_time}</div>
											</div>
										</div>
									{/if}
									{#if recipe.difficulty}
										<div class="flex items-center gap-2">
											<span class="text-2xl">📈</span>
											<div>
												<div class="text-sm text-gray-500">Difficulté</div>
												<div class="font-semibold text-gray-800">{recipe.difficulty}</div>
											</div>
										</div>
									{/if}
									{#if recipe.budget}
										<div class="flex items-center gap-2">
											<span class="text-2xl">💰</span>
											<div>
												<div class="text-sm text-gray-500">Budget</div>
												<div class="font-semibold text-gray-800">{recipe.budget}</div>
											</div>
										</div>
									{/if}
									{#if recipe.rate}
										<div class="flex items-center gap-2">
											<span class="text-2xl">⭐</span>
											<div>
												<div class="text-sm text-gray-500">Note</div>
												<div class="font-semibold text-gray-800">{recipe.rate}/5</div>
											</div>
										</div>
									{/if}
								</div>
							</div>

							{#if recipe.description}
								<div class="bg-white rounded-xl p-6 shadow-md border border-green-100">
									<h5 class="text-xl font-semibold mb-3 text-green-600">📝 Description</h5>
									<p class="m-0 text-gray-700 leading-relaxed">{recipe.description}</p>
								</div>
							{/if}

							{#if recipe.url}
								<div class="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-4 shadow-md">
									<a
										href={recipe.url}
										target="_blank"
										rel="noopener noreferrer"
										class="flex items-center justify-center gap-2 text-white font-semibold text-base hover:text-white/90 transition-colors"
									>
										<span>🔗</span> Voir la recette originale
									</a>
								</div>
							{/if}
						</aside>
					</section>
				</div>
			</div>
		</div>
	</div>
{/if}
