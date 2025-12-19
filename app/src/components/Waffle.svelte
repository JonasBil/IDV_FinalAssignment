<script>
import {unmixed_aggregated_street_data_citizenship} from '../unmixed_aggregated_street_data_citizenship.js'
import { Plot, WaffleY, AxisX } from 'svelteplot'
import * as d3 from 'd3'
import {selectedCities} from '../stores/compareSelection.js';

// const an array of studied city names
const Cities = Array.from(new Set(unmixed_aggregated_street_data_citizenship.map(d => d.lau_name))).sort(); 

// Map-selected cities come from the `selectedCities` store (keys from `city_centers.json`).
// Dataset cities (`lau_name`) are Title Case; build a lookup so keys like `wien` map to `Wien`.
function normalizeCityKey(v) {
  return (v ?? '')
    .toString()
    .trim()
    .toLowerCase()
    .normalize('NFKD')
    .replace(/\p{Diacritic}/gu, '');
}

let cityKeyToLauName = $derived.by(() => {
  const map = new Map();
  for (const city of Cities) {
    map.set(city.toLowerCase(), city);
    map.set(normalizeCityKey(city), city);
  }
  return map;
});

let Selected_city = $derived.by(() => {
  const key = ($selectedCities ?? [])[0];
  if (!key) return null;
  return cityKeyToLauName.get(key) ?? cityKeyToLauName.get(normalizeCityKey(key)) ?? null;
});

let Selected_city2 = $derived.by(() => {
  const key = ($selectedCities ?? [])[1];
  if (!key) return null;
  return cityKeyToLauName.get(key) ?? cityKeyToLauName.get(normalizeCityKey(key)) ?? null;
});
  

// Get top 20 places of birth for the selected city
let top_20_data = $derived(
  Selected_city
    ? unmixed_aggregated_street_data_citizenship
        .filter(d => d.lau_name === Selected_city)
        .sort((a, b) => b.total_count_unmixed - a.total_count_unmixed)
        .slice(0, 20)
    : []
)


// Calculate the sum of all other places
let other_count = $derived(
  Selected_city
    ? unmixed_aggregated_street_data_citizenship
        .filter(d => d.lau_name === Selected_city)
        .sort((a, b) => b.total_count_unmixed - a.total_count_unmixed)
        .slice(20)
        .reduce((sum, d) => sum + d.total_count_unmixed, 0)
    : 0
)


let filtered_aggregated_data = $derived.by(() => {      // Add "Other" category if there are remaining records
  const data = other_count > 0 ? [...top_20_data, { country_of_citizenship_label: "Other", total_count_unmixed: other_count }]: top_20_data;
  
 const mapped_data = data.map(d => ({
    ...d,
    country_of_citizenship_label: d.country_of_citizenship_label === "NA" ? "Not Identified" : d.country_of_citizenship_label}));

  // Custom sort to move "Other" and then "Not Identified" to the end
  mapped_data.sort((a, b) => {
    const aLabel = a.country_of_citizenship_label;
    const bLabel = b.country_of_citizenship_label;

    const getScore = (label) => {
      if (label === 'Not Identified') return 2;
      if (label === 'Other') return 1;
      return 0;};

    const scoreA = getScore(aLabel);
    const scoreB = getScore(bLabel);

    if (scoreA !== scoreB) {return scoreA - scoreB;}

    // Fallback to original sort order (by count)
    return (b.total_count_unmixed || 0) - (a.total_count_unmixed || 0);});

  return mapped_data;});

// Top 3 countries (exclude helper buckets), with % based on the same total used for the waffle
let totalCount_city1 = $derived.by(() =>
  (filtered_aggregated_data ?? []).reduce((s, d) => s + (d.total_count_unmixed ?? 0), 0)
);

let top3_city1 = $derived.by(() => {
  const rows = filtered_aggregated_data ?? [];
  const total = totalCount_city1;
  if (!total || !rows.length) return [];

  return rows
    .filter((d) => d.country_of_citizenship_label !== 'Other' && d.country_of_citizenship_label !== 'Not Identified')
    .slice()
    .sort((a, b) => (b.total_count_unmixed ?? 0) - (a.total_count_unmixed ?? 0))
    .slice(0, 3)
    .map((d) => ({
      label: d.country_of_citizenship_label,
      pct: ((d.total_count_unmixed ?? 0) / total) * 100
    }));
});


// Create color scale for countries
let colorScale = $derived.by(() => {
  const countries = filtered_aggregated_data.map(d => d.country_of_citizenship_label); //mapping the labels of countries
  const colors = d3.schemeTableau10.concat(d3.schemePaired); // Combined color schemes
  
  const scale = d3.scaleOrdinal()   //making the actual colorscale
    .domain(countries)
    .range(colors);
  
  // Set "Other" to gray
  scale.unknown("#999999");
  
  return scale;});

// Build 100 waffle squares for the selected city
let waffleSquares = $derived.by(() => {
  const TOTAL_SQUARES = 100;                        //numbers of squares in waffle -> 100 so 1 square should be 1% to show relative frequencies
  const rows = filtered_aggregated_data ?? [];
  const total = rows.reduce((s, r) => s + (r.total_count_unmixed ?? 0), 0);       //total number of named streets in the selected city to calculate rel. freq
  if (total <= 0 || rows.length === 0) return [];

  let allocated = 0;
  const allocations = rows.map(r => {
    const proportion = (r.total_count_unmixed ?? 0) / total;  //calculating the relative frequency of each country and 'other'
    const n = Math.round(proportion * TOTAL_SQUARES);
    allocated += n;
    return { 
      lau_name: Selected_city, 
      label: r.country_of_citizenship_label, 
      n, 
      proportion };});

  const squares = [];                  //building array of squares for waffle chart
  allocations.forEach(a => {
    for (let i = 0; i < a.n; i++) {
      squares.push({ 
        lau_name: a.lau_name, 
        category: a.label, 
        value: 1 
      });
    }
  });

  // Fix rounding to exactly 100 squares
  let diff = TOTAL_SQUARES - allocated;
  if (diff !== 0 && allocations.length > 0) {
    const byRemainder = allocations
      .map(a => ({ 
        lau_name: a.lau_name, 
        label: a.label, 
        rem: (a.proportion * TOTAL_SQUARES) - Math.floor(a.proportion * TOTAL_SQUARES) }))
      .sort((a, b) => b.rem - a.rem);
  
    if (diff > 0) {
      let i = 0;
      while (diff > 0) {squares.push({ 
          lau_name: Selected_city, 
          category: byRemainder[i % byRemainder.length].label, 
          value: 1 });i++; diff--;}} 
    else {
      let i = byRemainder.length - 1;
      while (diff < 0 && squares.length) {
        const idx = squares.findIndex(s => 
          s.lau_name === Selected_city && 
          s.category === byRemainder[i % byRemainder.length].label);
        if (idx >= 0) squares.splice(idx, 1);
        i--; diff++;}}}
  
  return squares;});



//different colouring for each country
function getBarColor(d) {
    const label = d.country_of_citizenship_label || d.category;
    if (label === "Other") return "#999999";  // light grey
    if (label === "Not Identified" ) return "#4a4a4a";  // dark grey
    return colorScale(label);} 


// ============ Second City Data ============
// Get top 20 places of birth for the second selected city
let top_20_data_2 = $derived(
  Selected_city2
    ? unmixed_aggregated_street_data_citizenship
        .filter(d => d.lau_name === Selected_city2)
        .sort((a, b) => b.total_count_unmixed - a.total_count_unmixed)
        .slice(0, 20)
    : []
)

// Calculate the sum of all other places for city 2
let other_count_2 = $derived(
  Selected_city2
    ? unmixed_aggregated_street_data_citizenship
        .filter(d => d.lau_name === Selected_city2)
        .sort((a, b) => b.total_count_unmixed - a.total_count_unmixed)
        .slice(20)
        .reduce((sum, d) => sum + d.total_count_unmixed, 0)
    : 0
)

let filtered_aggregated_data_2 = $derived.by(() => {
  const data = other_count_2 > 0 ? [...top_20_data_2, { country_of_citizenship_label: "Other", total_count_unmixed: other_count_2 }]: top_20_data_2;
  
  const mapped_data = data.map(d => ({
    ...d,
    country_of_citizenship_label: d.country_of_citizenship_label === "NA" ? "Not Identified" : d.country_of_citizenship_label}));

  // Custom sort to move "Other" and then "Not Identified" to the end
  mapped_data.sort((a, b) => {
    const aLabel = a.country_of_citizenship_label;
    const bLabel = b.country_of_citizenship_label;

    const getScore = (label) => {
      if (label === 'Not Identified') return 2;
      if (label === 'Other') return 1;
      return 0;};

    const scoreA = getScore(aLabel);
    const scoreB = getScore(bLabel);

    if (scoreA !== scoreB) {return scoreA - scoreB;}

    return (b.total_count_unmixed || 0) - (a.total_count_unmixed || 0);});

  return mapped_data;});

let totalCount_city2 = $derived.by(() =>
  (filtered_aggregated_data_2 ?? []).reduce((s, d) => s + (d.total_count_unmixed ?? 0), 0)
);

let top3_city2 = $derived.by(() => {
  const rows = filtered_aggregated_data_2 ?? [];
  const total = totalCount_city2;
  if (!total || !rows.length) return [];

  return rows
    .filter((d) => d.country_of_citizenship_label !== 'Other' && d.country_of_citizenship_label !== 'Not Identified')
    .slice()
    .sort((a, b) => (b.total_count_unmixed ?? 0) - (a.total_count_unmixed ?? 0))
    .slice(0, 3)
    .map((d) => ({
      label: d.country_of_citizenship_label,
      pct: ((d.total_count_unmixed ?? 0) / total) * 100
    }));
});

// Create color scale for countries for city 2
let colorScale_2 = $derived.by(() => {
  const countries = filtered_aggregated_data_2.map(d => d.country_of_citizenship_label);
  const colors = d3.schemeTableau10.concat(d3.schemePaired);
  
  const scale = d3.scaleOrdinal()
    .domain(countries)
    .range(colors);
  
  scale.unknown("#999999");
  
  return scale;});

// Build 100 waffle squares for the second selected city
let waffleSquares_2 = $derived.by(() => {
  const TOTAL_SQUARES = 100;
  const rows = filtered_aggregated_data_2 ?? [];
  const total = rows.reduce((s, r) => s + (r.total_count_unmixed ?? 0), 0);
  if (total <= 0 || rows.length === 0) return [];

  let allocated = 0;
  const allocations = rows.map(r => {
    const proportion = (r.total_count_unmixed ?? 0) / total;
    const n = Math.round(proportion * TOTAL_SQUARES);
    allocated += n;
    return { 
      lau_name: Selected_city2, 
      label: r.country_of_citizenship_label, 
      n, 
      proportion };});

  const squares = [];
  allocations.forEach(a => {
    for (let i = 0; i < a.n; i++) {
      squares.push({ 
        lau_name: a.lau_name, 
        category: a.label, 
        value: 1 
      });
    }
  });

  // Fix rounding to exactly 100 squares
  let diff = TOTAL_SQUARES - allocated;
  if (diff !== 0 && allocations.length > 0) {
    const byRemainder = allocations
      .map(a => ({ 
        lau_name: a.lau_name, 
        label: a.label, 
        rem: (a.proportion * TOTAL_SQUARES) - Math.floor(a.proportion * TOTAL_SQUARES) }))
      .sort((a, b) => b.rem - a.rem);
  
    if (diff > 0) {
      let i = 0;
      while (diff > 0) {squares.push({ 
          lau_name: Selected_city2, 
          category: byRemainder[i % byRemainder.length].label, 
          value: 1 });i++; diff--;}} 
    else {
      let i = byRemainder.length - 1;
      while (diff < 0 && squares.length) {
        const idx = squares.findIndex(s => 
          s.lau_name === Selected_city2 && 
          s.category === byRemainder[i % byRemainder.length].label);
        if (idx >= 0) squares.splice(idx, 1);
        i--; diff++;}}}
  
  return squares;});

// Color function for city 2
function getBarColor_2(d) {
    const label = d.country_of_citizenship_label || d.category;
    if (label === "Other") return "#999999";
    if (label === "Not Identified" ) return "#4a4a4a";
    return colorScale_2(label);} 



</script>

<div class="charts-container">

<div class="header">
  <h1> Regional Culture found in street names</h1>
</div>

<div class="dropdown-container">
  <!-- <p>For these cities, we can also explore where the honoured women come from. This can tell you something about how a city wants to profile itself by using it's regional culture in street names. One city might tend to name more streets to former or present inhabitants, other cities might emphasize different cultural backgrounds. A waffle chart can be used to visualise the distribution by country of citizenship among the honoured women.</p> -->
  <p class="selected-cities">
    The cities that you are comparing are {Selected_city ?? '—'}{Selected_city2 ? ` and ${Selected_city2}` : ''}
  </p>
</div>

<div class="container">



<div class="facet facet-2">
  
  <div class="legend">
    {#each filtered_aggregated_data as item}
      <div class="legend-item">
        <span class="swatch" style="background-color: {getBarColor({country_of_citizenship_label: item.country_of_citizenship_label})}"></span>
        <span>{item.country_of_citizenship_label}</span>
      </div>
    {/each}
  </div>

  {#if Selected_city && Array.isArray(waffleSquares) && waffleSquares.length}
    <Plot 
      x={{ title: "City", label: "Studied City" }}
      y={{ title: "Share (100 squares = 100%)", label: "Relative Frequency, 1 square = 1%" }}
      width={600}
      height={500}
    >
      <WaffleY 
        data={waffleSquares} 
        x="lau_name" 
        y="value" 
        fill={(d) => getBarColor(d)}
      >
        {#snippet symbol({x, y, height, width, style, styleClass })}
          <g
            style={(style || '') + '; pointer-events: all;'}
            class={styleClass}
            transform={'translate(' + x + ', ' + y + ') scale(' + (width / 60.6) + ', ' + (height / 60.6) + ')'}>

            <path d="m 30.307377,14.856128 c 1.775,0 3.215,-1.43875 3.215,-3.215 0,-1.7762504 -1.44,-3.2150005 -3.215,-3.2150005 -1.775,0 -3.215,1.4387501 -3.215,3.2150005 0,1.77625 1.44,3.215 3.215,3.215"/>
            <path d="m 34.731127,21.608628 2.4975,9.325001 2.41125,0 -1.94375,-11.030001 c -0.30125,-1.69625 -1.56375,-3.145 -3.345,-3.5875 -1.295,-0.3225 -2.65,-0.49625 -4.04375,-0.49625 -1.39375,0 -2.748751,0.17375 -4.043751,0.49625 -1.78125,0.4425 -3.045,1.89125 -3.345,3.5875 l -1.94375,11.030001 2.41125,0 2.4975,-9.325001 1.005,3.74875 c -2.3075,3.431251 -3.655,7.561251 -3.655,12.007501 l 4.19125,0 1.265001,14.458751 3.235,0 1.26375,-14.458751 4.1925,0 c 0,-4.44625 -1.34625,-8.5775 -3.655,-12.008751 l 1.005,-3.7475"/>
          </g>
        {/snippet}
      </WaffleY>
      <AxisX tickFontSize={15} />
    </Plot>
  {:else}
    <p>{Selected_city ? `No data available for ${Selected_city}` : 'Select a city on the map to show data.'}</p>
  {/if}
</div>

<div class="facet facet-3">
 
  <div class="legend">
    {#each filtered_aggregated_data_2 as item}
      <div class="legend-item">
        <span class="swatch" style="background-color: {getBarColor_2({country_of_citizenship_label: item.country_of_citizenship_label})}"></span>
        <span>{item.country_of_citizenship_label}</span>
      </div>
    {/each}
  </div>

  {#if Selected_city2 && Array.isArray(waffleSquares_2) && waffleSquares_2.length}
    <Plot 
      x={{ title: "City", label: "Studied City" }}
      y={{ title: "Share (100 squares = 100%)", label: "Relative Frequency, 1 square = 1%" }}
      width={600}
      height={500}
    >
      <WaffleY 
        data={waffleSquares_2} 
        x="lau_name" 
        y="value" 
        fill={(d) => getBarColor_2(d)}
        
      >
        {#snippet symbol({ x, y, height, width, style, styleClass })}
          <g
            style={(style || '') + '; pointer-events: all;'}
            class={styleClass}
            transform={'translate(' + x + ', ' + y + ') scale(' + (width / 60.6) + ', ' + (height / 60.6) + ')'}>
            
           
            <path d="m 30.307377,14.856128 c 1.775,0 3.215,-1.43875 3.215,-3.215 0,-1.7762504 -1.44,-3.2150005 -3.215,-3.2150005 -1.775,0 -3.215,1.4387501 -3.215,3.2150005 0,1.77625 1.44,3.215 3.215,3.215"/>
            <path d="m 34.731127,21.608628 2.4975,9.325001 2.41125,0 -1.94375,-11.030001 c -0.30125,-1.69625 -1.56375,-3.145 -3.345,-3.5875 -1.295,-0.3225 -2.65,-0.49625 -4.04375,-0.49625 -1.39375,0 -2.748751,0.17375 -4.043751,0.49625 -1.78125,0.4425 -3.045,1.89125 -3.345,3.5875 l -1.94375,11.030001 2.41125,0 2.4975,-9.325001 1.005,3.74875 c -2.3075,3.431251 -3.655,7.561251 -3.655,12.007501 l 4.19125,0 1.265001,14.458751 3.235,0 1.26375,-14.458751 4.1925,0 c 0,-4.44625 -1.34625,-8.5775 -3.655,-12.008751 l 1.005,-3.7475"/>
          </g>
        {/snippet}
      </WaffleY>
      <AxisX tickFontSize={15} />
    </Plot>
  {:else}
    <p>{Selected_city2 ? `No data available for ${Selected_city2}` : 'Select a second city on the map to compare.'}</p>
  {/if}
</div>

</div>

<!-- Shared text box for both waffle charts (edit content as desired) -->
<div class="description_box waffle-summary">
  <p>
    For these cities, we can also explore where the honoured women come from. This can tell you something about how a city wants to profile itself by using it's regional culture in street names. One city might tend to name more streets to former or present inhabitants, other cities might emphasize different cultural backgrounds. A waffle chart can be used to visualise the distribution by country of citizenship among the honoured women.
    Top 3 countries of citizenship for the honoured women in street names:
  </p>
  <p>
    {Selected_city ?? 'City A'}:
    {#if top3_city1.length}
      {#each top3_city1 as t, i (t.label)}
        <span class="top3-item"><u>{t.label}</u> ({t.pct.toFixed(1)}%){#if i < top3_city1.length - 1}, {/if}</span>
      {/each}
    {:else}
      —
    {/if}
  </p>
  <p>
    {Selected_city2 ?? 'City B'}:
    {#if top3_city2.length}
      {#each top3_city2 as t, i (t.label)}
        <span class="top3-item"><u>{t.label}</u> ({t.pct.toFixed(1)}%){#if i < top3_city2.length - 1}, {/if}</span>
      {/each}
    {:else}
      —
    {/if}
  </p>
</div>
</div>

<style>

.dropdown-container {
  margin-bottom: 20px;
  margin-left: 20px;
}

.dropdown-wrapper {
  display: flex;
  gap: 420px;
  align-items: center;
}

.selected-cities {
  margin-top: 6px;
}

/*the parent*/
.container { width: 1300px; display: flex;     
    gap: 28px;            
    align-items: flex-start; font-family: "Nunito", sans-serif;font-weight: 400}

/*the children*/
.facet{width: 49%; display:inline-block;margin-left: 20px; }


h1,h2 {
  font-family: "Nunito", sans-serif;
  font-optical-sizing: auto;
  font-weight: 600;
  font-style: normal;}

h2 {font-weight: normal; font-size: 1em; color: #545454;}
.description {font-weight: normal; font-size: 0.9em; color: #545454;}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 12px; 
  font-size: 0.75em;
  max-width: 600px;}

.legend-item {
  display:flex;
  align-items:center;
  font-size: 0.9em;
  color: #aeadadff; margin-right: 8px;}

.swatch {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-right: 4px;
  border-radius: 2px;}


.waffle-summary {
  max-width: 1300px;
  margin-left: 20px;
}

.top3-item u {
  text-underline-offset: 2px;
}

/* WaffleY handles layout; keep legend styles above */


</style>
