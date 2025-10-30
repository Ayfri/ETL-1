<script lang="ts">
	import { X, ExternalLink, ChefHat } from '@lucide/svelte';
	import type { FoodProduct } from '$lib/db';

	export interface Recipe {
		id: number;
		name: string;
		url: string;
		rate?: string;
		difficulty?: string;
		budget?: string;
		prep_time?: string;
		cook_time?: string;
		images?: string;
	}

	interface MatchedIngredient {
		ingredient_id: number;
		ingredient_name: string;
		match_score: number;
		match_method: string;
	}

	interface Props {
		product: FoodProduct | null;
		onclose?: () => void;
		onOpenRecipe?: (recipe: Recipe) => void;
	}

	let { product, onclose, onOpenRecipe }: Props = $props();
	let recipes: Recipe[] = $state([]);
	let matchedIngredients: MatchedIngredient[] = $state([]);
	let loading = $state(false);
	let error = $state('');

	async function loadRecipes() {
		if (!product?.code) return;

		loading = true;
		error = '';

		try {
			const response = await fetch(`/api/foods/${product.code}/recipes`);
			if (!response.ok) {
				throw new Error('Failed to load recipes');
			}

			const data = await response.json();
			recipes = data.recipes || [];
			matchedIngredients = data.matchedIngredients || [];
		} catch (err) {
			console.error('Error loading recipes:', err);
			error = 'Erreur lors du chargement des recettes';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		if (product) {
			loadRecipes();
		}
	});

	function getNutriScoreColor(grade?: string): string {
		switch (grade?.toLowerCase()) {
			case 'a':
				return 'bg-green-600';
			case 'b':
				return 'bg-lime-500';
			case 'c':
				return 'bg-yellow-500';
			case 'd':
				return 'bg-orange-500';
			case 'e':
				return 'bg-red-600';
			default:
				return 'bg-gray-400';
		}
	}

	function getImageUrl(imagesJson?: string): string | null {
		if (!imagesJson) return null;
		try {
			const images = JSON.parse(imagesJson);
			return images[0] || null;
		} catch {
			return null;
		}
	}
</script>

{#if product}
	<div class="h-full bg-white overflow-y-auto">
		<div
			class="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center"
		>
			<h2 class="text-2xl font-bold text-gray-900">Détails du produit</h2>
			<button
				onclick={onclose}
				class="p-2 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer"
				aria-label="Fermer"
			>
				<X size={20} />
			</button>
		</div>

		<div class="p-6 space-y-6">
			<!-- Product header -->
			<div class="flex gap-4">
				{#if product.image_url}
					<img
						src={product.image_url}
						alt={product.product_name}
						class="w-32 h-32 object-contain rounded-lg bg-gray-50"
					/>
				{/if}
				<div class="flex-1">
					<h3 class="text-2xl font-bold text-gray-900 mb-2">{product.product_name}</h3>
					{#if product.brands}
						<p class="text-lg text-gray-600 mb-2">{product.brands}</p>
					{/if}
					{#if product.main_category_en}
						<p class="text-sm text-emerald-600">{product.main_category_en}</p>
					{/if}
				</div>
			</div>

			<!-- Nutri-Score & Nova -->
			<div class="flex gap-4">
				{#if product.nutriscore_grade}
					<div>
						<p class="text-sm text-gray-600 mb-1">Nutri-Score</p>
						<div
							class="w-12 h-12 rounded-lg flex items-center justify-center text-2xl font-bold text-white {getNutriScoreColor(product.nutriscore_grade)}"
						>
							{product.nutriscore_grade.toUpperCase()}
						</div>
					</div>
				{/if}
				{#if product.nova_group}
					<div>
						<p class="text-sm text-gray-600 mb-1">NOVA</p>
						<div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center text-2xl font-bold text-blue-800">
							{product.nova_group}
						</div>
					</div>
				{/if}
			</div>

			<!-- Nutrition -->
			{#if product.energy_kcal_100g || product.proteins_100g || product.carbohydrates_100g || product.fat_100g}
				<section>
					<h4 class="text-lg font-semibold text-gray-900 mb-3">Valeurs nutritionnelles (pour 100g)</h4>
					<div class="bg-gray-50 rounded-lg p-4 space-y-2">
						{#if product.energy_kcal_100g}
							<div class="flex justify-between">
								<span class="text-gray-700">Énergie</span>
								<span class="font-semibold">{product.energy_kcal_100g.toFixed(0)} kcal</span>
							</div>
						{/if}
						{#if product.proteins_100g}
							<div class="flex justify-between">
								<span class="text-gray-700">Protéines</span>
								<span class="font-semibold">{product.proteins_100g.toFixed(1)}g</span>
							</div>
						{/if}
						{#if product.carbohydrates_100g}
							<div class="flex justify-between">
								<span class="text-gray-700">Glucides</span>
								<span class="font-semibold">{product.carbohydrates_100g.toFixed(1)}g</span>
							</div>
							{#if product.sugars_100g}
								<div class="flex justify-between pl-4">
									<span class="text-gray-600 text-sm">dont sucres</span>
									<span class="text-sm">{product.sugars_100g.toFixed(1)}g</span>
								</div>
							{/if}
						{/if}
						{#if product.fat_100g}
							<div class="flex justify-between">
								<span class="text-gray-700">Lipides</span>
								<span class="font-semibold">{product.fat_100g.toFixed(1)}g</span>
							</div>
							{#if product.saturated_fat_100g}
								<div class="flex justify-between pl-4">
									<span class="text-gray-600 text-sm">dont saturés</span>
									<span class="text-sm">{product.saturated_fat_100g.toFixed(1)}g</span>
								</div>
							{/if}
						{/if}
						{#if product.fiber_100g}
							<div class="flex justify-between">
								<span class="text-gray-700">Fibres</span>
								<span class="font-semibold">{product.fiber_100g.toFixed(1)}g</span>
							</div>
						{/if}
						{#if product.salt_100g}
							<div class="flex justify-between">
								<span class="text-gray-700">Sel</span>
								<span class="font-semibold">{product.salt_100g.toFixed(2)}g</span>
							</div>
						{/if}
					</div>
				</section>
			{/if}

			<!-- Matched Ingredients -->
			{#if matchedIngredients.length > 0}
				<section>
					<h4 class="text-lg font-semibold text-gray-900 mb-3">
						Ingrédients correspondants ({matchedIngredients.length})
					</h4>
					<div class="flex flex-wrap gap-2">
						{#each matchedIngredients as ingredient}
							<span
								class="px-3 py-1 rounded-full text-sm font-medium {ingredient.match_method === 'exact' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}"
								title="Score: {ingredient.match_score.toFixed(2)}"
							>
								{ingredient.ingredient_name}
							</span>
						{/each}
					</div>
				</section>
			{/if}

			<!-- Recipes -->
			<section>
				<h4 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
					<ChefHat size={20} />
					Recettes utilisant ce produit
				</h4>

				{#if loading}
					<div class="text-center py-8 text-gray-500">Chargement des recettes...</div>
				{:else if error}
					<div class="text-center py-8 text-red-500">{error}</div>
				{:else if recipes.length === 0}
					<div class="text-center py-8 text-gray-500">
						Aucune recette trouvée pour ce produit
					</div>
				{:else}
					<div class="space-y-3">
						{#each recipes as recipe}
							<button
								onclick={() => onOpenRecipe?.(recipe)}
								class="block w-full p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer text-left"
							>
								<div class="flex gap-3">
									{#if recipe.images}
										{@const imageUrl = getImageUrl(recipe.images)}
										{#if imageUrl}
											<img
												src={imageUrl}
												alt={recipe.name}
												class="w-16 h-16 object-cover rounded"
											/>
										{/if}
									{/if}
									<div class="flex-1 min-w-0">
										<h5 class="font-semibold text-gray-900 truncate">{recipe.name}</h5>
										<div class="flex gap-3 mt-1 text-sm text-gray-600">
											{#if recipe.rate}
												<span>⭐ {recipe.rate}</span>
											{/if}
											{#if recipe.difficulty}
												<span>• {recipe.difficulty}</span>
											{/if}
											{#if recipe.prep_time}
												<span>• ⏱️ {recipe.prep_time}</span>
											{/if}
										</div>
									</div>
									<ChefHat size={16} class="text-gray-400 flex-shrink-0 mt-1" />
								</div>
							</button>
						{/each}
					</div>
				{/if}
			</section>

			<!-- Ingredients text -->
			{#if product.ingredients_text}
				<section>
					<h4 class="text-lg font-semibold text-gray-900 mb-3">Liste des ingrédients</h4>
					<p class="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">{product.ingredients_text}</p>
				</section>
			{/if}

			<!-- Allergens -->
			{#if product.allergens}
				<section>
					<h4 class="text-lg font-semibold text-gray-900 mb-3">Allergènes</h4>
					<p class="text-sm text-gray-700 bg-red-50 p-3 rounded-lg">{product.allergens}</p>
				</section>
			{/if}
		</div>
	</div>

	<!-- Backdrop pour mobile -->
	<button
		onclick={onclose}
		class="fixed inset-0 bg-black/50 z-40 md:hidden cursor-pointer"
		aria-label="Fermer le panneau"
	></button>
{/if}
