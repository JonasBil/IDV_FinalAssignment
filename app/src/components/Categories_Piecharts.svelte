<script>
  // Props 
  let {
    data = [],
    size = 250,
    city,
    otherCity,
    pctThis = {},
    pctOther = {}
  } = $props();

  // Safety & geometry
  let safe = $derived(Array.isArray(data) ? data : []);
  let total = $derived(safe.reduce((s, d) => s + d.count, 0));
  let radius = $derived(size / 2);

  // Hover state
  let hovered = $state(null);

  // Pie segments
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
  );

  // Colors
  const colors = {
    culture: "#17BECF",
    politics: "#FFC20A",
    religion: "#00668E",
    military: "#FF9920",
    science: "#EF553B",
    others: "#9E48D0"
  };
</script>

<!-- PIE -->
<div class="chart-wrapper">
  {#if hovered}
    <div class="tooltip">
      <div class="tooltip-row">
        <span class="cat">{hovered.category}</span>
        <span class="pct">{(hovered.value * 100).toFixed(1)}%</span>
      </div>

      {#if city && otherCity && pctOther[hovered.category] !== undefined}
        <div class="tooltip-compare">
          {Math.abs(
            pctThis[hovered.category] - pctOther[hovered.category]
          ).toFixed(1)}%
          {pctThis[hovered.category] > pctOther[hovered.category]
            ? " more"
            : " less"}
          than in {otherCity}
        </div>
      {/if}
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
        fill={colors[s.category]}
        opacity={hovered && hovered !== s ? 0.35 : 1}
        style="cursor:pointer"
      />
    {/each}
  </svg>
</div>

<div class="legend">
  <span><i class="culture"></i> culture</span>
  <span><i class="politics"></i> politics</span>
  <span><i class="religion"></i> religion</span>
  <span><i class="military"></i> military</span>
  <span><i class="science"></i> science</span>
  <span><i class="others"></i> others</span>
</div>


<!--STYLES-->
<style>
  .chart-wrapper {
    position: relative;
  }

  .tooltip {
    position: absolute;
    top: -6px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(20, 28, 38, 0.95);
    color: #eaeaea;
    padding: 0.45rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    pointer-events: none;
    z-index: 20;
    backdrop-filter: blur(6px);
  }

  .tooltip-row {
    display: flex;
    justify-content: space-between;
    gap: 0.6rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .tooltip-row .pct {
    color: #9fd3ff;
  }

  .tooltip-compare {
    margin-top: 0.2rem;
    padding-top: 0.2rem;
    border-top: 1px solid rgba(255,255,255,0.15);
    font-size: 0.7rem;
    color: #b8c2cc;
    text-align: center;
  }

  .legend {
  margin-top: 1.2rem;
  display: flex;
  justify-content: center;
  gap: 1.2rem;
  font-size: 0.75rem;
  color: #cfd8e3;
  flex-wrap: wrap;
  }

  .legend i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 0.35rem;
  }

  /* colors */
  .legend .culture  { background: #17BECF; }
  .legend .politics { background: #FFC20A; }
  .legend .religion { background: #00668E; }
  .legend .military { background: #FF9920; }
  .legend .science  { background: #EF553B; }
  .legend .others   { background: #9E48D0; }    

</style>





