<script>
  let easterEggActive = $state(false);

  function triggerEasterEgg() {
    easterEggActive = true;
    createConfetti();
    // Hide after 3 seconds
    setTimeout(() => {
      easterEggActive = false;
    }, 3000);
  }

  function createConfetti() {
    const colors = ['#fb923c', '#60a5fa', '#34d399', '#f472b6', '#a78bfa'];
    const container = document.body;
    for (let i = 0; i < 100; i++) {
      const confetti = document.createElement('div');
      confetti.className = 'confetti-piece';
      confetti.style.cssText = `
        position: fixed;
        width: ${Math.random() * 10 + 5}px;
        height: ${Math.random() * 10 + 5}px;
        background: ${colors[Math.floor(Math.random() * colors.length)]};
        left: ${Math.random() * 100}vw;
        top: -20px;
        border-radius: ${Math.random() > 0.5 ? '50%' : '0'};
        pointer-events: none;
        z-index: 10000;
        animation: confetti-fall ${Math.random() * 3 + 2}s linear forwards;
        transform: rotate(${Math.random() * 360}deg);
      `;
      container.appendChild(confetti);
      setTimeout(() => confetti.remove(), 3000);
    }
  }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<footer class:rainbow={easterEggActive} onclick={triggerEasterEgg}>
  <p>&copy; 2025 Bil Jonas; Fronhoffs Gaëlle; Samyns Alex; Wallens Niels. All rights reserved.</p>
</footer>

{#if easterEggActive}
  <div class="cake-overlay" onclick={() => easterEggActive = false}>
    <div class="cake-message">
      <span class="cake-emoji">🎂</span>
      <p>Here is a cake!!</p>
    </div>
  </div>
{/if}

<style>
  footer {
    background: #1f2937;
    padding: 1rem 2rem;
    text-align: center;
    color: #6b7280;
    font-size: 0.9rem;
    border-top: 1px solid #374151;
    margin-top: 2rem;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .rainbow {
    background: linear-gradient(90deg, #fb923c, #f472b6, #a78bfa, #60a5fa, #34d399, #fb923c);
    background-size: 400% 100%;
    animation: rainbow-shift 2s linear infinite;
    color: white;
    border-top-color: transparent;
  }

  footer:hover {
    background: #374151;
  }

  .cake-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    cursor: pointer;
  }

  .cake-message {
    text-align: center;
    animation: pop-in 0.3s ease-out;
  }

  .cake-emoji {
    font-size: 8rem;
    display: block;
    animation: bounce 0.5s ease infinite alternate;
  }

  .cake-message p {
    font-size: 2rem;
    color: white;
    margin-top: 1rem;
    font-weight: bold;
  }

  @keyframes pop-in {
    from { 
      transform: scale(0);
      opacity: 0;
    }
    to { 
      transform: scale(1);
      opacity: 1;
    }
  }

  @keyframes rainbow-shift {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
  }

  @keyframes bounce {
    from { transform: translateY(0); }
    to { transform: translateY(-10px); }
  }

  /* Confetti animation keyframes are in Styles.css */
</style>
