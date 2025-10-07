<script lang="ts">
	import type { Food } from '$lib/types';

	interface Props {
		food: Food | null;
		onclose?: () => void;
	}

	let { food, onclose }: Props = $props();
</script>

{#if food}
	<div class="fixed inset-y-0 right-0 w-full md:w-96 bg-white shadow-2xl z-50 overflow-y-auto">
		<div class="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
			<h2 class="text-2xl font-bold text-gray-900">Détails</h2>
			<button
				onclick={onclose}
				class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
				aria-label="Fermer"
			>
				<svg
					class="w-6 h-6"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					></path>
				</svg>
			</button>
		</div>

		<div class="p-6">
			<img src={food.image} alt={food.name} class="w-full h-64 object-cover rounded-lg mb-6" />

			<h3 class="text-3xl font-bold text-gray-900 mb-2">{food.name}</h3>
			<p class="text-lg text-emerald-600 font-medium mb-6">{food.type}</p>

			<!-- Informations nutritionnelles -->
			<div class="space-y-6">
				<section>
					<h4 class="text-lg font-semibold text-gray-900 mb-3">Informations Nutritionnelles</h4>
					<div class="bg-gray-50 rounded-lg p-4 space-y-3">
						<div class="flex justify-between items-center">
							<span class="text-gray-700">Calories</span>
							<span class="font-semibold text-gray-900">{food.nutrition.calories} kcal</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-gray-700">Protéines</span>
							<span class="font-semibold text-gray-900">{food.nutrition.protein}g</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-gray-700">Glucides</span>
							<span class="font-semibold text-gray-900">{food.nutrition.carbs}g</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-gray-700">Lipides</span>
							<span class="font-semibold text-gray-900">{food.nutrition.fat}g</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-gray-700">Fibres</span>
							<span class="font-semibold text-gray-900">{food.nutrition.fiber}g</span>
						</div>
					</div>
				</section>

				<!-- Vitamines -->
				<section>
					<h4 class="text-lg font-semibold text-gray-900 mb-3">Vitamines</h4>
					<div class="flex flex-wrap gap-2">
						{#each food.vitamins as vitamin}
							<span
								class="px-3 py-1 bg-amber-100 text-amber-800 rounded-full text-sm font-medium"
							>
								{vitamin}
							</span>
						{/each}
					</div>
				</section>

				<!-- Minéraux -->
				<section>
					<h4 class="text-lg font-semibold text-gray-900 mb-3">Minéraux</h4>
					<div class="flex flex-wrap gap-2">
						{#each food.minerals as mineral}
							<span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
								{mineral}
							</span>
						{/each}
					</div>
				</section>

				<!-- Bienfaits -->
				<section>
					<h4 class="text-lg font-semibold text-gray-900 mb-3">Bienfaits pour la santé</h4>
					<ul class="space-y-2">
						{#each food.benefits as benefit}
							<li class="flex items-start">
								<svg
									class="w-5 h-5 text-emerald-500 mt-0.5 mr-2 flex-shrink-0"
									fill="currentColor"
									viewBox="0 0 20 20"
								>
									<path
										fill-rule="evenodd"
										d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
										clip-rule="evenodd"
									></path>
								</svg>
								<span class="text-gray-700">{benefit}</span>
							</li>
						{/each}
					</ul>
				</section>

				<!-- Score nutri -->
				<section>
					<h4 class="text-lg font-semibold text-gray-900 mb-3">Nutri-Score</h4>
					<div class="flex items-center gap-2">
						<div
							class="w-12 h-12 rounded-lg flex items-center justify-center text-2xl font-bold text-white {food.nutriScore ===
							'A'
								? 'bg-green-600'
								: food.nutriScore === 'B'
									? 'bg-lime-500'
									: food.nutriScore === 'C'
										? 'bg-yellow-500'
										: food.nutriScore === 'D'
											? 'bg-orange-500'
											: 'bg-red-600'}"
						>
							{food.nutriScore}
						</div>
						<span class="text-gray-600">Excellente qualité nutritionnelle</span>
					</div>
				</section>
			</div>
		</div>
	</div>

	<!-- Backdrop pour mobile -->
	<button
		onclick={onclose}
		class="fixed inset-0 bg-black/50 z-40 md:hidden"
		aria-label="Fermer le panneau"
	></button>
{/if}
