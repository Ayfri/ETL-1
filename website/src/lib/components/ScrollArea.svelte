<script lang="ts">
  export let className: string = '';
  export let ariaLabel: string | undefined;
</script>

<style>
  .scroll-area {
    overflow: auto;
    -webkit-overflow-scrolling: touch;
  }

  /* Thin, subtle custom scrollbar */
  .scroll-area::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  .scroll-area::-webkit-scrollbar-thumb {
    background: rgba(15, 23, 42, 0.12); /* gray-900/12 */
    border-radius: 9999px;
  }

  .scroll-area::-webkit-scrollbar-track {
    background: transparent;
  }

  @supports (scrollbar-width: thin) {
    .scroll-area { scrollbar-width: thin; scrollbar-color: rgba(15,23,42,0.12) transparent; }
  }
</style>

<div class={"scroll-area " + className} role={ariaLabel ? 'region' : undefined} aria-label={ariaLabel}>
  <slot />
</div>


