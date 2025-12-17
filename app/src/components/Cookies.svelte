<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';

  const dispatch = createEventDispatcher();

  let primaryBtn;
  let secondaryBtn;
  let modalEl;
  let previousBodyOverflow;

  function choose(value) {
    // restore body scroll immediately before dispatching so the page becomes normal
    if (typeof document !== 'undefined') document.body.style.overflow = previousBodyOverflow || '';
    dispatch('choose', value);
  }

  // Trap focus inside the modal and prevent background scrolling while mounted
  function handleKeydown(e) {
    // prevent Escape from closing or moving focus
    if (e.key === 'Escape' || e.key === 'Esc') {
      e.preventDefault();
      return;
    }

    if (e.key !== 'Tab') return;

    const focusable = [primaryBtn, secondaryBtn].filter(Boolean);
    if (focusable.length === 0) return;

    const active = document.activeElement;
    const idx = focusable.indexOf(active);

    if (e.shiftKey) {
      // Shift+Tab: if focus is on first, move to last
      if (idx === 0 || active === modalEl) {
        e.preventDefault();
        focusable[focusable.length - 1].focus();
      }
    } else {
      // Tab: if focus is on last, move to first
      if (idx === focusable.length - 1 || active === modalEl) {
        e.preventDefault();
        focusable[0].focus();
      }
    }
  }

  onMount(() => {
    if (typeof document !== 'undefined') {
      previousBodyOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
    }

    // focus first button on mount
    setTimeout(() => {
      if (primaryBtn) primaryBtn.focus();
      else if (secondaryBtn) secondaryBtn.focus();
    }, 0);

    // listen early to capture tab events
    document.addEventListener('keydown', handleKeydown, true);
  });

  onDestroy(() => {
    if (typeof document !== 'undefined') document.body.style.overflow = previousBodyOverflow || '';
    document.removeEventListener('keydown', handleKeydown, true);
  });
</script>

<div class="overlay" role="dialog" aria-modal="true" aria-label="Cookie choice dialog">
  <div class="modal" bind:this={modalEl} tabindex="-1">
    <p class="prompt">Do you accept Brownies?</p>

    <div class="actions">
      <button class="btn primary" bind:this={primaryBtn} on:click={() => choose('yes')}>Yes</button>
      <button class="btn" bind:this={secondaryBtn} on:click={() => choose('no')}>No, I prefer cookies</button>
    </div>
  </div>
</div>

<style>
  .overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,0,0,0.55);
    z-index: 9999;
    padding: 1rem;
  }

  .modal {
    width: 100%;
    max-width: 480px;
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 10px 30px rgba(2,6,23,0.6);
    color: #f9fafb;
    text-align: center;
  }

  .prompt {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    line-height: 1.4;
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
    margin-top: 0.5rem;
  }

  .btn {
    padding: 0.6rem 0.9rem;
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.06);
    background: transparent;
    color: #f3f4f6;
    cursor: pointer;
    font-weight: 600;
  }

  .btn:active { transform: translateY(1px); }
  .btn:focus { outline: 3px solid rgba(16,185,129,0.18); }
</style>
