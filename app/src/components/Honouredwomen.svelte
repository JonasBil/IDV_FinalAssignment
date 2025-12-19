<script>
  import Streets from "../Streets.json";
  import { Plot, BarY, GridY, RuleY, groupX } from "svelteplot";
  import '../Styles.css'

  // Bin size in years for the histogram
  const binSize = 10;

// Selected cities for comparison
  let selectedA = "";
  let selectedB = "";

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
  selectedA = cityOptions[0] || "";

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
        city: cityA,
        count: binCounts[binStart].a || 0
      });

      if (cityB) {
        rows.push({
          bin: `${binStart}-${binStart + binSize - 1}`,
          city: cityB,
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

// Initialize reactive variables for plot data and means
  let rows = [];
  let meanA = null;
  let meanB = null;
  let meanAllCities = null;
// Reactive updates when selected cities change
  $: rows = selectedA ? buildPlotRows(selectedA, selectedB) : [];
  $: meanA = selectedA ? meanFromYears(summary[selectedA]) : null;
  $: meanB = selectedB ? meanFromYears(summary[selectedB]) : null;
  $: meanAllCities = meanAll(summary);
</script>
<!-- Title -->
<div class="header">
  <h1>Histogram of the date of birth of women in street names in selected cities</h1>
</div>

<!-- selectors -->
<div class="controls">
  <label for="cityA">City A:</label>
  <select id="cityA" bind:value={selectedA}>
    {#each cityOptions as c}
      <option value={c}>{c}</option>
    {/each}
  </select>

  <label for="cityB">City B:</label>
  <select id="cityB" bind:value={selectedB}>
    <option value="">(none)</option>
    {#each cityOptions as c}
      <option value={c}>{c}</option>
    {/each}
  </select>
</div>

<!-- plot -->
{#if selectedA && rows.length}
  <div class="plot">
  <Plot
  height={420}
  color={{
    legend: true,
    scheme: ['#2ecc71', '#e74c3c'],   // colours to use
    domain: selectedB ? [selectedA, selectedB] : [selectedA] // map colours to city names
  }}
  x={{ label: "Birth year of women", tickRotate: -45 }}
  y={{ label: "Count (women)" }}
>
      <GridY />
      <RuleY data={[0]} />
      <BarY
      stroke="white" strokeWidth={0.8}
        {...groupX(
          { data: rows, x: "bin", y: "count", fill: "city"},
          { y: "sum" }
        )}
      />
    </Plot>
  </div>
{:else}

  <p>Select City A to show the chart.</p>
{/if}

  <!-- small summary below the chart showing means and comparison -->

  <div class="description_box" aria-live="polite">
    <p> The histogram groups birth years into 10-year bins and counts how many honoured women
      were born in each interval. This lets us compare the age cohorts represented in street names
      between cities and spot if one city honours earlier or later-born figures. </p>
    {#if selectedA}
      <p>
        {#if selectedB}
         On average, women in {selectedA} are born in {meanA ? Math.round(meanA) : '—'}, while women in {selectedB} are born in {meanB ? Math.round(meanB) : '—'}. The overall mean birth year across all cities is {meanAllCities ? Math.round(meanAllCities) : '—'}.
        {:else}
         On average, women in {selectedA} are born in {meanA ? Math.round(meanA) : '—'}. The overall mean birth year across all cities is {meanAllCities ? Math.round(meanAllCities) : '—'}. Select City B to compare.
        {/if}

        {#if selectedA && selectedB && meanA != null && meanB != null}
          {#if meanA < meanB}
            On average, {selectedA} honours earlier-born women than {selectedB}.
          {:else if meanA > meanB}
            On average, {selectedB} honours earlier-born women than {selectedA}.
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
  .controls { display: flex; gap: 12px; align-items: center; margin: 12px 0; flex-wrap: wrap; }
  .plot { width: 100%; }
</style>