<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { X } from '@lucide/svelte';

  const dispatch = createEventDispatcher();

  export let open: boolean = false;

  let name = '';
  let description = '';
  let images_input = '';
  let ingredients_input = '';
  let steps_input = '';
  let prep_time = '';
  let cook_time = '';
  let total_time = '';
  let difficulty = '';
  let budget = '';
  let recipe_quantity = '';
  let rate = '';
  let url = '';

  function close() {
    dispatch('close');
  }

  async function create() {
    const payload = {
      name,
      description,
      images: JSON.stringify(images_input.split('\n').map(s=>s.trim()).filter(Boolean)),
      ingredients: JSON.stringify(ingredients_input.split('\n').map(s=>s.trim()).filter(Boolean)),
      steps: JSON.stringify(steps_input.split('\n').map(s=>s.trim()).filter(Boolean)),
      prep_time,
      cook_time,
      total_time,
      difficulty,
      budget,
      recipe_quantity,
      rate,
      url
    };

    try {
      const res = await fetch('/api/recipes', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      if (res.ok) {
        const created = await res.json();
        dispatch('created', created);
        close();
      } else {
        const err = await res.json();
        alert(err.error || 'Erreur');
      }
    } catch (e) {
      console.error(e);
      alert('Erreur');
    }
  }
</script>

{#if open}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="backdrop" role="button" tabindex="0" aria-label="Fermer le modal" on:click={() => dispatch('close')} on:keydown={(e) => { if (e.key === 'Enter' || e.key === ' ') dispatch('close'); }}></div>
    <div class="modal">
      <header class="modal-header">
        <h3>Ajouter une recette</h3>
        <button class="close-btn" on:click={() => dispatch('close')} aria-label="Fermer"><X /></button>
      </header>

      <div class="modal-body">
        <label>Nom<input bind:value={name} /></label>
        <label>Description<textarea bind:value={description} rows={3}></textarea></label>
        <label>Images (une URL par ligne)<textarea bind:value={images_input} rows={3}></textarea></label>
        <label>Ingrédients<textarea bind:value={ingredients_input} rows={4}></textarea></label>
        <label>Étapes<textarea bind:value={steps_input} rows={6}></textarea></label>
        <label>Préparation<input bind:value={prep_time} /></label>
        <label>Cuisson<input bind:value={cook_time} /></label>
        <label>Temps total<input bind:value={total_time} /></label>
        <label>Difficulté<input bind:value={difficulty} /></label>
        <label>Budget<input bind:value={budget} /></label>
        <label>Quantité<input bind:value={recipe_quantity} /></label>
        <label>Note<input bind:value={rate} /></label>
        <label>URL source<input bind:value={url} /></label>

        <div class="actions">
          <button class="create" on:click={create}>Créer</button>
          <button class="cancel" on:click={close}>Annuler</button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .backdrop { position:fixed; inset:0; background:rgba(0,0,0,0.45); z-index:40 }
  .modal { width:min(760px,95%); background:white; padding:1rem; border-radius:10px; box-shadow:0 20px 60px rgba(2,6,23,0.2); z-index:50 }
  .modal-header { display:flex; justify-content:space-between; align-items:center }
  label { display:block; margin:0.5rem 0 }
  input, textarea { width:100%; padding:0.5rem; border:1px solid #ddd; border-radius:6px }
  .actions { display:flex; gap:0.5rem; justify-content:flex-end; margin-top:0.75rem }
  .create { background:linear-gradient(90deg,#06b6d4,#3b82f6); color:white; padding:0.45rem 0.75rem; border-radius:8px; border:none }
  .cancel { background:transparent; border:1px solid #ddd; padding:0.45rem 0.75rem; border-radius:8px }
</style>
