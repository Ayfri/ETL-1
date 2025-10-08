<script lang="ts">
    import '../app.css';
    import favicon from '$lib/assets/icon.png';
    import Header from '$lib/components/Header.svelte';

    let { children } = $props();
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
	<title>Recipe Search</title>
</svelte:head>

<Header />

<main>
    {@render children?.()}
</main>
