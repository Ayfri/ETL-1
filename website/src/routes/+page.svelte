<script lang="ts">
	import FoodCard from '$lib/components/FoodCard.svelte';
	import FoodDetails from '$lib/components/FoodDetails.svelte';
	import type { Food } from '$lib/types';

	let selectedFood = $state<Food | null>(null);

	const foods: Food[] = [
		{
			id: 1,
			name: 'Pomme',
			type: 'Fruit',
			image: 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=400&fit=crop',
			nutrition: {
				calories: 52,
				protein: 0.3,
				carbs: 14,
				fat: 0.2,
				fiber: 2.4
			},
			vitamins: ['Vitamine C', 'Vitamine K', 'Vitamine B6'],
			minerals: ['Potassium', 'Cuivre', 'Manganèse'],
			benefits: [
				'Riche en antioxydants',
				'Favorise la santé cardiaque',
				'Aide à la digestion',
				'Renforce le système immunitaire'
			],
			nutriScore: 'A'
		},
		{
			id: 2,
			name: 'Banane',
			type: 'Fruit',
			image: 'https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=400&h=400&fit=crop',
			nutrition: {
				calories: 89,
				protein: 1.1,
				carbs: 23,
				fat: 0.3,
				fiber: 2.6
			},
			vitamins: ['Vitamine B6', 'Vitamine C', 'Vitamine B9'],
			minerals: ['Potassium', 'Magnésium', 'Cuivre'],
			benefits: [
				'Excellente source d\'énergie',
				'Riche en potassium',
				'Améliore l\'humeur',
				'Soutient la santé digestive'
			],
			nutriScore: 'A'
		},
		{
			id: 3,
			name: 'Orange',
			type: 'Fruit',
			image: 'https://images.unsplash.com/photo-1547514701-42782101795e?w=400&h=400&fit=crop',
			nutrition: {
				calories: 47,
				protein: 0.9,
				carbs: 12,
				fat: 0.1,
				fiber: 2.4
			},
			vitamins: ['Vitamine C', 'Vitamine A', 'Thiamine'],
			minerals: ['Calcium', 'Potassium', 'Magnésium'],
			benefits: [
				'Renforce le système immunitaire',
				'Protège contre les maladies',
				'Améliore la santé de la peau',
				'Favorise l\'absorption du fer'
			],
			nutriScore: 'A'
		},
		{
			id: 4,
			name: 'Fraise',
			type: 'Fruit',
			image: 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400&h=400&fit=crop',
			nutrition: {
				calories: 32,
				protein: 0.7,
				carbs: 8,
				fat: 0.3,
				fiber: 2
			},
			vitamins: ['Vitamine C', 'Vitamine B9', 'Vitamine K'],
			minerals: ['Potassium', 'Manganèse', 'Magnésium'],
			benefits: [
				'Riche en antioxydants',
				'Favorise la santé cardiaque',
				'Régule la glycémie',
				'Anti-inflammatoire naturel'
			],
			nutriScore: 'A'
		},
		{
			id: 5,
			name: 'Mangue',
			type: 'Fruit',
			image: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=400&h=400&fit=crop',
			nutrition: {
				calories: 60,
				protein: 0.8,
				carbs: 15,
				fat: 0.4,
				fiber: 1.6
			},
			vitamins: ['Vitamine A', 'Vitamine C', 'Vitamine E'],
			minerals: ['Potassium', 'Cuivre', 'Magnésium'],
			benefits: [
				'Booste l\'immunité',
				'Améliore la santé des yeux',
				'Favorise la digestion',
				'Protège contre le cancer'
			],
			nutriScore: 'A'
		},
		{
			id: 6,
			name: 'Tomate',
			type: 'Légume',
			image: 'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400&h=400&fit=crop',
			nutrition: {
				calories: 18,
				protein: 0.9,
				carbs: 3.9,
				fat: 0.2,
				fiber: 1.2
			},
			vitamins: ['Vitamine C', 'Vitamine K', 'Vitamine B9'],
			minerals: ['Potassium', 'Manganèse', 'Phosphore'],
			benefits: [
				'Riche en lycopène',
				'Protège contre les maladies cardiaques',
				'Améliore la santé de la peau',
				'Soutient la santé des os'
			],
			nutriScore: 'A'
		},
		{
			id: 7,
			name: 'Brocoli',
			type: 'Légume',
			image: 'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400&h=400&fit=crop',
			nutrition: {
				calories: 34,
				protein: 2.8,
				carbs: 7,
				fat: 0.4,
				fiber: 2.6
			},
			vitamins: ['Vitamine C', 'Vitamine K', 'Vitamine B9'],
			minerals: ['Potassium', 'Fer', 'Calcium'],
			benefits: [
				'Puissant antioxydant',
				'Protège contre le cancer',
				'Renforce les os',
				'Améliore la santé digestive'
			],
			nutriScore: 'A'
		},
		{
			id: 8,
			name: 'Carotte',
			type: 'Légume',
			image: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400&h=400&fit=crop',
			nutrition: {
				calories: 41,
				protein: 0.9,
				carbs: 10,
				fat: 0.2,
				fiber: 2.8
			},
			vitamins: ['Vitamine A', 'Vitamine K', 'Vitamine B6'],
			minerals: ['Potassium', 'Calcium', 'Magnésium'],
			benefits: [
				'Excellente pour la vision',
				'Renforce le système immunitaire',
				'Favorise une peau saine',
				'Réduit le risque de maladies cardiaques'
			],
			nutriScore: 'A'
		}
	];

	function selectFood(food: Food) {
		selectedFood = food;
	}

	function closeDetails() {
		selectedFood = null;
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<header class="text-center mb-12">
			<h1 class="text-5xl font-bold text-gray-900 mb-3">Encyclopédie Nutritionnelle</h1>
			<p class="text-xl text-gray-600 mb-8">
				Explorez les aliments et importez des données Open Food Facts
			</p>

			<div class="flex flex-wrap justify-center gap-4">
				<button
					class="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-all shadow-sm hover:shadow-md"
				>
					<span class="text-2xl">📖</span>
					<span class="font-medium">Encyclopédie</span>
				</button>
				<button
					class="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-all shadow-sm hover:shadow-md"
				>
					<span class="text-2xl">📄</span>
					<span class="font-medium">Importer CSV</span>
				</button>
			</div>
		</header>

		<!-- Food Grid -->
		<div
			class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 {selectedFood
				? 'md:mr-96'
				: ''} transition-all duration-300"
		>
			{#each foods as food (food.id)}
				<FoodCard {food} selected={selectedFood?.id === food.id} onclick={() => selectFood(food)} />
			{/each}
		</div>
	</div>

	<!-- Details Panel -->
	<FoodDetails food={selectedFood} onclose={closeDetails} />
</div>
