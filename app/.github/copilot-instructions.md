# GitHub Copilot Instructions

## Project Overview
This is a **Svelte 5** data visualization project using **Vite**. It visualizes street name data (gender, citizenship, etc.) across various European cities.

## Tech Stack
- **Framework**: Svelte 5 (Runes mode)
- **Build Tool**: Vite
- **Data Visualization**: `svelteplot` (charts), `d3` (scales, geo, utilities), `chart.js`
- **Data**: JSON files and JS modules in `src/` and `src/CityStreetData/`

## Architecture & Patterns

### 1. Component Structure
- **Entry Point**: `src/App.svelte` is the main layout.
- **State Management**: Global state (like selected cities) is lifted to `App.svelte` and passed down as props to visualization components (`Waffle.svelte`, `Categories.svelte`, etc.).
- **Components**: Located in `src/components/`. Each component typically handles a specific visualization type.

### 2. Svelte 5 Conventions (Strict)
- **Reactivity**: Use **Runes** exclusively.
  - State: `let count = $state(0);`
  - Derived: `let double = $derived(count * 2);`
  - Props: `let { city1, city2 } = $props();`
  - Bindable Props: `let { value = $bindable() } = $props();`
  - **DO NOT** use legacy Svelte 4 syntax (`export let`, `$:`, etc.).
- **Snippets**: Use `{#snippet name(args)}` for reusable template blocks (e.g., inside `svelteplot` components).

### 3. Data Handling
- **Static Data**: Small datasets are imported directly (e.g., `import data from '../Streets.json'`).
- **Dynamic Data**: Larger or city-specific datasets are loaded dynamically or imported as needed (e.g., `import(...)` in `MapVisualization.svelte`).
- **Data Processing**: Data transformation often happens inside `$derived` blocks within components to react to prop changes.

### 4. Visualization Patterns
- **Svelteplot**: Used for declarative charts (Waffle, etc.).
  - Ensure `svelteplot` components (`Plot`, `WaffleY`, `AxisX`) are imported from `svelteplot`.
  - Use the `symbol` snippet for custom marks in `WaffleY`.
- **D3**: Used for scales (`d3-scale`), geography (`d3-geo`), and color schemes.

## Critical Workflows
- **Development**: Run `npm run dev` to start the Vite server.
- **Dependencies**: If `svelteplot` components are missing, ensure the latest version is installed (`npm install svelteplot@latest`).
- **Styling**: Use scoped `<style>` blocks in components. Global styles are in `src/Styles.css`.

## Common Gotchas
- **Svelteplot Version**: Ensure `svelteplot` is v0.8+ to access components like `WaffleY`.
- **Path Resolution**: Use relative paths for imports (e.g., `../Streets.json`).
- **CSS Comments**: Use `/* comment */` in CSS blocks, not `//` or `/comment/`.
