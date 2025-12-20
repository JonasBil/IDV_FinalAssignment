<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';

  const dispatch = createEventDispatcher();

  import brownieImg from '../Figures/brownie-clipart-lg.png';

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
    <div class="illustration" aria-hidden="true">
      <!-- use provided brownie image from Figures -->
      <img src={brownieImg} alt="" aria-hidden="true" class="figure-img" />
    </div>
    <p class="prompt">We work with Brownies.</p>
    <div class="actions">
  <button class="btn" bind:this={primaryBtn} on:click={() => choose('yes')}>Accept</button>
      <button class="btn" bind:this={secondaryBtn} on:click={() => choose('no')}>Reject, I prefer Cookies 🍪</button>
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
    max-width: 600px;
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

  /* Make primary button turn orange on hover */
  .btn:hover {
    background: #fb923c; /* orange */
    box-shadow: 0 8px 20px rgba(251,146,60,0.18);
    transform: translateY(-1px);
  }

  .btn:active { transform: translateY(1px); }


  /* keep the brownie fully inside the modal box */
  .modal { position: relative; padding-top: 1rem; }
  .illustration { position: static; margin-bottom: 0.6rem; text-align: center; }
  .figure-img {
    width: 160px;
    max-width: 80vw;
    height: auto;
    display: inline-block;
    margin: 0 auto 0.5rem auto;
    border-radius: 8px;
  }

</style>
