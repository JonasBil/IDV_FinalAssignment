<script>
  import { onMount, onDestroy } from 'svelte';
  import {Chart, BarElement,BarController,CategoryScale,LinearScale,Tooltip,Legend} from 'chart.js';

  Chart.register(BarElement, BarController, CategoryScale, LinearScale, Tooltip, Legend); //

  let canvasEl; 
  let chart;
  let summary = {};
  let cityOptions = [];
  let selectedA = null;
  let selectedB = null;
  let meanA = null;
  let meanB = null;
  let meanAll = null;
  let error = null;

  // Try to extract a 4-digit year from various date_of_birth formats
  function extractYearFromDob(dob) {
    if (!dob) return null;
    const parsed = new Date(dob);
    if (!isNaN(parsed.getTime())) return parsed.getFullYear();
    const m = String(dob).match(/(1[6-9]\d{2}|20\d{2})/);
    return m ? Number(m[0]) : null;
  }

  // Build { city: { year: count } } from raw street rows
  function buildSummaryFromRows(rows) {
    const out = Object.create(null);
// only account for women in the streetnames (lau_name)
    for (const r of rows) {
      try {
        const gender = r.gender && String(r.gender).toLowerCase();
        if (!gender || !gender.startsWith('f')) continue;

        const city = (r.lau_name || '').trim();
        if (!city) continue;

        const year = extractYearFromDob(r.date_of_birth);
        if (!year) continue;

        if (!out[city]) out[city] = Object.create(null);
        out[city][year] = (out[city][year] || 0) + 1;
      } catch {
        // ignore bad rows
      }
    }

    return out;
  }

  // Helper: fetch JSON, return null on any error
  async function fetchJson(url) {
    try {
      const res = await fetch(url);
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;}}

  // Load summary.json, or derives it from Streets.json as a fallback
  async function loadSummary() {
    try {
      let obj = await fetchJson('/summary.json');
      if (obj && Object.keys(obj).length) {
        // Pre-computed summary structure
        summary = obj;
      } else {
        // Try to build summary from raw streets files
        const paths = ['/src/Streets.json', '/Streets.json', '/public/Streets.json'];
        for (const p of paths) {
          const rows = await fetchJson(p);
          if (Array.isArray(rows) && rows.length) {
            summary = buildSummaryFromRows(rows);
            break;}}
        if (!summary || !Object.keys(summary).length) summary = obj || {};}

        // Prepare city options for the select dropdowns
      cityOptions = Object.keys(summary).sort();

      renderChart();
    } catch (e) {
      console.error('Failed to load data', e);
      error = e.message || String(e); }
}

  // Convert per-year data to binned histogram data for two cities
  function getChartDataForCities(a, b) {
    const normalize = (obj) => {
      if (!obj) return { years: {}, total: 0, known: 0, unknown: 0, nullDob: 0 };

      // Case 1: pre-aggregated object with .years, .total, ...
      if (obj.years) {
        return {
          years: obj.years || {},
          total: obj.total || 0,
          known: obj.known || 0,
          unknown: obj.unknown || 0,
          nullDob: obj.nullDob || 0
        };
      }

      // Case 2: plain { year: count } object
      const years = Object.create(null);
      let sum = 0;
      for (const key of Object.keys(obj)) {
        const n = Number(obj[key] || 0);
        years[key] = n;
        sum += n;
      }
      return { years, total: sum, known: sum, unknown: 0, nullDob: 0 };
    };
// normalize data for both cities
    const ainfo = normalize(summary[a]);
    const binfo = normalize(summary[b]);
// binning
    const binCounts = Object.create(null);
    const allYears = new Set(
      [...Object.keys(ainfo.years || {}), ...Object.keys(binfo.years || {})].map(Number)
    );
// aggregate counts into bins
    for (const y of allYears) {
      if (isNaN(y)) continue;
      const binStart = Math.floor(y / binSize) * binSize;
      if (!binCounts[binStart]) binCounts[binStart] = { a: 0, b: 0 };
      binCounts[binStart].a += Number(ainfo.years[y] || 0);
      binCounts[binStart].b += Number(binfo.years[y] || 0);}

    const sortedBins = Object.keys(binCounts).map(Number).sort((x, y) => x - y);
    const labels = sortedBins.map((b) => `${b}-${b + binSize - 1}`);
    const dataA = sortedBins.map((b) => binCounts[b].a || 0);
    const dataB = sortedBins.map((b) => binCounts[b].b || 0);

    return { labels, dataA, dataB, statsA: ainfo, statsB: binfo };}

  // Create / update stacked bar chart in the canvas
  function renderChart() {
    if (!canvasEl || !summary || !selectedA) return;

  const { labels, dataA, dataB, statsA, statsB } = getChartDataForCities(selectedA, selectedB);

    if (chart) chart.destroy();

    const datasets = [];
// Dataset for city A
    if (selectedA) {
      datasets.push({
        label: selectedA,
        data: dataA,
        backgroundColor: 'rgba(255,205,86,0.95)',
        borderColor: '#ffffff',
        borderWidth: 2,
        borderSkipped: false,
        hoverBackgroundColor: 'rgba(255,205,86,1)',
        hoverBorderColor: '#ffffff'});}

// Dataset for city B
    if (selectedB) {
      datasets.push({
        label: selectedB,
        data: dataB,
        backgroundColor: 'rgba(54,162,235,0.95)',
        borderColor: '#ffffff',
        borderWidth: 2,
        borderSkipped: false,
        hoverBackgroundColor: 'rgba(54,162,235,1)',
        hoverBorderColor: '#ffffff'
      });
    }
// Create the Chart.js bar chart
    chart = new Chart(canvasEl.getContext('2d'), {
      type: 'bar',
      data: { labels, datasets },
      options: {
        responsive: true,
        plugins: {
          tooltip: {
            enabled: true,
            mode: 'index',
            intersect: false,
            callbacks: {
              label(context) {
                const v = context.parsed.y;
                return `${context.dataset.label}: ${
                  Number.isInteger(v) ? v : Math.round(v)}`;}}},
          legend: { position: 'top' }
        },
        scales: {
          x: {
            stacked: true,
            title: { display: true, text: 'Birth year' }
          },
          y: {
            stacked: true,
            beginAtZero: true,
            title: { display: true, text: 'Count (women)' },
            ticks: {
              stepSize: 1,
              callback(value) {
                const v = Number(value);
                return Number.isInteger(v) ? v : Math.round(v);}}}}}});

    // compute and expose means for the UI below the chart
    meanA = computeMeanFromStats(statsA);
    meanB = computeMeanFromStats(statsB);
    meanAll = computeMeanFromSummary(summary);
  }

  // Compute weighted mean birth year from normalized stats
  function computeMeanFromStats(info) {
    if (!info || !info.years) return null;
    let total = 0;
    let count = 0;
    for (const k of Object.keys(info.years)) {
      const y = Number(k);
      const n = Number(info.years[k] || 0);
      if (!isFinite(y) || isNaN(n) || n <= 0) continue;
      total += y * n;
      count += n;
    }
    return count ? total / count : null;
  }
  // Compute weighted mean birth year across all cities in `summary`.
  function computeMeanFromSummary(sumObj) {
    if (!sumObj) return null;
    let total = 0;
    let count = 0;
    for (const city of Object.keys(sumObj)) {
      const obj = sumObj[city] || {};

  // object can be { years: {...}, ... } or plain { year: count }
      const years = obj.years || obj;
      if (!years) continue;
      for (const k of Object.keys(years)) {
        const y = Number(k);
        const n = Number(years[k] || 0);
        if (!isFinite(y) || isNaN(n) || n <= 0) continue;
        total += y * n;
        count += n;}}
    return count ? total / count : null;}

  // Return total count of women for a given city in the summary
  function getTotalForCity(city) {
    if (!city || !summary) return 0;
    const obj = summary[city];
    if (!obj) return 0;
    if (obj.total) return Number(obj.total) || 0;
    const years = obj.years || obj;
    let sum = 0;
    for (const k of Object.keys(years || {})) {
      sum += Number(years[k] || 0);
    }
    return sum;
  }

  // Load data once the component is created 
  onMount(loadSummary);

  // Clean up chart 
  onDestroy(() => {
    if (chart) chart.destroy();
  });

</script>

<h1 class="main-title"> Birth year of honoured women in street names</h1>
<h2 class="subtitle">  The histogram groups birth years into 10-year bins and counts how many honoured women
      were born in each interval. This lets us compare the age cohorts represented in street names
      between cities and spot if one city honours earlier or later-born figures. </h2> 

  <div class="controls">  <!-- labels for the selectors -->
    <label for="cityA">City A:</label>
    <select id="cityA" bind:value={selectedA} on:change={renderChart}>
      {#each cityOptions as c}
        <option value={c}>{c}</option>
      {/each}
    </select>
<!-- second selector -->
    <label for="cityB">City B:</label>
    <select id="cityB" bind:value={selectedB} on:change={renderChart}>
      <option value="">(none)</option>
      {#each cityOptions as c}
        <option value={c}>{c}</option>
      {/each}
    </select>
  </div>

<!-- layout: left explanation | chart | right city numbers -->
<div class="chart-row">
  <div class="explain-left">
    <h3>What this plot shows</h3>
  </div>

  <div class="chart-area">
    <canvas bind:this={canvasEl}></canvas>
   
  </div>

  <div class="explain-right">
    <h3>Quick summary</h3>
    {#if selectedA && selectedB}
      <p>
        {selectedA} has a mean birth year of {meanA ? Math.round(meanA) : '—'}, while {selectedB} has a mean birth year of {meanB ? Math.round(meanB) : '—'}. The overall mean across all cities is {meanAll ? Math.round(meanAll) : '—'}.
      </p>
      {#if meanA && meanB}
        {#if meanA < meanB}
          <p>On average, {selectedA} honours earlier-born women than {selectedB}.</p>
        {:else if meanA > meanB}
          <p>On average, {selectedB} honours earlier-born women than {selectedA}.</p>
        {:else}
          <p>Both cities have the same mean birth year.</p>
        {/if}
      {/if}

    {:else if selectedA}
      <p>{selectedA} (n={getTotalForCity(selectedA)}) has a mean birth year of {meanA ? Math.round(meanA) : '—'}. The overall mean across all cities is {meanAll ? Math.round(meanAll) : '—'}. Select City B to compare.</p>

    {:else}
      <p>Select City A to see its mean birth year and total; pick City B to compare. Overall mean across all cities is {meanAll ? Math.round(meanAll) : '—'}.</p>
    {/if}
  </div>
</div>
 

<style>
    .main-title {
    text-align: center;
    font-size: 1.9rem;
    font-weight: 700;
    margin-bottom: 2rem;
  }

  .container {
    max-width: 1000px;
    margin: 1.5rem auto;
    font-family: system-ui, sans-serif;
    text-align: center;
  }
  .controls {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 12px;
  }
  canvas {
    width: 100%;
    height: 420px;
  }
  .chart-row {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    margin-top: 1rem;
  }
  .explain-left, .explain-right {
    width: 22%;
    background: #f8fafc;
    color: #111827;
    padding: 0.75rem;
    border-radius: 8px;
    font-size: 0.95rem;
    line-height: 1.4;
  }
  .chart-area { flex: 1 1 auto; }
  /* place mean text left-aligned under the graph and remove bold styling */
  .means {
    margin-top: 0.5rem;
    font-size: 0.95rem;
    color: #222;
    width: 100%;
    display: block;
    text-align: left;
    padding-left: 0.5rem; /* small inset from the container edge */
  }
  .means strong { font-weight: normal; }
</style>
