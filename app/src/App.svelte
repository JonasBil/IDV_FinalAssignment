<script>
  import Header from './components/Header.svelte';
  import Footer from './components/Footer.svelte';
  import MapVisualization from './components/MapVisualization.svelte';
  import Categories from './components/Categories.svelte';
  import Honouredwomen from './components/Honouredwomen.svelte';
</script>

<div class="app-container">
  <Header />
  
  <main>
    <div>
      <MapVisualization />
    </div>
    <div class="charts-container">
      <Categories />
    </div>
    <div class="charts-container">
      <Honouredwomen />
    </div>
  </main>



  <Footer />
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
</style>
