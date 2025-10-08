<script lang="ts">
    import '../app.css';
    import favicon from '$lib/assets/favicon.svg';
    
    let { children } = $props();
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

<nav style="padding:0.5rem 1rem; border-bottom:1px solid #eee; display:flex; gap:1rem; align-items:center;">
    <a href="/" style="text-decoration:none; font-weight:600;">Encyclopédie</a>
    <a href="/recipes" style="text-decoration:none;">Recettes</a>
</nav>

<main style="padding:1rem;">
    {@render children?.()}
</main>
