<script lang="ts">
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';
	import RecipeModal from '$lib/components/RecipeModal.svelte';
	import AddRecipeModal from '$lib/components/AddRecipeModal.svelte';
	import { ChevronLeft, ChevronRight } from '@lucide/svelte';

	const recipes = writable([] as any[]);
	const loading = writable(true);

	let currentPage = $state(1);
	let totalRecipes = $state(0);
	let totalPages = $state(0);
	const limit = 20;

	let name = $state('');
	let authorTip = $state('');
	let budget = $state('');
	let cookTime = $state('');
	let difficulty = $state('');
	let imagesInput = $state('');
	let ingredientsInput = $state('');
	let nbComments = $state('');
	let prepTime = $state('');
	let rate = $state('');
	let recipeQuantity = $state('');
	let stepsInput = $state('');
	let totalTime = $state('');
	let url = $state('');
	let description = $state('');

	let modalOpen = $state(false);
	let selectedRecipe = $state<any>(null);
	let addModalOpen = $state(false);

	function openRecipe(recipe: any) {
		selectedRecipe = recipe;
		modalOpen = true;
	}

	function closeModal() {
		modalOpen = false;
		selectedRecipe = null;
	}

	function openAddModal() {
		addModalOpen = true;
	}

	function closeAddModal() {
		addModalOpen = false;
	}

	async function loadRecipes(page = 1) {
		loading.set(true);
		try {
			const res = await fetch(`/api/recipes?page=${page}&limit=${limit}`);
			const data = await res.json();
			recipes.set(data.data || []);
			totalRecipes = data.total || 0;
			totalPages = data.pages || 0;
			currentPage = page;
		} catch (e) {
			console.error(e);
		} finally {
			loading.set(false);
		}
	}

	function nextPage() {
		if (currentPage < totalPages) {
			loadRecipes(currentPage + 1);
		}
	}

	function prevPage() {
		if (currentPage > 1) {
			loadRecipes(currentPage - 1);
		}
	}

	function parseListField(field: any): string[] {
		if (!field) return [];
		if (typeof field === 'string') {
			try {
				const parsed = JSON.parse(field);
				if (Array.isArray(parsed)) return parsed;
			} catch {}
			return field.split('\n').map(s => s.trim()).filter(Boolean);
		}
		if (Array.isArray(field)) return field;
		return [];
	}

	function formatImagesForDisplay(recipe: any) {
		const imgs = parseListField(recipe.images || recipe.image_url || '');
		return imgs.length ? imgs[0] : '';
	}

	async function submitRecipe() {
		const images = imagesInput.split('\n').map(s => s.trim()).filter(Boolean);
		const ingredients = ingredientsInput.split('\n').map(s => s.trim()).filter(Boolean);
		const steps = stepsInput.split('\n').map(s => s.trim()).filter(Boolean);

		const payload = {
			name,
			author_tip: authorTip,
			budget,
			cook_time: cookTime,
			difficulty,
			images: JSON.stringify(images),
			ingredients: JSON.stringify(ingredients),
			nb_comments: nbComments,
			prep_time: prepTime,
			rate,
			recipe_quantity: recipeQuantity,
			steps: JSON.stringify(steps),
			total_time: totalTime,
			url,
			description
		};

		try {
			const res = await fetch('/api/recipes', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});

			if (res.ok) {
				name = '';
				authorTip = '';
				budget = '';
				cookTime = '';
				difficulty = '';
				imagesInput = '';
				ingredientsInput = '';
				nbComments = '';
				prepTime = '';
				rate = '';
				recipeQuantity = '';
				stepsInput = '';
				totalTime = '';
				url = '';
				description = '';
				await loadRecipes();
			} else {
				const err = await res.json();
				alert(err.error || 'Error');
			}
		} catch (e) {
			console.error(e);
			alert('Error creating recipe');
		}
	}

	function goToPage(newPage: number) {
		const maxPage = Math.max(1, Math.ceil(totalRecipes / limit));
		if (newPage >= 1 && newPage <= maxPage) {
			loadRecipes(newPage);
		}
	}

	onMount(loadRecipes);
</script>

<div class="max-w-4xl mx-auto font-sans p-4">
	<div class="flex items-center justify-between mb-6">
		<h1 class="text-2xl font-bold">Recipes</h1>
		<button class="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-4 py-2 rounded-lg font-bold hover:opacity-90" onclick={openAddModal}>Add Recipe</button>
	</div>


    {#if totalPages > 1}
        <div class="flex items-center justify-center gap-4 bg-white/80 backdrop-blur-sm rounded-lg px-6 py-3 shadow-sm mt-6">
            <button onclick={prevPage} disabled={currentPage <= 1}
                    class="cursor-pointer px-4 py-2 bg-gray-100 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 transition-colors">
                <ChevronLeft size={16}/>
            </button>

            <div class="flex items-center gap-2">
                <span class="text-sm font-medium">Page</span>
                <input
                        type="number"
                        min="1"
                        max={Math.max(1, Math.ceil(totalRecipes / limit))}
                        value={currentPage}
                        onchange={(e) => goToPage(parseInt(e.target.value) || 1)}
                        class="w-16 px-2 py-1 text-center border border-gray-300 rounded text-sm"
                />
                <span class="text-sm">of {Math.max(1, Math.ceil(totalRecipes / limit))}</span>
            </div>

            <button onclick={nextPage} disabled={currentPage >= Math.max(1, Math.ceil(totalRecipes / limit))}
                    class="cursor-pointer px-4 py-2 bg-gray-100 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 transition-colors">
                <ChevronRight size={16}/>
            </button>
        </div>
    {/if}

	<div class="space-y-6">
		<section>
			<div class="bg-gradient-to-br from-white to-orange-50 p-6 rounded-xl shadow-lg">
				<div class="flex items-center gap-4 mb-4">
					<h2 class="text-xl font-semibold">Saved Recipes</h2>
				</div>

				{#if $loading}
					<p class="text-gray-500">Loading...</p>
				{:else}
					{#if $recipes.length === 0}
						<p class="text-gray-500">No recipes.</p>
					{:else}
						<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mt-4">
							{#each $recipes as recipe}
								<article class="flex flex-col gap-2 p-3 rounded-xl border border-gray-100 hover:shadow-md transition-shadow">
									<button class="w-full text-left p-0 hover:transform hover:-translate-y-1 transition-transform" onclick={() => openRecipe(recipe)} aria-label={`Open ${recipe.name}`}>
										<img class="w-full h-40 object-cover rounded-lg bg-gray-100" src={formatImagesForDisplay(recipe)} alt={recipe.name} />
										<div class="flex justify-between items-center w-full mt-2">
											<div class="flex-1">
												<strong class="text-lg block">{recipe.name}</strong>
												<div class="text-gray-600 text-sm mt-1">{recipe.description}</div>
												<div class="flex gap-2 mt-2">
													{#if recipe.prep_time}<span class="bg-gray-100 px-2 py-1 rounded text-xs">Prep: {recipe.prep_time}</span>{/if}
													{#if recipe.cook_time}<span class="bg-gray-100 px-2 py-1 rounded text-xs">Cook: {recipe.cook_time}</span>{/if}
													{#if recipe.total_time}<span class="bg-gray-100 px-2 py-1 rounded text-xs">Total: {recipe.total_time}</span>{/if}
												</div>
											</div>
										</div>
									</button>
								</article>
							{/each}
						</div>

						<div class="text-sm text-gray-600 mt-4">
							{$recipes.length} recipes displayed out of {totalRecipes} total
						</div>
					{/if}
				{/if}
			</div>
		</section>
	</div>
	<RecipeModal open={modalOpen} recipe={selectedRecipe} on:close={closeModal} />
	<AddRecipeModal open={addModalOpen} on:close={closeAddModal} on:created={async (e) => { await loadRecipes(); closeAddModal(); }} />
</div>
