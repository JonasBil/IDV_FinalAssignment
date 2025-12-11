import osmtogeojson from 'osmtogeojson';

export async function getCityGeoJSON(cityName) {
    // Overpass QL query:
    // 1. Get the area for the city name
    // 2. Find all "ways" (streets) with a "highway" tag inside that area
    const query = `
      [out:json];
      area[name="${cityName}"]->.searchArea;
      (
        way["highway"](area.searchArea);
      );
      out geom;
    `;

    const url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;

    try {
        const response = await fetch(url);
        const osmData = await response.json();
        
        // Convert the raw OSM data (nodes/ways) to GeoJSON (Features/LineStrings)
        const geojson = osmtogeojson(osmData);
        return geojson;
    } catch (error) {
        console.error("Error fetching map data:", error);
        return null;
    }
}