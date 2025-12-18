<script>
  import data from '../Streets.json';
  import PieChart from './Categories_Piecharts.svelte';

  //Only keep lists which have gender = female
  const females = data.filter(d => d.gender === "female");

  //Unique cities
  const cities = [...new Set(females.map(d => d.lau_name))].sort();

  //User selections
  let city1 = $state('');
  let city2 = $state('');

  // --- CATEGORY CLEANING ---
  function classifyCategories(text, occ) {
    const o = (occ || "").toLowerCase();
    const t = (text || "").toLowerCase();

    const parts = o
      .split(";")
      .map(p => p.trim())
      .filter(Boolean);

    const has = kw => parts.some(p => p === kw);

    if (has("military")) return "military";
    if (has("religion")) return "religion";
    if (has("politics and government")) return "politics";
    if (has("culture, science, arts")) return "culture";
    if (has("other")) return "others";

    if (t.includes("military") || t.includes("army")) return "military";
    if (t.includes("relig")) return "religion";
    if (t.includes("politic") || t.includes("government")) return "politics";
    if (t.includes("art") || t.includes("scienc") || t.includes("culture")) return "culture";

    return "others";
  }

  //Cleaned dataset
  let categories = $derived(
    females.map(d => ({
      ...d,
      category_cleaned: classifyCategories(d.occupation_label, d.occupation_category)
    }))
  );

  //Filter datasets by city
  let filtered1 = $derived(city1 ? categories.filter(d => d.lau_name === city1) : []);
  let filtered2 = $derived(city2 ? categories.filter(d => d.lau_name === city2) : []);

  //Counts per category
  function countCategories(list) {
    const counts = {};
    for (const d of list) {
      const cat = d.category_cleaned;
      counts[cat] = (counts[cat] || 0) + 1;
    }
    return Object.entries(counts).map(([category, count]) => ({ category, count }));
  }

  let pie1 = $derived([...countCategories(filtered1)]);
  let pie2 = $derived([...countCategories(filtered2)]);

  //Computing the percentages of the different categories
  function pctMap(list) {
    const total = list.reduce((s, d) => s + d.count, 0);
    const map = {};
    for (const d of list) {
      map[d.category] = total > 0 ? (d.count / total) * 100 : 0;
    }
    return map;
  }

  let pctCity1 = $derived(pctMap(pie1));
  let pctCity2 = $derived(pctMap(pie2));

  //Most represented category
  function topCategory(pctMap) {
    const entries = Object.entries(pctMap);
    if (!entries.length) return null;
    entries.sort((a, b) => b[1] - a[1]);
    return { category: entries[0][0], pct: entries[0][1] };
  }

  let top1 = $derived(topCategory(pctCity1));
  let top2 = $derived(topCategory(pctCity2));

</script>

<!-- Main Title -->
<h1 class="main-title">Representation of streetnames that were named after females and categorized by their occupation</h1>

<!-- selectors -->
<div class="selectors">
  <div>
    <label>City 1</label>
    <select bind:value={city1}>
      <option value="">Choose…</option>
      {#each cities as c}
        <option value={c}>{c}</option>
      {/each}
    </select>
  </div>

  <div>
    <label>City 2</label>
    <select bind:value={city2}>
      <option value="">Choose…</option>
      {#each cities as c}
        <option value={c}>{c}</option>
      {/each}
    </select>
  </div>
</div>

<!-- charts -->
<div class="charts">
  <div class="chart">
    <h3>{city1 || "City 1"}</h3>

    {#if top1}
      <p class="annotation-city">
        Most represented category: <strong>{top1.category}</strong> ({top1.pct.toFixed(1)}%)
      </p>
    {/if}

    {#if pie1.length}
      <PieChart data={pie1} size={250} />
    {/if}
  </div>

  <div class="chart">
    <h3>{city2 || "City 2"}</h3>

    {#if top2}
      <p class="annotation-city">
        Most represented category: <strong>{top2.category}</strong> ({top2.pct.toFixed(1)}%)
      </p>
    {/if}

    {#if pie2.length}
      <PieChart data={pie2} size={250} />
    {/if}
  </div>
</div>

  <!-- the caption -->
  <p class="main-caption">
    Comparison of two cities based on the occupation categories of women represented
    in their streetnames. Categories are grouped into culture, politics, religion, 
    military and others. Hover over the piecharts to view detailed percentages.
  </p>

<!-- comparative summary -->
{#if city1 && city2}
  <div class="comparison-box">
    <h4>How do your chosen cities differ?</h4>

    {#each Object.keys(pctCity1) as c}
      {#if pctCity2[c] !== undefined}
        <p>
          {c} is 
          {Math.abs(pctCity1[c] - pctCity2[c]).toFixed(1)} 
          %
          {pctCity1[c] > pctCity2[c] ? "higher" : "lower"} 
          in {city1} than in {city2}.
        </p>
      {/if}
    {/each}
  </div>

  <p class="main-caption">
    {city1} shows a distribution dominated by {top1?.category || ""}, whereas {city2} 
    is characterised most strongly by {top2?.category || ""}. The differences in category 
    shares indicate how each city chooses to remember women through its street names.
  </p>
{/if}

<style>
  .main-title {
    text-align: center;
    font-size: 1.9rem;
    font-weight: 700;
    margin-bottom: 2rem;
  }

  .selectors {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-bottom: 2rem;
  }

  .charts {
    display: flex;
    justify-content: center;
    gap: 8rem;
    margin-bottom: 3rem;
  }

  .chart {
    width: 350px;
    text-align: center;
  }

  h3 {
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
  }

  .comparison-box {
  max-width: 700px;
  margin: 2rem auto;
  padding: 1.5rem;
  background: #1f2937;                 
  border: 1px solid #374151;
  border-radius: 0.5rem;
  line-height: 1.5;
  color: #e5e7eb;                    
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
}

.comparison-box h4 {
  margin-top: 0;
  margin-bottom: 0.8rem;
  color: #f3f4f6;
  font-size: 1.1rem;
}

.comparison-box p {
  font-size: 0.9rem;
  color: #d1d5db;
  margin-bottom: 0.4rem;
}

  .comparison-box h4 {
    margin-top: 0;
    margin-bottom: 0.8rem;
  }

  .main-caption {
    text-align: center;
    max-width: 750px;
    margin: 2.5rem auto;
    font-size: 0.9rem;
    color: #666;
    line-height: 1.4;
    font-style: italic;
  }
</style>
