<script>
  import Header from './components/Header.svelte';
  import Footer from './components/Footer.svelte';
  import MapVisualization from './components/MapVisualization.svelte';
  import Categories from './Categories.svelte';
  import Honouredwomen from './Honouredwomen.svelte';
</script>

<div class="app-container">
  <Header />
  
  <main>
    <MapVisualization />
    <Categories />
    <Honouredwomen />
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
</style>
