<script lang="ts">
  import { onMount } from 'svelte';
  import { writable, get } from 'svelte/store';
  import RecipeModal from '$lib/components/RecipeModal.svelte';
  import AddRecipeModal from '$lib/components/AddRecipeModal.svelte';

  const recipes = writable([] as any[]);
  const loading = writable(true);

  // Form state matching v0.4
  let name = '';
  let author_tip = '';
  let budget = '';
  let cook_time = '';
  let difficulty = '';
  let images_input = ''; // newline-separated URLs
  let ingredients_input = '';
  let nb_comments = '';
  let prep_time = '';
  let rate = '';
  let recipe_quantity = '';
  let steps_input = '';
  let total_time = '';
  let url = '';
  let description = '';

  // Modal state
  let modalOpen = false;
  let selectedRecipe: any = null;
  // Add recipe modal
  let addModalOpen = false;

  function openRecipe(r: any) {
    selectedRecipe = r;
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

  async function loadRecipes() {
    loading.set(true);
    try {
      const res = await fetch('/api/recipes');
      const data = await res.json();
      recipes.set(data.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      loading.set(false);
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

  function formatImagesForDisplay(r: any) {
    const imgs = parseListField(r.images || r.image_url || '');
    return imgs.length ? imgs[0] : '';
  }

  async function submitRecipe() {
    const images = images_input.split('\n').map(s => s.trim()).filter(Boolean);
    const ingredients = ingredients_input.split('\n').map(s => s.trim()).filter(Boolean);
    const steps = steps_input.split('\n').map(s => s.trim()).filter(Boolean);

    const payload = {
      name,
      author_tip,
      budget,
      cook_time,
      difficulty,
      images: JSON.stringify(images),
      ingredients: JSON.stringify(ingredients),
      nb_comments,
      prep_time,
      rate,
      recipe_quantity,
      steps: JSON.stringify(steps),
      total_time,
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
        // reset form
        name = '';
        author_tip = '';
        budget = '';
        cook_time = '';
        difficulty = '';
        images_input = '';
        ingredients_input = '';
        nb_comments = '';
        prep_time = '';
        rate = '';
        recipe_quantity = '';
        steps_input = '';
        total_time = '';
        url = '';
        description = '';
        await loadRecipes();
      } else {
        const err = await res.json();
        alert(err.error || 'Erreur');
      }
    } catch (e) {
      console.error(e);
      alert('Erreur lors de la création');
    }
  }

  onMount(loadRecipes);
</script>

<style>
  .page { max-width: 980px; margin: 0 auto; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
  .grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
  .card { background: #fff; border: 1px solid #eee; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);} 
  h1 { margin-bottom: 0.5rem; }
  .recipe-img { width:100%; height:160px; object-fit:cover; border-radius:8px; background:#fafafa; }
  .badges { display:flex; gap:0.5rem; margin-top:0.5rem }
  .badge { background:#f5f5f5; padding:0.25rem 0.5rem; border-radius:4px; font-size:0.85rem }
  .title-row { display:flex; gap:1rem; align-items:center }
  /* Modern theme */
  .recipes-card { background: linear-gradient(180deg,#ffffff,#fffaf3); border: none; box-shadow: 0 8px 30px rgba(16,24,40,0.08); }
  .card-compact { display:flex; gap:1rem; align-items:center; padding:0.75rem; border-radius:12px; border:1px solid rgba(16,24,40,0.03); }
  .meta { display:flex; justify-content:space-between; width:100%; align-items:center }
  .meta-main .name { font-size:1.05rem; display:block }
  .meta-main .desc { color:#586069; font-size:0.92rem; margin-top:0.25rem }
  .view-btn { background: linear-gradient(90deg,#ff8a00,#ff3b81); color:white; border:none; padding:0.5rem 0.85rem; border-radius:10px; cursor:pointer; font-weight:700; transition:transform 180ms ease, box-shadow 180ms ease }
  .view-btn:hover { transform:translateY(-3px); box-shadow:0 8px 20px rgba(255,59,129,0.12) }
  .badge { background:linear-gradient(90deg,#f3f4f6,#fff); padding:0.28rem 0.5rem; border-radius:8px; font-size:0.82rem; color:#374151 }
  .recipes-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap:1rem; margin-top:0.5rem }
  .recipe-card { display:flex; flex-direction:column; gap:0.5rem; padding:0; }
  .page-header { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:0.75rem }
  .add-btn { background: linear-gradient(90deg,#06b6d4,#3b82f6); color:white; border:none; padding:0.5rem 0.9rem; border-radius:10px; cursor:pointer; font-weight:700 }
</style>

<div class="page">
  <div class="page-header">
    <h1>Recettes</h1>
    <button class="add-btn" on:click={openAddModal}>Ajouter une recette</button>
  </div>
  <div class="grid">
    <section>
      <div class="card recipes-card">
        <div class="title-row">
          <h2>Recettes enregistrées</h2>
        </div>

        {#if $loading}
          <p>Chargement...</p>
        {:else}
          {#if $recipes.length === 0}
            <p>Aucune recette.</p>
          {:else}
            <div class="recipes-grid">
            {#each $recipes as r}
              <article class="recipe-card card-compact">
                <img class="recipe-img" src={formatImagesForDisplay(r)} alt={r.name} />
                <div class="meta">
                  <div class="meta-main">
                    <strong class="name">{r.name}</strong>
                    <div class="desc">{r.description}</div>
                    <div class="badges">
                      {#if r.prep_time}<div class="badge">Prépa: {r.prep_time}</div>{/if}
                      {#if r.cook_time}<div class="badge">Cuisson: {r.cook_time}</div>{/if}
                      {#if r.total_time}<div class="badge">Total: {r.total_time}</div>{/if}
                    </div>
                  </div>

                  <div class="actions">
                    <button class="view-btn small" on:click={() => openRecipe(r)}>Voir</button>
                  </div>
                </div>
              </article>
            {/each}
            </div>
          {/if}
        {/if}
      </div>
    </section>
  </div>
  <RecipeModal open={modalOpen} recipe={selectedRecipe} on:close={closeModal} />
  <AddRecipeModal open={addModalOpen} on:close={closeAddModal} on:created={async (e) => { await loadRecipes(); closeAddModal(); }} />
</div>
