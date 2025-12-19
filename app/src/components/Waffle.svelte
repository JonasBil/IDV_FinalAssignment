<script>
import {unmixed_aggregated_street_data_citizenship} from '../unmixed_aggregated_street_data_citizenship.js'
import { Plot, WaffleY, AxisX } from 'svelteplot'
import * as d3 from 'd3'
import WaffleMask from '../Figures/waffle-mask.svg'; // Import SVG as raw text

// const an array of studied city names
const Cities = Array.from(new Set(unmixed_aggregated_street_data_citizenship.map(d => d.lau_name))).sort(); 
// state and function to handle city selection
let Selected_city = $state("Wien")
let Selected_city2 = $state("Wien")
function onSelectCity(event) {
  Selected_city = event.target.value;}
  

// Get top 20 places of birth for the selected city
let top_20_data = $derived(unmixed_aggregated_street_data_citizenship.filter(d => d.lau_name === Selected_city).sort((a, b) => b.total_count_unmixed - a.total_count_unmixed).slice(0, 20))  


// Calculate the sum of all other places
let other_count = $derived(unmixed_aggregated_street_data_citizenship
  .filter(d => d.lau_name === Selected_city)
  .sort((a, b) => b.total_count_unmixed - a.total_count_unmixed)
  .slice(20)
  .reduce((sum, d) => sum + d.total_count_unmixed, 0))


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
let top_20_data_2 = $derived(unmixed_aggregated_street_data_citizenship.filter(d => d.lau_name === Selected_city2).sort((a, b) => b.total_count_unmixed - a.total_count_unmixed).slice(0, 20))  

// Calculate the sum of all other places for city 2
let other_count_2 = $derived(unmixed_aggregated_street_data_citizenship
  .filter(d => d.lau_name === Selected_city2)
  .sort((a, b) => b.total_count_unmixed - a.total_count_unmixed)
  .slice(20)
  .reduce((sum, d) => sum + d.total_count_unmixed, 0))

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



<h1> Regional Culture found in street names</h1>

<div class="dropdown-container">
  <p>Select two cities to compare the countries of citizenship of people who have streets named after them.</p>
  <div class="dropdown-wrapper">
    <select class="dropdownmenu" bind:value={Selected_city} id="city-select">
      {#each Cities as city}
        <option value={city}>
          {city}
        </option>
      {/each}
    </select>
    <select class="dropdownmenu" bind:value={Selected_city2} id="city-select-2">
      {#each Cities as city}
        <option value={city}>
          {city}
        </option>
      {/each}
    </select>
  </div>
</div>

<div class="container">



<div class="facet facet-2">
  <!-- Select a city to inspect: <select class ="dropdownmenu"  bind:value={Selected_city} id="city-select">
      {#each Cities as city}
        <option value={city}>
          {city}
        </option>
      {/each}
	  </select> -->
  <!-- <h2> Waffle chart showing the countries of citizenship of people who have streets named after them in {Selected_city} </h2>
  <h3 class='description' > Top 20 Citizenships found by researchers include: </h3> -->

  <div class="legend">
    {#each filtered_aggregated_data as item}
      <div class="legend-item">
        <span class="swatch" style="background-color: {getBarColor({country_of_citizenship_label: item.country_of_citizenship_label})}"></span>
        <span>{item.country_of_citizenship_label}</span>
      </div>
    {/each}
  </div>

  {#if Array.isArray(waffleSquares) && waffleSquares.length}
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
    <p>No data available for {Selected_city}</p>
  {/if}
</div>

<div class="facet facet-3">
  <!-- Select a city to inspect: <select class ="dropdownmenu"  bind:value={Selected_city2} id="city-select-2">
      {#each Cities as city}
        <option value={city}>
          {city}
        </option>
      {/each}
	  </select> -->
  <!-- <h2> Waffle chart showing the countries of citizenship of people who have streets named after them in {Selected_city2} </h2>
   <h3 class='description' > Top 20 Citizenships found by researchers include: </h3> -->

  <div class="legend">
    {#each filtered_aggregated_data_2 as item}
      <div class="legend-item">
        <span class="swatch" style="background-color: {getBarColor_2({country_of_citizenship_label: item.country_of_citizenship_label})}"></span>
        <span>{item.country_of_citizenship_label}</span>
      </div>
    {/each}
  </div>

  {#if Array.isArray(waffleSquares_2) && waffleSquares_2.length}
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
    <p>No data available for {Selected_city2}</p>
  {/if}
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

/*the parent*/
.container { width: 1300px; display: flex;     
    gap: 28px;            
    align-items: flex-start; font-family: "Nunito", sans-serif;font-weight: 400}

/*the children*/
.facet{width: 49%; display:inline-block;margin-left: 20px; }

.dropdownmenu {
  margin-bottom: 5px;
  padding: 5px;
  font-size: 0.8em;}


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

/* WaffleY handles layout; keep legend styles above */


</style>
