<script lang="ts">
	import AddRecipeModal from '$lib/components/AddRecipeModal.svelte';
	import RecipeModal from '$lib/components/RecipeModal.svelte';
	import type {Recipe} from '$lib/db';
	import {ArrowDown, ArrowUp, ArrowUpDown, ChevronLeft, ChevronRight, Filter} from '@lucide/svelte';
	import {onMount} from 'svelte';
	import {writable} from 'svelte/store';

import { fly } from 'svelte/transition';
import { flip } from 'svelte/animate';

const appearDelayBase = 35;
function computeDelay(index: number) {
    return index * appearDelayBase;
}

const recipes = writable([] as Recipe[]);
const loading = writable(true);

	let currentPage = $state(1);
	let totalRecipes = $state(0);
	let totalPages = $state(0);
	const limit = 20;

	// Filtres
	let selectedDifficulties = $state<Set<string>>(new Set());
	let selectedBudgets = $state<Set<string>>(new Set());
	const difficulties = ['Facile', 'Moyen', 'Difficile'];
	const budgets = ['Bon marché', 'Coût moyen', 'Cher'];

	// Tri
	let sortBy = $state<string>('name');
	let sortOrder = $state<'asc' | 'desc'>('asc');

	const sortOptions = [
		{value: 'name', label: 'Nom'},
		{value: 'prep_time', label: 'Temps de préparation'},
		{value: 'cook_time', label: 'Temps de cuisson'},
		{value: 'total_time', label: 'Temps total'},
		{value: 'rate', label: 'Note'},
		{value: 'nb_comments', label: 'Commentaires'},
		{value: 'created_at', label: 'Date de création'}
	];

let loadTimeout: ReturnType<typeof setTimeout> | null = null;

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
	let selectedRecipe = $state<Recipe | null>(null);
	let addModalOpen = $state(false);

	function openRecipe(recipe: Recipe) {
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

	function prevPage() {
		if (currentPage > 1) {
			loadRecipes(currentPage - 1);
		}
	}

	function nextPage() {
		if (currentPage < totalPages) {
			loadRecipes(currentPage + 1);
		}
	}

	async function loadRecipes(page = 1) {
		loading.set(true);
		try {
			const difficultyParam = selectedDifficulties.size > 0 ? `&difficulty=${Array.from(selectedDifficulties).join(',')}` : '';
			const budgetParam = selectedBudgets.size > 0 ? `&budget=${Array.from(selectedBudgets).join(',')}` : '';
			const sortParam = `&sort=${sortBy}&order=${sortOrder}`;
			const res = await fetch(`/api/recipes?page=${page}&limit=${limit}${difficultyParam}${budgetParam}${sortParam}`);
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

	function debouncedLoadRecipes() {
		if (loadTimeout) clearTimeout(loadTimeout);
		loadTimeout = setTimeout(() => {
			loadRecipes();
		}, 300); // 300ms debounce
	}

	function toggleDifficulty(difficulty: string) {
		if (selectedDifficulties.has(difficulty)) {
			selectedDifficulties.delete(difficulty);
		} else {
			selectedDifficulties.add(difficulty);
		}
		selectedDifficulties = new Set(selectedDifficulties); // trigger reactivity
		currentPage = 1; // reset to first page
		debouncedLoadRecipes();
	}

	function toggleBudget(budget: string) {
		if (selectedBudgets.has(budget)) {
			selectedBudgets.delete(budget);
		} else {
			selectedBudgets.add(budget);
		}
		selectedBudgets = new Set(selectedBudgets); // trigger reactivity
		currentPage = 1; // reset to first page
		debouncedLoadRecipes();
	}

	function changeSort(newSortBy: string) {
		if (sortBy === newSortBy) {
			sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
		} else {
			sortBy = newSortBy;
			sortOrder = 'asc';
		}
		currentPage = 1; // reset to first page
		debouncedLoadRecipes();
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
				headers: {'Content-Type': 'application/json'},
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

	function parseListField(field: unknown): string[] {
		if (field == null) return [];
		if (typeof field === 'string') {
			try {
				const parsed = JSON.parse(field);
				if (Array.isArray(parsed)) return parsed;
			} catch {
			}
        // Accept JSON array, newline, comma or pipe-separated lists
        const parts = field.split(/[,|\n]+/).map(s => s.trim()).filter(Boolean);
        return parts;
		}
		if (Array.isArray(field)) return field;
		return [];
	}

	function formatImagesForDisplay(recipe: Recipe) {
		const imgs = parseListField(recipe.images || '');
		return imgs.length ? imgs[0] : '';
	}

	function formatDuration(duration: string): string {
		if (!duration) return '';
		const match = duration.match(/(\d+)m/);
		if (!match) return duration;
		const minutes = parseInt(match[1]);
		const hours = Math.floor(minutes / 60);
		const mins = minutes % 60;
		if (hours > 0) {
			return `${hours}h${mins}m`;
		} else {
			return `${mins}m`;
		}
	}

	onMount(loadRecipes);
</script>

<div class="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <header class="mb-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-extrabold text-gray-900 flex items-center gap-3">
                        <span class="inline-block w-2 h-8 bg-emerald-500 rounded"></span>
                        Recettes
                    </h1>
                    <p class="text-sm text-gray-600 mt-1">Parcourez et filtrez les recettes — cliquez sur une carte pour voir les détails.</p>
                </div>

                <div class="ml-4">
                    <button
                        class="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg font-bold shadow-sm"
                        onclick={openAddModal}
                    >Ajouter une recette</button>
                </div>
            </div>
        </header>

	<!-- Filters and Controls -->
	<div class="mb-8 space-y-6">
		<!-- Filters -->
		<div>
			<div class="flex items-center gap-2 mb-4">
				<Filter size={20} class="text-gray-600"/>
				<h2 class="text-xl font-semibold text-gray-800">Filtres</h2>
			</div>
			<div class="flex flex-wrap gap-2">
				{#each difficulties as diff}
					<button
						class="cursor-pointer px-3 py-1 rounded-full text-sm font-medium transition-all {selectedDifficulties.has(diff)
							? 'bg-orange-500 text-white shadow-md'
							: 'bg-white text-gray-700 border border-gray-300 hover:border-orange-400 hover:bg-orange-50'}"
						onclick={() => toggleDifficulty(diff)}
					>
						{diff}
					</button>
				{/each}
				{#each budgets as budg}
					<button
						class="cursor-pointer px-3 py-1 rounded-full text-sm font-medium transition-all {selectedBudgets.has(budg)
							? 'bg-orange-500 text-white shadow-md'
							: 'bg-white text-gray-700 border border-gray-300 hover:border-orange-400 hover:bg-orange-50'}"
						onclick={() => toggleBudget(budg)}
					>
						{budg}
					</button>
				{/each}
			</div>
		</div>

		<!-- Sort and Pagination Controls -->
		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
			<!-- Sort Controls -->
			<div class="flex items-center gap-4">
				<div class="flex items-center gap-2">
					<ArrowUpDown size={16} class="text-gray-600"/>
					<span class="text-sm font-medium text-gray-700">Trier par:</span>
				</div>
				<div class="flex gap-2">
					{#each sortOptions as option}
						<button
							class="cursor-pointer px-3 py-1 text-sm rounded-md transition-all flex items-center gap-1 {sortBy === option.value
								? 'bg-orange-500 text-white'
								: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
							onclick={() => changeSort(option.value)}
						>
							<span>{option.label}</span>
							{#if sortBy === option.value}
								{#if sortOrder === 'asc'}
									<ArrowUp size={14}/>
								{:else}
									<ArrowDown size={14}/>
								{/if}
							{/if}
						</button>
					{/each}
				</div>
			</div>
		</div>
	</div>


    {#if !$loading && totalPages > 1}
		<div class="flex items-center justify-center gap-4 bg-white/80 backdrop-blur-sm rounded-lg px-6 py-3 shadow-sm mt-6">
			<button
				onclick={prevPage} disabled={currentPage <= 1}
				class="cursor-pointer px-4 py-2 bg-gray-100 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 transition-colors"
			>
				<ChevronLeft size={16}/>
			</button>

                <div class="flex items-center gap-2">
                    <span class="text-sm font-medium">Page</span>
                    <input
                        type="number"
                        min="1"
                        max={Math.max(1, Math.ceil(totalRecipes / limit))}
                        value={currentPage}
                        onchange={(e: Event) => goToPage(parseInt((e.target as HTMLInputElement).value) || 1)}
                        class="w-16 px-2 py-1 text-center border border-gray-300 rounded text-sm"
                    />
                    <span class="text-sm">of {Math.max(1, Math.ceil(totalRecipes / limit))}</span>
                </div>

			<button
				onclick={nextPage} disabled={currentPage >= Math.max(1, Math.ceil(totalRecipes / limit))}
				class="cursor-pointer px-4 py-2 bg-gray-100 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 transition-colors"
			>
				<ChevronRight size={16}/>
			</button>

			<div class="text-sm text-gray-600 ml-4">
				{$recipes.length} recipes displayed out of {totalRecipes} total
			</div>
		</div>
	{/if}

        <div class="space-y-6">
        <section>
            {#if $loading}
                <p class="text-gray-500">Loading...</p>
            {:else}
                {#if $recipes.length === 0}
                    <p class="text-gray-500">No recipes.</p>
                {:else}
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mt-4">
                        {#each $recipes as recipe, i (recipe.id)}
                            <button
                                type="button"
                                animate:flip={{ duration: 300 }}
                                in:fly={{ y: 8, duration: 260, delay: i * 35 }}
                                class="bg-white rounded shadow p-2 flex flex-col items-center gap-2 cursor-pointer transition-shadow duration-200 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-emerald-300 text-left"
                                onclick={() => openRecipe(recipe)}
                            >
                                <img class="w-full h-40 object-cover rounded-lg bg-gray-100" src={formatImagesForDisplay(recipe) || '/favicon.svg'} alt={recipe.name} />
                                <div class="w-full">
                                    <div class="text-lg font-semibold text-gray-900">{recipe.name}</div>
                                    {#if recipe.description}
                                        <div class="text-gray-600 text-sm mt-1">{recipe.description}</div>
                                    {/if}
                                    <div class="flex gap-2 mt-2">
                                        {#if recipe.prep_time}<span class="bg-gray-100 px-2 py-1 rounded text-xs">Prep: {recipe.prep_time}</span>{/if}
                                        {#if recipe.cook_time}<span class="bg-gray-100 px-2 py-1 rounded text-xs">Cook: {recipe.cook_time}</span>{/if}
                                        {#if recipe.total_time}<span class="bg-gray-100 px-2 py-1 rounded text-xs">Total: {recipe.total_time}</span>{/if}
                                    </div>
                                </div>
                            </button>
                        {/each}
                    </div>
                {/if}
            {/if}
        </section>
    </div>
	<RecipeModal open={modalOpen} recipe={selectedRecipe} on:close={closeModal}/>
	<AddRecipeModal open={addModalOpen} on:close={closeAddModal} on:created={async (e) => { await loadRecipes(); closeAddModal(); }}/>
    </div>
</div>
