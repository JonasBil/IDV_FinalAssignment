<script>
  import Header from './components/Header.svelte';
  import Footer from './components/Footer.svelte';
  import MapVisualization from './components/MapVisualization.svelte';
  import Categories from './components/Categories.svelte';
  import Honouredwomen from './components/Honouredwomen.svelte';
  import Cookies from './components/Cookies.svelte';
  import Waffle from './components/Waffle.svelte';

  // show the initial prompt until the user makes a choice
  let promptVisible = true;
  let userChoice = null; // 'yes' | 'no'

  function handleChoice(event) {
    userChoice = event.detail;
    promptVisible = false;
  }
</script>

<div class="intro">
  <h1>Who gets remembered in our streets?</h1>

  <p>
    In <strong>Paris</strong>, 2,725 streets are named after people.
    <strong>2,569</strong> honour men, while <strong>156</strong> are named after women, which correspond to <strong>6%</strong>. In <strong>Debrecen</strong>, the imbalance is even sharper. Out of 273 eponymic streets, <strong>265</strong> are named after men
    and just <strong>8</strong> after women, less than <strong>3%</strong>. Beyond numbers, the occupation of these women who are remembered in the streets differs too. In Paris, most streets are associated with <strong>culture</strong>
    (<strong>37.2%</strong>), while in Debrecen nearly half (<strong>44.4%</strong>) are linked to <strong>politics</strong>.
  </p>

  <p class="cta">
    Explore more below...
  </p>
</div>


<div class="app-container">
  <Header />
  
  <main>
    <div class="content" aria-hidden={promptVisible}>
      <MapVisualization />

      <div class="charts-container">
        <Categories />
      </div>

      <div class="charts-container">
        <Honouredwomen />
      </div>
      <div class="charts-container">
        <Waffle/>
      </div>
    </div>
  </main>

  <Footer />

  {#if promptVisible}
    <!-- Cookies prompt overlays the page until user picks an option -->
    <Cookies on:choose={handleChoice} />
  {/if}
</div>

<style>
  :global(body) { 
    margin: 0; 
    background: #111827; 
    color: #f3f4f6; 
    font-family: sans-serif; 
  }
  
  .app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  main {
    flex: 1;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
  }

  .charts-container {
    margin-top: 2rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
    background-color: #1f2937;
  }

  /* dim the background slightly while prompt is visible */
  .content[aria-hidden="true"] {
    filter: blur(1px) brightness(0.9);
    pointer-events: none;
    user-select: none;
  }

  .intro {
    max-width: 1000px;
    margin: 3rem auto 2rem;
    padding: 0 1.5rem;
    color: #e5e7eb;
    text-align: center;
  }

  .cta {
    font-size: 0.95rem;
    color: #9ca3af;
    font-style: italic;
  }

</style>

