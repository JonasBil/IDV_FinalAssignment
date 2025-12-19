<script>
  import { Plot, Geo } from 'svelteplot';
  import { geoMercator } from 'd3-geo';
  import cityData from '../city_centers.json';
  import { selectedCities } from '../stores/compareSelection.js';
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
  let moved = false;
  let hovered = $state(null);

  let femalePctByCity = $state({});
  let streetsLoading = $state(false);

  const cityKeySet = new Set(Object.keys(cityData));
  const CITY_ALIASES = {
    // Common diacritics/English variants
    'münchen': 'munchen',
    'munich': 'munchen',
    'athen': 'athene',
    'athens': 'athene',
    'gdańsk': 'gdansk',
    'gdansk': 'gdansk',
    'łódź': 'łodz',
    'lodz': 'łodz',
    'kobenhavn': 'københavn'
  };

  function toCityKey(name) {
    const raw = (name ?? '').toString().trim().toLowerCase();
    if (cityKeySet.has(raw)) return raw;

    const directAlias = CITY_ALIASES[raw];
    if (directAlias && cityKeySet.has(directAlias)) return directAlias;

    const stripped = raw.normalize('NFKD').replace(/\p{Diacritic}/gu, '');
    if (cityKeySet.has(stripped)) return stripped;

    const strippedAlias = CITY_ALIASES[stripped];
    if (strippedAlias && cityKeySet.has(strippedAlias)) return strippedAlias;

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

    const cacheKey = 'femalePctByCity_fromStreets_v1';
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

  async function getEuropeData() {
    const response = await fetch('https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson');
    europe = await response.json();
    fitMap(europe);
  }

  function handleMouseMove(e) {
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

    if (closest?.properties?.name) selectedCities.toggle(closest.properties.name);
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
    const s = (name ?? '').toString();
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
  }

</script>

<div class="visualization-container">
  <div class="header">
    <h1>
      Map of Europe
      {#if hovered}
        <span class="hovered-city">: {hovered.properties.name}</span>
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
      <Plot {projection} {width} {height}>
        <Geo data={europe.features} stroke="white" fill="#374151" />
        <Geo data={cities.features} r={(d) => radiusForPct(d?.properties?.femalePct)} fill="#fb923c" />
      </Plot>
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
  }

  .hovered-city {
    color: #fb923c;
    text-transform: capitalize;
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
</style>