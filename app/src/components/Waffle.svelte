<script>
import {unmixed_aggregated_street_data_citizenship} from '../unmixed_aggregated_street_data_citizenship.js'
import { Plot, BarY } from 'svelteplot'
import '../Styles.css'
import * as d3 from 'd3'

// const an array of studied city names
const Cities = Array.from(new Set(unmixed_aggregated_street_data_citizenship.map(d => d.lau_name))).sort(); 
// state and function to handle city selection
let Selected_city = $state("Wien")
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


</script>



<h1> Regional Culture found in street names</h1>
<div class="container">
  
<div class=charts-container>
    <div class="facet facet-2">
    Select a city to inspect: <select class ="dropdownmenu"  bind:value={Selected_city} id="city-select">
        {#each Cities as city}
            <option value={city}>
            {city}
            </option>
        {/each}
        </select>
    <h2> Waffle chart showing the countries of citizenship of people who have streets named after them in {Selected_city} </h2>
    <h3 class='description' > Top 20 Citizenships found by researchers include: </h3>

    <div class="legend">
        {#each filtered_aggregated_data as item}
        <div class="legend-item">
            <span class="swatch" style="background-color: {getBarColor({country_of_citizenship_label: item.country_of_citizenship_label})}"></span>
            <span>{item.country_of_citizenship_label}</span>
        </div>
        {/each}
    </div>

    {#if Array.isArray(waffleSquares) && waffleSquares.length}
        <div class="waffle-grid" aria-label="Waffle chart grid">
        {#each waffleSquares as s, i}
            <div class="waffle-cell" title={s.category} style="background-color: {getBarColor(s)}"></div>
        {/each}
        </div>
    {:else}
        <p>No data available for {Selected_city}</p>
    {/if}
    </div>
</div>
</div>


<style>


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
  color: #333; margin-right: 8px;}

.swatch {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-right: 4px;
  border-radius: 2px;}

.waffle-grid {
  display: grid;
  grid-template-columns: repeat(10, 16px);
  grid-auto-rows: 16px;
  gap: 2px;
  width: max-content;
  padding: 6px 0;
}

.waffle-cell {
  width: 16px;
  height: 16px;
  border-radius: 2px;
}


</style>