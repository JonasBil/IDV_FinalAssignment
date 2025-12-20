<script>
  import { Plot, Geo } from 'svelteplot';
  import { geoMercator } from 'd3-geo';
  import cityData from '../city_centers.json';
  import { selectedCities } from '../stores/compareSelection.js';
  import '../Styles.css';
  import { LAU_NAME_TO_CITY_KEY, normalizeCityKey, displayCityName, CITY_KEY_TO_LAU } from '../cityMappings.js';

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
  let moved = false;
  let hovered = $state(null);
  let tooltipPos = $state({ x: 0, y: 0 });
  let clickRipples = $state([]);

  let femalePctByCity = $state({});
  let streetsLoading = $state(false);

  const cityKeySet = new Set(Object.keys(cityData));

  function toCityKey(name) {
    const raw = (name ?? '').toString().trim().toLowerCase();
    if (!raw) return null;
    
    // Check direct mapping from dataset lau_name to city key
    if (LAU_NAME_TO_CITY_KEY[raw]) return LAU_NAME_TO_CITY_KEY[raw];
    
    // Check if it's already a valid city key
    if (cityKeySet.has(raw)) return raw;

    // Strip diacritics and check mapping
    const stripped = normalizeCityKey(raw);
    if (LAU_NAME_TO_CITY_KEY[stripped]) return LAU_NAME_TO_CITY_KEY[stripped];
    if (cityKeySet.has(stripped)) return stripped;

    return raw;
  }

  function radiusForPct(pct) {
    const MIN_R = 3;
    const MAX_R = 12;
    const MULTIPLIER = 1.6;
    if (typeof pct !== 'number' || !Number.isFinite(pct)) return MIN_R;
    const clamped = Math.max(0, Math.min(100, pct));
    const scaled = MIN_R + (MAX_R - MIN_R) * Math.sqrt(clamped / 100);
    return Math.min(MAX_R, MIN_R + (scaled - MIN_R) * MULTIPLIER);
  }

  async function loadFemalePctByCity() {
    if (streetsLoading) return;
    streetsLoading = true;

    const cacheKey = 'femalePctByCity_fromStreets_v3';
    try {
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        femalePctByCity = JSON.parse(cached);
        return;
      }

      const streetsUrl = new URL('../Streets.json', import.meta.url);
      const res = await fetch(streetsUrl);
      const streets = await res.json();

      const totals = Object.create(null);
      const females = Object.create(null);

      for (const row of streets) {
        const city = toCityKey(row?.lau_name);
        if (!city) continue;
        totals[city] = (totals[city] ?? 0) + 1;

        const g = (row?.gender ?? '').toString().toLowerCase();
        if (g === 'female') females[city] = (females[city] ?? 0) + 1;
      }

      const pct = Object.create(null);
      for (const city of Object.keys(totals)) {
        pct[city] = ((females[city] ?? 0) / totals[city]) * 100;
      }

      femalePctByCity = pct;
      localStorage.setItem(cacheKey, JSON.stringify(pct));
    } catch (err) {
      console.error('Failed to compute female street percentages from Streets.json', err);
      femalePctByCity = {};
    } finally {
      streetsLoading = false;
    }
  }

  const cityFeatures = $derived(
    Object.entries(cityData).map(([name, coords]) => ({
      type: 'Feature',
      properties: {
        name,
        femalePct: femalePctByCity[name] ?? null
      },
      geometry: {
        type: 'Point',
        coordinates: [coords.lon, coords.lat]
      }
    }))
  );

  const cities = $derived({
    type: 'FeatureCollection',
    features: cityFeatures
  });

  // Projection for zooming and panning
  let scale = $derived(baseScale * (1 + zoom / 50));
  let translate = $derived([
    (width / 2) * (1 - (1 + zoom / 50)) + baseTranslate[0] * (1 + zoom / 50) + pan.x,
    (height / 2) * (1 - (1 + zoom / 50)) + baseTranslate[1] * (1 + zoom / 50) + pan.y
  ]);
  
  let projection = $derived(geoMercator().scale(scale).translate(translate));

  // Get projected coordinates for selected cities (for custom SVG overlay)
  // Must be after projection is defined
  const selectedCityCoords = $derived(
    $selectedCities.map(name => {
      const feature = cityFeatures.find(f => f.properties.name === name);
      if (!feature) return null;
      const [x, y] = projection(feature.geometry.coordinates);
      const r = radiusForPct(feature.properties.femalePct);
      return { name, x, y, r };
    }).filter(Boolean)
  );

  async function getEuropeData() {
    const response = await fetch('https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson');
    europe = await response.json();
    fitMap(europe);
  }

  function handleMouseMove(e) {
    // Tooltip position relative to the container
    const containerRect = e.currentTarget.getBoundingClientRect();
    tooltipPos = { 
      x: e.clientX - containerRect.left, 
      y: e.clientY - containerRect.top 
    };

    // City detection relative to the SVG (projection coordinates)
    const svg = e.currentTarget.querySelector('svg');
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    let closest = null;
    let minD2 = Infinity;

    for (const feature of cities.features) {
      const [cx, cy] = projection(feature.geometry.coordinates);
      const r = radiusForPct(feature?.properties?.femalePct) + 2;
      const d2 = (mx - cx) ** 2 + (my - cy) ** 2;
      if (d2 <= r * r && d2 < minD2) {
        minD2 = d2;
        closest = feature;
      }
    }

    hovered = closest;
  }

  function handleClick(e) {
    const svg = e.currentTarget.querySelector('svg');
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    let closest = null;
    let minD2 = Infinity;

    for (const feature of cities.features) {
      const [cx, cy] = projection(feature.geometry.coordinates);
      const r = radiusForPct(feature?.properties?.femalePct) + 2;
      const d2 = (mx - cx) ** 2 + (my - cy) ** 2;
      if (d2 <= r * r && d2 < minD2) {
        minD2 = d2;
        closest = feature;
      }
    }

    if (closest?.properties?.name) {
      // Add click ripple animation
      const [cx, cy] = projection(closest.geometry.coordinates);
      const r = radiusForPct(closest.properties.femalePct);
      const rippleId = Date.now();
      clickRipples = [...clickRipples, { id: rippleId, x: cx, y: cy, r }];
      
      // Remove ripple after animation completes
      setTimeout(() => {
        clickRipples = clickRipples.filter(rip => rip.id !== rippleId);
      }, 600);
      
      selectedCities.toggle(closest.properties.name);
    }
  }

  function handleMouseLeave() {
    hovered = null;
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
  loadFemalePctByCity();

  function displayCity(name) {
    if (!name) return '';
    // Try to get LAU name first, then use displayCityName for English name
    const lauName = CITY_KEY_TO_LAU[name] || CITY_KEY_TO_LAU[name.toLowerCase()];
    if (lauName) {
      const english = displayCityName(lauName);
      if (english && english !== lauName) return english;
    }
    // Fallback: capitalize city key
    const s = name.toString();
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

</script>

<div class="visualization-container">
  <div class="header">
    <h1>
      Map of Europe
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
    onmousedown={(e) => { dragging = true; moved = false; start = { x: e.clientX - pan.x, y: e.clientY - pan.y }; }}
    onmousemove={(e) => { 
      if (dragging) { 
        e.preventDefault(); 
        const dx = e.clientX - start.x - pan.x;
        const dy = e.clientY - start.y - pan.y;
        if (Math.abs(dx) > 2 || Math.abs(dy) > 2) moved = true;
        pan = { x: e.clientX - start.x, y: e.clientY - start.y }; 
      } else {
        handleMouseMove(e);
      }
    }}
    onmouseup={(e) => { dragging = false; if (!moved) handleClick(e); }}
    onmouseleave={() => { dragging = false; handleMouseLeave(); }}
  >
    {#if europe}
      <div class="plot-wrapper">
        <Plot {projection} {width} {height}>
          <Geo data={europe.features} stroke="white" fill="#374151" />
          <Geo 
            data={cities.features} 
            r={(d) => radiusForPct(d?.properties?.femalePct)} 
            fill={(d) => $selectedCities.includes(d?.properties?.name) ? '#3b82f6' : '#fb923c'} 
            stroke={(d) => $selectedCities.includes(d?.properties?.name) ? '#93c5fd' : 'none'}
            strokeWidth={(d) => $selectedCities.includes(d?.properties?.name) ? 2 : 0}
          />
        </Plot>
        
        <!-- Custom SVG overlay for selection animations -->
        <svg class="selection-overlay" {width} {height}>
          <!-- Click ripple animations -->
          {#each clickRipples as ripple (ripple.id)}
            <circle 
              cx={ripple.x} 
              cy={ripple.y} 
              r={ripple.r}
              fill="none"
              stroke="#60a5fa"
              stroke-width="3"
              class="click-ripple"
            />
          {/each}
          
          {#each selectedCityCoords as city (city.name)}
            <!-- Pulsing outer ring -->
            <circle 
              cx={city.x} 
              cy={city.y} 
              r={city.r + 6}
              fill="none"
              stroke="#3b82f6"
              stroke-width="2"
              class="pulse-ring"
            />
            <!-- Secondary expanding ring -->
            <circle 
              cx={city.x} 
              cy={city.y} 
              r={city.r + 3}
              fill="none"
              stroke="#93c5fd"
              stroke-width="1.5"
              class="pulse-ring-delayed"
            />
          {/each}
        </svg>
      </div>
    {/if}

    {#if hovered}
      <div 
        class="tooltip" 
        style="left: {tooltipPos.x}px; top: {tooltipPos.y}px;"
      >
        <strong>{displayCity(hovered.properties.name)}</strong>
        {#if typeof hovered.properties.femalePct === 'number'}
          <br>
          <span class="tooltip-sub">{hovered.properties.femalePct.toFixed(1)}% female streets</span>
        {/if}
      </div>
    {/if}
  </div>

  <div class="selection-readout" aria-live="polite">
    <div class="selection-title">Selected cities (max 2):</div>
    {#if $selectedCities.length === 0}
      <div class="selection-value">None</div>
    {:else}
      <div class="selection-value">{$selectedCities.map(displayCity).join(' vs ')}</div>
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
    position: relative;         /* For tooltip positioning */
  }

  .plot-wrapper {
    position: relative;
  }

  .selection-overlay {
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: none;
  }

  .tooltip {
    position: absolute;
    background: #1f2937;
    color: #f3f4f6;
    padding: 0.5rem 0.75rem;
    border-radius: 0.5rem;
    border: 1px solid #374151;
    font-size: 1rem;
    pointer-events: none;
    transform: translate(15px, -50%);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }

  .tooltip strong {
    color: #fb923c;;
    margin-bottom: 0.25rem;
    font-size: 1rem;
  }

  .tooltip-sub {
    font-size: 0.9rem;
    color: #d1d5db;
    font-weight: normal;
  }

  .selection-readout {
    margin-top: 0.75rem;
    padding: 0.75rem 1rem;
    background-color: #1f2937;
    border-radius: 0.5rem;
  }

  .selection-title {
    font-size: 0.9rem;
    color: #9ca3af;
  }

  .selection-value {
    margin-top: 0.25rem;
    color: #f3f4f6;
    text-transform: capitalize;
  }

  .slider-control { display: flex; align-items: center; gap: 0.5rem; background: #1f2937; padding: 0.5rem 1rem; border-radius: 0.25rem; border: 1px solid #374151; }
  .slider-control label { font-size: 0.9rem; font-weight: 500; }
  .slider-control input[type=range] { width: 100px; accent-color: #fb923c; cursor: pointer; }

  .pulse-ring {
    animation: pulse 2s ease-in-out infinite 0.6s;
    transform-origin: center;
    transform-box: fill-box;
  }

  .pulse-ring-delayed {
    animation: pulse 2s ease-in-out infinite 0.9s;
    transform-origin: center;
    transform-box: fill-box;
  }

  .click-ripple {
    animation: ripple 0.6s ease-out forwards;
    transform-origin: center;
  }

  @keyframes ripple {
    0% {
      r: inherit;
      opacity: 1;
      stroke-width: 3;
    }
    100% {
      r: 30;
      opacity: 0;
      stroke-width: 1;
    }
  }

  @keyframes pulse {
    0% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.6;
      transform: scale(1.12);
    }
    100% {
      opacity: 1;
      transform: scale(1);
    }
  }
</style>