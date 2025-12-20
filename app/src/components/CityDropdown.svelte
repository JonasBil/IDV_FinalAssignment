<script>
  import { selectedCities } from '../stores/compareSelection.js';
  import cityData from '../city_centers.json';
  import { CITY_KEY_TO_LAU, displayCityName } from '../cityMappings.js';

  // Get all city keys and sort them by English display name
  const cityKeys = Object.keys(cityData).sort((a, b) => {
    const nameA = getDisplayName(a);
    const nameB = getDisplayName(b);
    return nameA.localeCompare(nameB);
  });

  function getDisplayName(cityKey) {
    if (!cityKey) return '';
    const lauName = CITY_KEY_TO_LAU[cityKey] || CITY_KEY_TO_LAU[cityKey.toLowerCase()];
    if (lauName) {
      const english = displayCityName(lauName);
      if (english && english !== lauName) return english;
    }
    return cityKey.charAt(0).toUpperCase() + cityKey.slice(1);
  }

  function handleSelect(index, event) {
    const newCity = event.target.value;
    const current = $selectedCities;

    if (index === 0) {
      if (newCity === '') {
        selectedCities.set(current.slice(1));
      } else if (current.length === 0) {
        selectedCities.set([newCity]);
      } else if (current.length === 1) {
        if (newCity !== current[0]) {
          selectedCities.set([newCity]);
        }
      } else {
        if (newCity !== current[1]) {
          selectedCities.set([newCity, current[1]]);
        } else {
          selectedCities.set([current[1]]);
        }
      }
    } else {
      if (newCity === '') {
        selectedCities.set(current.slice(0, 1));
      } else if (current.length === 0) {
        selectedCities.set([newCity]);
      } else if (current.length === 1) {
        if (newCity !== current[0]) {
          selectedCities.set([current[0], newCity]);
        }
      } else {
        if (newCity !== current[0]) {
          selectedCities.set([current[0], newCity]);
        } else {
          selectedCities.set([current[0]]);
        }
      }
    }
  }

  let city1 = $derived($selectedCities[0] || '');
  let city2 = $derived($selectedCities[1] || '');
</script>

<div class="city-dropdown">
  <select 
    value={city1}
    onchange={(e) => handleSelect(0, e)}
    class="city-select"
  >
    <option value="">City 1</option>
    {#each cityKeys as cityKey}
      <option value={cityKey} disabled={cityKey === city2}>
        {getDisplayName(cityKey)}
      </option>
    {/each}
  </select>

  <span class="vs">vs</span>

  <select 
    value={city2}
    onchange={(e) => handleSelect(1, e)}
    class="city-select"
  >
    <option value="">City 2</option>
    {#each cityKeys as cityKey}
      <option value={cityKey} disabled={cityKey === city1}>
        {getDisplayName(cityKey)}
      </option>
    {/each}
  </select>

  {#if city1 || city2}
    <button class="clear-btn" onclick={() => selectedCities.clear()}>
      ✕
    </button>
  {/if}
</div>

<style>
  .city-dropdown {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: 1rem;
  }

  .city-select {
    padding: 0.4rem 1.8rem 0.4rem 0.6rem;
    font-size: 0.85rem;
    border: 1px solid #4b5563;
    border-radius: 0.4rem;
    background: #1f2937;
    color: #f3f4f6;
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%239ca3af' d='M2 4l4 4 4-4'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.5rem center;
    min-width: 120px;
  }

  .city-select:hover {
    border-color: #fb923c;
  }

  .city-select:focus {
    outline: none;
    border-color: #fb923c;
    box-shadow: 0 0 0 2px rgba(251, 146, 60, 0.3);
  }

  .vs {
    color: #9ca3af;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .clear-btn {
    padding: 0.3rem 0.5rem;
    font-size: 0.8rem;
    background: transparent;
    color: #9ca3af;
    border: 1px solid #4b5563;
    border-radius: 0.3rem;
    cursor: pointer;
    line-height: 1;
  }

  .clear-btn:hover {
    background: #374151;
    color: #f3f4f6;
  }

  @media (max-width: 600px) {
    .city-dropdown {
      flex-wrap: wrap;
      margin-left: 0;
      margin-top: 0.5rem;
    }

    .city-select {
      min-width: 100px;
      font-size: 0.8rem;
    }
  }
</style>
