<script>
  import Header from './components/Header.svelte';
  import Footer from './components/Footer.svelte';
  import MapVisualization from './components/MapVisualization.svelte';
  import Categories from './components/Categories.svelte';
  import Honouredwomen from './components/Honouredwomen.svelte';
  import Cookies from './components/Cookies.svelte';
  import Waffle from './components/Waffle.svelte';
  import Intro from './components/Intro.svelte';

  // show the initial prompt until the user makes a choice
  let promptVisible = true;
  let userChoice = null; // 'yes' | 'no'

  function handleChoice(event) {
    userChoice = event.detail;
    promptVisible = false;
  }
</script>

<div class="app-container">
  <Header />
  <Intro />
  
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


</style>

