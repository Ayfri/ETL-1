<script lang="ts">
	import type { Food } from '$lib/types';

	interface Props {
		food: Food;
		selected?: boolean;
		onclick?: () => void;
	}

	let { food, selected = false, onclick }: Props = $props();
</script>

<button
	class="group relative overflow-hidden rounded-xl shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1 w-full text-left {selected
		? 'ring-4 ring-emerald-500'
		: ''}"
	{onclick}
>
	<img src={food.image} alt={food.name} class="w-full h-64 object-cover" />

	<div
		class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-4"
	>
		<h3 class="text-white text-xl font-semibold">{food.name}</h3>
		<p class="text-white/90 text-sm">{food.type}</p>
	</div>

	{#if selected}
		<div
			class="absolute top-3 right-3 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center text-white font-bold shadow-lg"
		>
			✓
		</div>
	{/if}
</button>
