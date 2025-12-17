<script>
  import data from '../Streets.json';

  // Only keep lists which have gender = female
  const females = data.filter(d => d.gender === "female");

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

  // Cleaned dataset
  let categories = females.map(d => ({
    ...d,
    category_cleaned: classifyCategories(d.occupation_label, d.occupation_category)
  }));

  // Count categories
  const counts = {};
  for (const d of categories) {
    const cat = d.category_cleaned;
    counts[cat] = (counts[cat] || 0) + 1;
  }

  const total = categories.length;
  const categoryData = Object.entries(counts).map(([category, count]) => ({
    category,
    count,
    percentage: (count / total) * 100
  })).sort((a, b) => b.count - a.count);

  // Prepare waffle data (100 cells)
  let waffleCells = [];
  
  // Colors for categories
  const colors = {
    "military": "#ef4444", // red
    "religion": "#f59e0b", // amber
    "politics": "#3b82f6", // blue
    "culture": "#10b981", // green
    "others": "#6b7280"   // gray
  };

  for (const cat of categoryData) {
    const numCells = Math.round(cat.percentage);
    for (let i = 0; i < numCells; i++) {
      if (waffleCells.length < 100) {
        waffleCells.push({ category: cat.category, color: colors[cat.category] || "#ccc" });
      }
    }
  }
  
  // Fill remaining if any (due to rounding)
  while (waffleCells.length < 100) {
     waffleCells.push({ category: "others", color: colors["others"] });
  }
</script>

<div class="waffle-container">
  <h2>Overall Category Distribution</h2>
  <div class="waffle-grid">
    {#each waffleCells as cell}
      <div class="waffle-cell" style="background-color: {cell.color}" title="{cell.category}"></div>
    {/each}
  </div>
  <div class="legend">
    {#each categoryData as cat}
      <div class="legend-item">
        <span class="color-box" style="background-color: {colors[cat.category] || '#ccc'}"></span>
        <span>{cat.category} ({cat.percentage.toFixed(1)}%)</span>
      </div>
    {/each}
  </div>
</div>

<style>
  .waffle-container {
    padding: 1rem;
    color: #f3f4f6;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .waffle-grid {
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    gap: 4px;
    width: 300px;
    margin: 1rem auto;
  }
  .waffle-cell {
    width: 100%;
    padding-top: 100%; /* Aspect ratio 1:1 */
    border-radius: 2px;
  }
  .legend {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
  }
  .color-box {
    width: 1rem;
    height: 1rem;
    display: inline-block;
    border-radius: 2px;
  }
  h2 {
    margin-bottom: 1rem;
    text-align: center;
  }
</style>
