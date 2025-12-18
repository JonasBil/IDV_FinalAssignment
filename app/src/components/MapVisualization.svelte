<script>
  import { Plot, Geo } from 'svelteplot';
  import { geoMercator } from 'd3-geo';
  import '../Styles.css';

  // Cities available in the dataset
  const cities = ['ancona', 'athene', 'barcelona', 'berlin', 'bologna', 'brussels', 'bucuresti', 'budapest', 'chisinau', 'debrecen', 'firenze', 'gdansk', 'genova', 'katowice', 'krakow', 'kyiv', 'københavn', 'lisboa', 'lyon', 'madrid', 'milano', 'munchen', 'oslo', 'palermo', 'paris', 'praha', 'roma', 'sevilla', 'sibiu', 'stockholm', 'torino', 'warszawa', 'wien', 'wrocław', 'zagreb', 'łodz'];

  let selectedCity = $state('brussels');
  let geoData = $state.raw(null);
  let width = $state(0);
  let height = $state(0);
  
  // Begin state
  let baseScale = $state(100);
  let baseTranslate = $state([0, 0]);
  let zoom = $state(25);
  let pan = $state({ x: 0, y: 0 });
  
  // Interaction
  let dragging = false;
  let start = { x: 0, y: 0 };
  let moved = false;
  let selected = $state(null);

  // Geometry arrays (merged for performance)
  let layers = $state({ female: [], male: [], other: [] });
  let counts = $state({ female: 0, male: 0, other: 0 });

  // Projection for zooming and panning
  let scale = $derived(baseScale * (1 + zoom / 50));
  let translate = $derived([
    (width / 2) * (1 - (1 + zoom / 50)) + baseTranslate[0] * (1 + zoom / 50) + pan.x,
    (height / 2) * (1 - (1 + zoom / 50)) + baseTranslate[1] * (1 + zoom / 50) + pan.y
  ]);
  
  let projection = $derived(geoMercator().scale(scale).translate(translate));

  // Load and process city data
  async function load(city) {
    geoData = null;
    
    try {
      // Note: Adjusted path for component location
      const data = (await import(`../CityStreetData/${city}_enriched.json`)).default;
      geoData = data;
      
      // Reset view
      if (width && height) fitMap(data);

      // Group features in array by gender to reduce DOM elements
      const groups = { female: [], male: [], other: [] };
      const c = { female: 0, male: 0, other: 0 };

      for (const f of data.features) {
        const g = f.properties.gender || 'other';
        // Map null/unknown to 'other', keep 'female'/'male'
        const key = (g === 'female' || g === 'male') ? g : 'other';
        
        const coords = f.geometry.coordinates;
        // Flatten MultiLineStrings so it can be displayed as one element in the DOM
        if (f.geometry.type === 'LineString') groups[key].push(coords);
        else groups[key].push(...coords);
        
        c[key]++;
      }

      // Convert back to GeoJSON MultiLineString
      const toGeo = (coords) => coords.length ? [{ type: 'Feature', geometry: { type: 'MultiLineString', coordinates: coords } }] : [];
      
      layers = {
        female: toGeo(groups.female),
        male: toGeo(groups.male),
        other: toGeo(groups.other)
      };
      counts = c;

    } catch (err) {
      console.error("Failed to load city:", err);
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

  // Watch for city changes
  $effect(() => { load(selectedCity); });

  // Watch for resize if data is loaded but not fitted
  $effect(() => {
    if (geoData && width && height && baseScale === 100) fitMap(geoData);
  });

  // Math helper for clicking lines
  function getSqDist(p, v, w) {
    const l2 = (v[0] - w[0])**2 + (v[1] - w[1])**2;
    if (l2 === 0) return (p[0] - v[0])**2 + (p[1] - v[1])**2;
    let t = ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2;
    t = Math.max(0, Math.min(1, t));
    return (p[0] - (v[0] + t * (w[0] - v[0])))**2 + (p[1] - (v[1] + t * (w[1] - v[1])))**2;
  }

  function handleClick(e) {
    if (moved || !geoData) return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const [lon, lat] = projection.invert([e.clientX - rect.left, e.clientY - rect.top]);
    const p = [lon, lat];
    
    let closest = null;
    let minD = Infinity;
    const limit = 0.0005 ** 2;

    // Check all streets
    for (const f of geoData.features) {
      let d = Infinity;
      const coords = f.geometry.coordinates;
      
      // Handle both LineString and MultiLineString
      const lines = f.geometry.type === 'LineString' ? [coords] : coords;
      
      for (const line of lines) {
        for (let i = 0; i < line.length - 1; i++) {
          const dist = getSqDist(p, line[i], line[i+1]);
          if (dist < d) d = dist;
        }
      }

      if (d < minD && d < limit) {
        minD = d;
        closest = f;
      }
    }
    selected = closest ? closest.properties : null;
  }

  // Handle historical dates
  function niceDate(str) {
    if (!str) return '';
    const m = str.match(/^([+-]?\d+)-(\d{2})-(\d{2})/);
    if (!m) return str;
    
    let [_, y, mon, d] = m;
    let year = Math.abs(parseInt(y));
    const bc = parseInt(y) < 0 ? ' BC' : '';
    
    if (mon === '00' || d === '00') return `${year}${bc}`;
    
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${parseInt(d)} ${months[parseInt(mon)-1]} ${year}${bc}`;
  }
</script>

<div class="visualization-container">
  <div class="header">
    <h1>Street Names Gender</h1>
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
      <select bind:value={selectedCity}>
        {#each cities as city}
          <option value={city}>{city}</option>
        {/each}
      </select>
    </div>
  </div>

  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div 
    class="map-container" 
    bind:clientWidth={width} 
    bind:clientHeight={height}
    onwheel={handleWheel}
    onmousedown={(e) => { dragging = true; moved = false; start = { x: e.clientX - pan.x, y: e.clientY - pan.y }; }}
    onmousemove={(e) => { 
      if (dragging) { 
        e.preventDefault(); 
        const dx = e.clientX - start.x - pan.x;
        const dy = e.clientY - start.y - pan.y;
        if (Math.abs(dx) > 2 || Math.abs(dy) > 2) moved = true;
        pan = { x: e.clientX - start.x, y: e.clientY - start.y }; 
      } 
    }}
    onmouseup={(e) => { dragging = false; if (!moved) handleClick(e); }}
    onmouseleave={() => dragging = false}
  >
    {#if geoData && width > 0}
      <div class="movable">
        {#key selectedCity}
          <Plot {width} {height} {projection}>
            <Geo data={layers.other} stroke="#5c6c86" strokeWidth={1} />
            <Geo data={layers.male} stroke="#60a5fa" strokeWidth={2} />
            <Geo data={layers.female} stroke="#fb923c" strokeWidth={3} />
          </Plot>
        {/key}
      </div>
    {:else}
      <div class="loading">Loading...</div>
    {/if}

    {#if geoData}
      <div class="legend">
        <div class="item"><span class="box female"></span> Female ({counts.female})</div>
        <div class="item"><span class="box male"></span> Male ({counts.male})</div>
        <div class="item"><span class="box other"></span> Other ({counts.other})</div>
      </div>
    {/if}

    {#if selected}
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
      <div 
        class="popup"
        onwheel={(e) => e.stopPropagation()}
        onmousedown={(e) => e.stopPropagation()}
        onmouseup={(e) => e.stopPropagation()}
        onclick={(e) => e.stopPropagation()}
      >
        <button class="close" onclick={() => selected = null}>×</button>
        <h2>{selected.street_name}</h2>
        {#if selected.is_person}
          <div class="person-details">
            {#if selected.picture_embed}
              <img src={selected.picture_embed} alt={selected.label} />
            {/if}
            <h3>{selected.label}</h3>
            <p class="desc">{selected.description || 'No description available'}</p>
            
            <div class="meta">
              {#if selected.date_of_birth}
                <div><strong>Born:</strong> {niceDate(selected.date_of_birth)} {selected.place_of_birth_label ? `in ${selected.place_of_birth_label}` : ''}</div>
              {/if}
              {#if selected.date_of_death}
                <div><strong>Died:</strong> {niceDate(selected.date_of_death)} {selected.place_of_death_label ? `in ${selected.place_of_death_label}` : ''}</div>
              {/if}
              {#if selected.occupation_label}
                <div><strong>Occupation:</strong> {selected.occupation_label}</div>
              {/if}
            </div>

            {#if selected.wikipedia}
              <a href={selected.wikipedia} target="_blank" rel="noopener noreferrer">Wikipedia →</a>
            {/if}
          </div>
        {:else}
          <p>Not named after a person.</p>
        {/if}
      </div>
    {/if}
  </div>

  <div class="description">
    <p>
      This map explores gender representation in European street names, highlighting <span class="orange_bold">female</span> and <span class="blue_bold">male</span> streets. 
      Based on the Mapping Diversity project by the European Data Journalism Network, it analyzes 145,000+ streets across 30+ cities to spark debate on urban representation. The dataset includes biographical data from Wikidata for each person.
    </p>
  </div>
</div>

<style>
  .visualization-container { padding: 1rem; }
  
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
  .controls { display: flex; align-items: center; gap: 1rem; }
  
  .slider-control { display: flex; align-items: center; gap: 0.5rem; background: #1f2937; padding: 0.5rem 1rem; border-radius: 0.25rem; border: 1px solid #374151; }
  .slider-control label { font-size: 0.9rem; font-weight: 500; }
  .slider-control input[type=range] { width: 100px; accent-color: #fb923c; cursor: pointer; }

  h1 { margin: 0; font-size: 1.5rem; border-bottom: 3px solid #fb923c; display: inline-block; padding-bottom: 0.25rem; }
  select { padding: 0.5rem; background: #1f2937; color: white; border: 1px solid #374151; border-radius: 0.25rem; }

  .map-container { width: 100%; height: 600px; position: relative; background: #1f2937; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); cursor: grab; }
  .map-container:active { cursor: grabbing; }
  .movable { width: 100%; height: 100%; transform-origin: center; will-change: transform; }
  
  /* Allow SVG to overflow so we can pan to see hidden parts */
  :global(.map-container svg) { overflow: visible; }

  .loading { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #9ca3af; }

  .legend { position: absolute; bottom: 1rem; right: 1rem; background: rgba(31, 41, 55, 0.9); padding: 1rem; border-radius: 0.5rem; border: 1px solid #374151; }
  .item { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; font-size: 0.9rem; }
  .box { width: 1rem; height: 1rem; border-radius: 0.25rem; }
  
  .female { background: #fb923c; }
  .male { background: #60a5fa; }
  .other { background: #5c6c86; }

  .popup {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 0.5rem;
    padding: 1.5rem;
    width: 300px;
    max-height: calc(100% - 12rem);
    overflow-y: auto;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    z-index: 10;
  }
  .popup h2 { margin: 0 0 1rem 0; font-size: 1.25rem; color: #f3f4f6; }
  .popup .close {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: none;
    border: none;
    color: #9ca3af;
    font-size: 1.5rem;
    cursor: pointer;
  }
  .popup .close:hover { color: #f3f4f6; }
  .person-details img { width: 100%; border-radius: 0.25rem; margin-bottom: 1rem; }
  .person-details h3 { margin: 0 0 0.5rem 0; font-size: 1.1rem; color: #fb923c; }
  .person-details .desc { font-size: 0.9rem; color: #d1d5db; margin-bottom: 1rem; line-height: 1.4; }
  .meta { font-size: 0.85rem; color: #9ca3af; margin-bottom: 1rem; }
  .meta div { margin-bottom: 0.25rem; }
  .popup a { color: #60a5fa; text-decoration: none; font-size: 0.9rem; }
  .popup a:hover { text-decoration: underline; }

  .description { margin-top: 1.5rem; padding: 1rem; background: #1f2937; border-left: 3px solid #fb923c; color: #9ca3af; font-size: 0.85rem; line-height: 1.5; }
  .description h3 { margin-top: 0; color: #e5e7eb; font-size: 1rem; margin-bottom: 0.5rem; }
</style>
