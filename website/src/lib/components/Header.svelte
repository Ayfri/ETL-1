<script lang="ts">
	import icon from '$lib/assets/icon.png';
	import { page } from '$app/state';

	const links = [
		{ href: '/', text: 'Accueil' },
		{ href: '/ingredients', text: 'Ingrédients' },
		{ href: '/recipes', text: 'Recettes' }
	];
</script>

<nav class="py-3 px-6 border-b border-gray-200 flex gap-6 items-center bg-white shadow-sm">
	<a href="/">
		<img src={icon} alt="Logo" class="h-10" />
	</a>
	{#each links as link}
		<a href={link.href} class="no-underline font-semibold text-black hover:text-gray-800 hover:bg-gray-100 transition-colors duration-200 px-2 py-1 rounded text-lg {page.url.pathname === link.href || (link.href !== '/' && page.url.pathname.startsWith(link.href)) ? 'text-green-600' : ''}">{link.text}</a>
	{/each}
</nav>
