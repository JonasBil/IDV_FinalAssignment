<script>
  //Using $props() to get the right properties to the svg element for constructing the piechart
  let { data = [], size = 250 } = $props();

  //If data is not an array, use empty array instead, count of all values in dataset
  let safe = $derived(Array.isArray(data) ? data : []);
  let total = $derived(safe.reduce((s, d) => s + d.count, 0));
  let radius = $derived(size / 2);

  //Hover state for indicating the percentage per slice
  let hovered = $state(null);

  //Build segments => Start position/End position of each pie slice
  let segments = $derived(
    total === 0
      ? []
      : (() => {
          let acc = 0;
          return safe.map(d => {
            const value = d.count / total;
            const start = acc;
            const end = acc + value;
            acc = end;
            return { category: d.category, start, end, value };
          });
        })()
  )

  //Define colors for each category
  const colors = {
    culture: "#17BECF",
    politics: "#FFC20A",
    religion: "#00668E",
    military: "#FF9920",
    science: "#2CA02C",
    others: "#9E48D0"
  };
</script>

<!--Defining what gets shown in the SVG-->

<!--If no data is available show this-->
{#if total === 0}
  <svg width={size} height={size}>
    <text
      x="50%" 
      y="50%"
      text-anchor="middle"
      dominant-baseline="middle"
      fill="#777">No data</text>
  </svg>

<!--Else show the piechart-->
{:else}
  <div class="chart-wrapper">
    <!-- Tooltip -->
    {#if hovered}
      <div class="tooltip">
        <strong>{hovered.category}</strong><br />
        {(hovered.value * 100).toFixed(1)}%
      </div>
    {/if}

    <svg width={size} height={size}>
      {#each segments as s}
        <path
          on:mouseenter={() => hovered = s}
          on:mouseleave={() => hovered = null}
          d="
            M {radius} {radius}
            L {radius + radius * Math.cos(2 * Math.PI * s.start)}
              {radius + radius * Math.sin(2 * Math.PI * s.start)}
            A {radius} {radius} 0
              {s.end - s.start > 0.5 ? 1 : 0} 1
              {radius + radius * Math.cos(2 * Math.PI * s.end)}
              {radius + radius * Math.sin(2 * Math.PI * s.end)}
            Z
          "
          fill={colors[s.category] || "#ccc"}
          opacity={hovered && hovered !== s ? 0.4 : 1}
          style="cursor:pointer"
        />
      {/each}
    </svg>
  </div>
{/if}

<!-- Legend -->
<div class="legend">
  {#each Object.entries(colors) as [cat, col]}
    <div class="legend-row">
      <span class="legend-color" style="background:{col}"></span>
      <span class="legend-label">{cat}</span>
    </div>
  {/each}
</div>

<style>
  .chart-wrapper {
    position: relative;
    display: inline-block;
  }

  .tooltip {
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 0.4rem;
    padding: 0.4rem 0.6rem;
    font-size: 0.75rem;
    color: #e5e7eb;
    line-height: 1.2;
    pointer-events: none;
    white-space: nowrap;
    box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.5);
    z-index: 10;
  }

  .tooltip strong {
    font-weight: 600;
    color: #f3f4f6;
  }

  .legend {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .legend-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 3px;
  }

  .legend-label {
    font-size: 0.9rem;
    color: #555;
    text-transform: capitalize;
  }
</style>
