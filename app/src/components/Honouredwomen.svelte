<script>
  import Streets from "../Streets.json";
  import { Plot, BarY, GridY, RuleY, groupX } from "svelteplot";
  import { selectedCities } from "../stores/compareSelection.js";
  import '../Styles.css'
  import { CITY_KEY_TO_LAU, displayCityName, normalizeCityKey } from '../cityMappings.js';
  import CityDropdown from './CityDropdown.svelte';

  // Bin size in years for the histogram
  const binSize = 10;

  // Selected cities for comparison (driven by MapSelection via store)

// Extract year from date_of_birth field
  function extractYearFromDob(dob) {
    if (!dob) return null;
// Try to parse as a date first
    const parsed = new Date(dob);
    if (!isNaN(parsed.getTime())) return parsed.getFullYear();
    const m = String(dob).match(/(1[6-9]\d{2}|20\d{2})/);
    return m ? Number(m[0]) : null;}

  // Build: { city: { year: count } } for women only
  function buildSummary(rows) {
    const out = Object.create(null);

    for (const r of rows) {
      const gender = r.gender && String(r.gender).toLowerCase();
      if (!gender || !gender.startsWith("f")) continue;

      const city = (r.lau_name || "").trim();
      if (!city) continue;

      const year = extractYearFromDob(r.date_of_birth);
      if (!year) continue;

      out[city] ??= Object.create(null);
      out[city][year] = (out[city][year] || 0) + 1;
    }
    return out;}

  const summary = buildSummary(Streets);

  const cityOptions = Object.keys(summary).sort();

  // colour scheme for cities (kept in sync with the Plot `color.scheme` below)
  const colorScheme = ['#2ecc71', '#e74c3c', '#3498db', '#f39c12'];

  const cityKeyToSummaryCity = (() => {
    const map = new Map();
    // First add explicit mappings
    for (const [key, lau] of Object.entries(CITY_KEY_TO_LAU)) {
      map.set(key, lau);
      map.set(normalizeCityKey(key), lau);
    }
    // Then add automatic mappings from dataset
    for (const city of cityOptions) {
      const lower = city.toLowerCase();
      const normalized = normalizeCityKey(city);
      if (!map.has(lower)) map.set(lower, city);
      if (!map.has(normalized)) map.set(normalized, city);
    }
    return map;
  })();

  const selectedKeys = $derived($selectedCities || []);
  const selectedA = $derived(cityKeyToSummaryCity.get(normalizeCityKey(selectedKeys[0])) ?? cityKeyToSummaryCity.get(selectedKeys[0]) ?? "");
  const selectedB = $derived(cityKeyToSummaryCity.get(normalizeCityKey(selectedKeys[1])) ?? cityKeyToSummaryCity.get(selectedKeys[1]) ?? "");

  // reactive domain/map using the project's $derived helper
  const colorDomain = $derived(selectedB ? [displayCityName(selectedA), displayCityName(selectedB)] : [displayCityName(selectedA)]);
  const colorMap = $derived((() => {
    const dom = colorDomain || [];
    return Object.fromEntries(dom.map((c, i) => [c, colorScheme[i % colorScheme.length]]));
  })());

  function buildPlotRows(cityA, cityB) {
    const yearsA = summary[cityA] || {};
    const yearsB = (cityB && summary[cityB]) || {};

    const binCounts = Object.create(null);
    const allYears = new Set([
      ...Object.keys(yearsA).map(Number),
      ...Object.keys(yearsB).map(Number)
    ]);

    for (const y of allYears) {
      if (!Number.isFinite(y)) continue;
      const binStart = Math.floor(y / binSize) * binSize;
      binCounts[binStart] ??= { a: 0, b: 0 };
      binCounts[binStart].a += Number(yearsA[y] || 0);
      binCounts[binStart].b += Number(yearsB[y] || 0);
    }
// Sort bins
    const sortedBins = Object.keys(binCounts).map(Number).sort((x, y) => x - y);
// Build rows for plotting
    const rows = [];
    for (const binStart of sortedBins) {
      rows.push({
        bin: `${binStart}-${binStart + binSize - 1}`,
        city: displayCityName(cityA),
        count: binCounts[binStart].a || 0
      });

      if (cityB) {
        rows.push({
          bin: `${binStart}-${binStart + binSize - 1}`,
          city: displayCityName(cityB),
          count: binCounts[binStart].b || 0
        });
      }
    }
    return rows;
  }
// Calculate mean birth year from years object
  function meanFromYears(yearsObj) {
    let total = 0;
    let count = 0;
    for (const k of Object.keys(yearsObj || {})) {
      const y = Number(k);
      const n = Number(yearsObj[k] || 0);
      if (!Number.isFinite(y) || n <= 0) continue;
      total += y * n;
      count += n;
    }
    return count ? total / count : null;
  }
// Calculate mean birth year across all cities
  function meanAll(summaryObj) {
    let total = 0;
    let count = 0;
    for (const city of Object.keys(summaryObj || {})) {
      const years = summaryObj[city] || {};
      for (const k of Object.keys(years)) {
        const y = Number(k);
        const n = Number(years[k] || 0);
        if (!Number.isFinite(y) || n <= 0) continue;
        total += y * n;
        count += n;
      }
    }
    return count ? total / count : null;
  }

  // Derived values (runes mode)
  const rows = $derived(selectedA ? buildPlotRows(selectedA, selectedB) : []);
  const meanA = $derived(selectedA ? meanFromYears(summary[selectedA]) : null);
  const meanB = $derived(selectedB ? meanFromYears(summary[selectedB]) : null);
  const meanAllCities = meanAll(summary);

  // Hover tooltip for bars
  let plotWrap;
  let hoveredBin = $state(null);
  let hoverPos = $state({ x: 0, y: 0 });

  const countsByBin = $derived((() => {
    const m = Object.create(null);
    for (const r of rows) {
      if (!r?.bin) continue;
      m[r.bin] ??= Object.create(null);
      m[r.bin][r.city] = r.count;
    }
    return m;
  })());

  function updateHover(event, datum) {
    hoveredBin = datum?.bin ?? null;
    if (!plotWrap) return;
    const r = plotWrap.getBoundingClientRect();
    hoverPos = {
      x: event.clientX - r.left + 10,
      y: event.clientY - r.top + 10
    };
  }

  function clearHover() {
    hoveredBin = null;
  }
</script>
<!-- Title -->
<div class="section-header">
  <h1>Histogram of the date of birth of women in street names in selected cities</h1>
  <CityDropdown />
</div>

<!-- Main cart component -->
<div class= "charts-container"> 
<!-- selection (from map) -->

<!-- plot -->
{#if selectedA && rows.length}
  <div class="plot" bind:this={plotWrap}>
    {#if hoveredBin}
      <div class="bar-tooltip" style={`left:${hoverPos.x}px; top:${hoverPos.y}px;`}>
        <div><strong>Count (women)</strong></div>

        <div>
          {displayCityName(selectedA)}: {countsByBin?.[hoveredBin]?.[displayCityName(selectedA)] ?? 0}
        </div>

        {#if selectedB}
          <div>
            {displayCityName(selectedB)}: {countsByBin?.[hoveredBin]?.[displayCityName(selectedB)] ?? 0}
          </div>
        {/if}
      </div>
    {/if}
  <Plot
  height={420}
  color={{
    legend: true,
    scheme: ['#2ecc71', '#e74c3c'],   // colours to use
    domain: selectedB ? [displayCityName(selectedA), displayCityName(selectedB)] : [displayCityName(selectedA)] // map colours to city names
  }}
  x={{ label: "Birth year of women", tickRotate: -45 }}
  y={{ label: "Count (women)" }}
>
      <GridY />
      <RuleY data={[0]} />
      <BarY
      stroke="white" strokeWidth={0.8}
      onmouseover={updateHover}
      onmousemove={updateHover}
      onmouseleave={clearHover}
        {...groupX(
          { data: rows, x: "bin", y: "count", fill: "city"},
          { y: "sum" }
        )}
      />
    </Plot>
  </div>
{:else}

  <p>Select City A on the map to show the chart.</p>
{/if}
</div>


<!-- small summary below the chart showing means and comparison -->
  <div class="description_box" aria-live="polite">
    <p> The histogram groups birth years into 10-year bins and counts how many honoured women
      were born in each interval. This lets us compare the age cohorts represented in street names
      between cities and spot if one city honours earlier or later-born figures. </p>
    {#if selectedA}
      <p>
        {#if selectedB}
         On average, women in <strong style="color: {colorMap[displayCityName(selectedA)] || 'currentColor'}">{displayCityName(selectedA)}</strong> are born in {meanA ? Math.round(meanA) : '—'}, while women in <strong style="color: {colorMap[displayCityName(selectedB)] || 'currentColor'}">{displayCityName(selectedB)}</strong> are born in {meanB ? Math.round(meanB) : '—'}. The overall mean birth year across all cities is {meanAllCities ? Math.round(meanAllCities) : '—'}.
        {:else}
         On average, women in <strong style="color: {colorMap[displayCityName(selectedA)] || 'currentColor'}">{displayCityName(selectedA)}</strong> are born in {meanA ? Math.round(meanA) : '—'}. The overall mean birth year across all cities is {meanAllCities ? Math.round(meanAllCities) : '—'}. Select City B to compare.
        {/if}

        {#if selectedA && selectedB && meanA != null && meanB != null}
          {#if meanA < meanB}
            On average, <strong style="color: {colorMap[displayCityName(selectedA)] || 'currentColor'}">{displayCityName(selectedA)}</strong> honours earlier-born women than <strong style="color: {colorMap[displayCityName(selectedB)] || 'currentColor'}">{displayCityName(selectedB)}</strong>.
          {:else if meanA > meanB}
            On average, <strong style="color: {colorMap[displayCityName(selectedB)] || 'currentColor'}">{displayCityName(selectedB)}</strong> honours earlier-born women than <strong style="color: {colorMap[displayCityName(selectedA)] || 'currentColor'}">{displayCityName(selectedA)}</strong>.
          {:else}
            Both cities have the same mean birth year.
          {/if}
        {/if}
      </p>
    {:else}
      <p>Select City A to see mean birth years and comparisons.</p>
    {/if}
  </div>
<style>
    .section-header {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
    }

    .section-header h1 {
      margin: 0;
    }

    .selectors {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-bottom: 2rem;
  }
  .plot { width: 100%; position: relative; }

  .bar-tooltip {
    position: absolute;
    transform: translate(0, 0);
    background: rgba(20, 28, 38, 0.95);
    color: #eaeaea;
    padding: 0.45rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    pointer-events: none;
    z-index: 20;
    backdrop-filter: blur(6px);
    white-space: nowrap;
  }
</style>