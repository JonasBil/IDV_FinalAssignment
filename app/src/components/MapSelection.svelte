<script>
  import { Plot, Geo } from 'svelteplot';
  import { geoMercator } from 'd3-geo';
  import cityData from '../city_centers.json';
  import '../Styles.css';

  let europe = $state(null);
  const width = 600;
  const height = 500;
  
  // Begin state
  let baseScale = $state(100);
  let baseTranslate = $state([0, 0]);
  let zoom = $state(25);
  let pan = $state({ x: 0, y: 0 });
  
  // Interaction
  let dragging = false;
  let start = { x: 0, y: 0 };
  let hovered = $state(null);
  let tooltip = $state({ x: 0, y: 0 });

  const cityFeatures = Object.entries(cityData).map(([name, coords]) => ({
    type: 'Feature',
    properties: { name },
    geometry: {
      type: 'Point',
      coordinates: [coords.lon, coords.lat]
    }
  }));

  const cities = {
    type: 'FeatureCollection',
    features: cityFeatures
  };

  // Projection for zooming and panning
  let scale = $derived(baseScale * (1 + zoom / 50));
  let translate = $derived([
    (width / 2) * (1 - (1 + zoom / 50)) + baseTranslate[0] * (1 + zoom / 50) + pan.x,
    (height / 2) * (1 - (1 + zoom / 50)) + baseTranslate[1] * (1 + zoom / 50) + pan.y
  ]);
  
  let projection = $derived(geoMercator().scale(scale).translate(translate));

  async function getEuropeData() {
    const response = await fetch('https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson');
    europe = await response.json();
    fitMap(europe);
  }

  function handleHover(e) {
    console.log('Hover event:', e.detail); // Debugging line
    const d = e.detail.data;
    // Check if the hovered item is a city point
    if (d && d.properties && d.properties.name) {
      hovered = d;
      tooltip = { x: e.detail.x, y: e.detail.y };
    } else {
      hovered = null;
    }
  }

  function handleWheel(e) {
    e.preventDefault();
    const d = -Math.sign(e.deltaY) * 25;
    zoom = Math.max(0, Math.min(500, zoom + d));
  }

  function fitMap(data) {
    const p = geoMercator().fitSize([width, height], data);
    baseScale = p.scale();
    baseTranslate = p.translate();
    pan = { x: 0, y: 0 };
    zoom = 25;
  }

  getEuropeData();

</script>

{#if hovered}
  <div class="tooltip" style="position: fixed; top: {tooltip.y + 5}px; left: {tooltip.x + 5}px;">
    {hovered.properties.name}
  </div>
{/if}

<div class="visualization-container">
  <div class="header">
    <h1>
      Map of Europe 
      {#if hovered}
        <span class="hovered-city">: {hovered.properties.name.toUpperCase()}</span>
      {/if}
    </h1>
    <div class="controls">
      <div class="slider-control">
        <label for="zoom">Zoom</label>
        <input 
          type="range" 
          id="zoom" 
          bind:value={zoom} 
          min="0" 
          max="500" 
        />
      </div>
    </div>
  </div>

  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div 
    class="map-container" 
    onwheel={handleWheel}
    onmousedown={(e) => { dragging = true; start = { x: e.clientX - pan.x, y: e.clientY - pan.y }; }}
    onmousemove={(e) => { 
      if (dragging) { 
        e.preventDefault(); 
        pan = { x: e.clientX - start.x, y: e.clientY - start.y }; 
      }
    }}
    onmouseup={() => { dragging = false; }}
    onmouseleave={() => { dragging = false; }}
  >
    {#if europe}
      <Plot {projection} {width} {height} on:hover={handleHover}>
        <Geo data={europe.features} stroke="white" fill="#374151" />
        <Geo data={cities.features} r={3} fill="#fb923c" />
      </Plot>
    {/if}
  </div>
</div>

<style>
  .map-container {
    display: flex;
    justify-content: center;
    background-color: #1f2937; /* Added background */
    border-radius: 0.5rem;      /* Rounded corners */
    overflow: hidden;           /* Contain the map on zoom */
  }

  .hovered-city {
    color: #fb923c;
    text-transform: capitalize;
  }

  .tooltip {
    background: #111827;
    color: #f3f4f6;
    padding: 0.5rem 0.75rem;
    border-radius: 0.25rem;
    border: 1px solid #374151;
    pointer-events: none; /* so it doesn't block mouse events on the map */
    z-index: 10;
  }
</style>