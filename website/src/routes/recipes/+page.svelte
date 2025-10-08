<script lang="ts">
  import { onMount } from 'svelte';
  import { writable, get } from 'svelte/store';

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
  .grid { display: grid; grid-template-columns: 360px 1fr; gap: 1.5rem; }
  .card { background: #fff; border: 1px solid #eee; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);} 
  h1 { margin-bottom: 0.5rem; }
  .recipe-preview { display:flex; gap:1rem; align-items:center; padding:0.75rem 0; border-bottom:1px solid #f0f0f0 }
  .recipe-img { width:96px; height:96px; object-fit:cover; border-radius:6px; background:#fafafa; }
  .badges { display:flex; gap:0.5rem; margin-top:0.5rem }
  .badge { background:#f5f5f5; padding:0.25rem 0.5rem; border-radius:4px; font-size:0.85rem }
  label { display:block; margin-top:0.5rem; font-weight:600; font-size:0.9rem }
  input, textarea { width:100%; padding:0.5rem; margin-top:0.25rem; border:1px solid #ddd; border-radius:6px }
  button { margin-top:0.75rem; background:#ff6b00; color:white; border:none; padding:0.6rem 1rem; border-radius:6px; cursor:pointer }
  .title-row { display:flex; gap:1rem; align-items:center }
</style>

<div class="page">
  <h1>Recettes</h1>
  <div class="grid">
    <aside>
      <div class="card">
        <h2>Ajouter une recette</h2>
        <label>Nom
          <input bind:value={name} />
        </label>
        <label>Auteur (tip)
          <input bind:value={author_tip} />
        </label>
        <label>Description
          <textarea bind:value={description} rows={3} />
        </label>
        <label>Images (une URL par ligne)
          <textarea bind:value={images_input} rows={3} placeholder="https://..." />
        </label>
        <label>Ingrédients (une ligne par ingrédient)
          <textarea bind:value={ingredients_input} rows={4} />
        </label>
        <label>Étapes (une ligne par étape)
          <textarea bind:value={steps_input} rows={6} />
        </label>
        <label>Temps préparation
          <input bind:value={prep_time} placeholder="ex: 20 min" />
        </label>
        <label>Temps cuisson
          <input bind:value={cook_time} placeholder="ex: 30 min" />
        </label>
        <label>Temps total
          <input bind:value={total_time} placeholder="ex: 50 min" />
        </label>
        <label>Difficulté
          <input bind:value={difficulty} placeholder="facile / moyen / difficile" />
        </label>
        <label>Budget
          <input bind:value={budget} placeholder="bon marché / moyen / cher" />
        </label>
        <label>Quantité (recipe_quantity)
          <input bind:value={recipe_quantity} placeholder="ex: 4 personnes / 500 g" />
        </label>
        <label>Note (rate)
          <input bind:value={rate} placeholder="ex: 4.2" />
        </label>
        <label>Nombre de commentaires
          <input bind:value={nb_comments} placeholder="ex: 12" />
        </label>
        <label>URL source
          <input bind:value={url} placeholder="https://..." />
        </label>
        <button on:click={submitRecipe}>Créer</button>
      </div>
    </aside>

    <section>
      <div class="card">
        <div class="title-row">
          <h2>Recettes enregistrées</h2>
        </div>

        {#if $loading}
          <p>Chargement...</p>
        {:else}
          {#if $recipes.length === 0}
            <p>Aucune recette.</p>
          {:else}
            {#each $recipes as r}
              <article class="recipe-preview">
                <img class="recipe-img" src={formatImagesForDisplay(r)} alt={r.name} />
                <div>
                  <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem">
                    <div>
                      <strong style="font-size:1.05rem">{r.name}</strong>
                      <div style="color:#666; font-size:0.9rem">{r.description}</div>
                      <div class="badges">
                        {#if r.prep_time}<div class="badge">Préparation: {r.prep_time}</div>{/if}
                        {#if r.cook_time}<div class="badge">Cuisson: {r.cook_time}</div>{/if}
                        {#if r.total_time}<div class="badge">Total: {r.total_time}</div>{/if}
                        {#if r.difficulty}<div class="badge">{r.difficulty}</div>{/if}
                        {#if r.budget}<div class="badge">{r.budget}</div>{/if}
                        {#if r.rate}<div class="badge">⭐ {r.rate}</div>{/if}
                      </div>
                    </div>
                  </div>

                  <details style="margin-top:0.5rem">
                    <summary style="cursor:pointer">Voir la recette</summary>
                    <div style="margin-top:0.5rem">
                      <h4>Ingrédients</h4>
                      <ul>
                        {#each parseListField(r.ingredients) as ing}
                          <li>{ing}</li>
                        {/each}
                      </ul>

                      <h4>Préparation</h4>
                      <ol>
                        {#each parseListField(r.steps) as step}
                          <li>{step}</li>
                        {/each}
                      </ol>
                    </div>
                  </details>
                </div>
              </article>
            {/each}
          {/if}
        {/if}
      </div>
    </section>
  </div>
</div>
