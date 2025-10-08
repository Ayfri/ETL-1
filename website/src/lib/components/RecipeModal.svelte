<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { fly, scale, fade } from 'svelte/transition';
  import { X } from '@lucide/svelte';

  export let open: boolean = false;
  export let recipe: any = null;
  const dispatch = createEventDispatcher();

  function close() {
    dispatch('close');
  }

  let modalEl: HTMLElement | null = null;

  function onBackdropClick(e: Event) {
    // accept MouseEvent or KeyboardEvent - close only when target is backdrop
    const target = (e as any).target;
    const current = (e as any).currentTarget;
    if (target === current) close();
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

  function getFirstImageForRecipe(r: any): string {
    if (!r) return '';
    // try parsing images field (could be JSON string or array or newline list)
    const imgs = parseListField(r.images || r.image_url || '');
    if (imgs.length) return imgs[0];
    // fallback to image_url if present
    if (typeof r.image_url === 'string' && r.image_url.trim()) return r.image_url.trim();
    return '';
  }
</script>

{#if open && recipe}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div
      class="backdrop"
      role="button"
      tabindex="0"
      aria-label="Fermer le modal"
      on:click={onBackdropClick}
      on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') onBackdropClick(e); }}
      transition:fade
    ></div>

    <div bind:this={modalEl} class="modal" transition:scale={{ duration: 220 }}>
      <header class="modal-header">
        <div class="heading">
          <h3>{recipe.name}</h3>
          {#if recipe.recipe_quantity}<span class="pill">{recipe.recipe_quantity}</span>{/if}
        </div>
        <button class="close-btn" on:click={close} aria-label="Fermer"><X /></button>
      </header>

      <div class="modal-body">
        {#if getFirstImageForRecipe(recipe)}
          <img src={getFirstImageForRecipe(recipe)} alt={recipe.name || 'Recette'} class="hero" />
        {/if}

        <section class="sections">
          <div class="left">
            <div class="section card">
              <h4>Ingrédients</h4>
              <ul>
                {#each parseListField(recipe.ingredients) as ing}
                  <li>{ing}</li>
                {/each}
              </ul>
            </div>

            <div class="section card">
              <h4>Préparation</h4>
              <ol>
                {#each parseListField(recipe.steps) as step}
                  <li>{step}</li>
                {/each}
              </ol>
            </div>
          </div>

          <aside class="right">
            <div class="card small">
              {#if recipe.prep_time}<div><strong>Préparation:</strong> {recipe.prep_time}</div>{/if}
              {#if recipe.cook_time}<div><strong>Cuisson:</strong> {recipe.cook_time}</div>{/if}
              {#if recipe.total_time}<div><strong>Temps total:</strong> {recipe.total_time}</div>{/if}
              {#if recipe.difficulty}<div><strong>Difficulté:</strong> {recipe.difficulty}</div>{/if}
              {#if recipe.budget}<div><strong>Budget:</strong> {recipe.budget}</div>{/if}
              {#if recipe.rate}<div><strong>Note:</strong> ★ {recipe.rate}</div>{/if}
            </div>

            {#if recipe.description}
              <div class="card small">
                <h5>Description</h5>
                <p>{recipe.description}</p>
              </div>
            {/if}

            {#if recipe.url}
              <div class="card small">
                <a href={recipe.url} target="_blank" rel="noopener noreferrer" class="source-link">Ouvrir la source</a>
              </div>
            {/if}
          </aside>
        </section>
      </div>
    </div>
  </div>
{/if}

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(10,11,13,0.55);
    backdrop-filter: blur(3px);
    z-index: 50;
  }

  .modal {
    z-index: 60;
    width: min(1100px, 95%);
    max-height: 90vh;
    overflow: auto;
    background: linear-gradient(180deg, #ffffff, #fffaf3);
    border-radius: 12px;
    box-shadow: 0 12px 40px rgba(16,24,40,0.35);
    padding: 1rem;
    transform-origin: center center;
  }

  .modal-header { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:0.5rem }
  .modal-header .heading h3 { margin:0; font-size:1.4rem }
  .pill { background:linear-gradient(90deg,#ffd6a5,#ff7b7b); padding:0.25rem 0.5rem; border-radius:999px; font-weight:600; color:#2b2b2b; margin-left:0.5rem }
  .close-btn { background:transparent; border:none; padding:0.25rem; cursor:pointer }

  .modal-body { padding:0.5rem }
  .hero { width:100%; height:300px; object-fit:cover; border-radius:10px; margin-bottom:0.75rem }

  .sections { display:grid; grid-template-columns: 1fr 320px; gap:1rem }
  .left { display:flex; flex-direction:column; gap:1rem }
  .right { display:flex; flex-direction:column; gap:1rem }

  .card { background: linear-gradient(180deg,#fff,#fffefc); border-radius:8px; padding:0.75rem; box-shadow: 0 2px 8px rgba(11,12,16,0.06) }
  .card.small { padding:0.6rem }
  .section h4 { margin:0 0 0.4rem 0 }
  ul, ol { margin:0; padding-left:1.1rem }

  .source-link { display:inline-block; color:#ff6b00; font-weight:700 }

  @media (max-width: 800px) {
    .sections { grid-template-columns: 1fr }
    .hero { height:200px }
    .modal { width: 96% }
  }
</style>
