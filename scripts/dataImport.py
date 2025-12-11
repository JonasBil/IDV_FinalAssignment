import os
import json
import time
import requests
import unicodedata
import osm2geojson

# Configuration
OUTPUT_DIR = os.path.join(os.getcwd(), 'data')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

CITIES = [
    "Genova", "Zagreb", "Katowice", "Kraków", "Kyiv",
    "København", "Lisboa", "Lyon", "Madrid", "Milano",
    "București", "Sibiu", "München", "Oslo", "Palermo",
    "Paris", "Praha", "Rome", "Sevilla", "Stockholm",
    "Torino", "Warszawa", "Wien", "Wrocław", "Łódź",
    "Αθήνα"
]

def clean_filename(name):
    """
    Normalizes a city name to be used as a JSON key/filename.
    e.g., "München" -> "munchen"
    """
    nfkd_form = unicodedata.normalize('NFD', name.lower())
    without_accents = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return "".join([c if c.isalnum() else "_" for c in without_accents])

def process_geojson(geojson_data):
    """
    Cleans the GeoJSON to ensure it matches standard formatting.
    Crucially, it flattens the 'tags' object so 'name' is directly inside 'properties'.
    """
    if not geojson_data or 'features' not in geojson_data:
        return None

    cleaned_features = []

    for feature in geojson_data['features']:
        # Ensure we have a properties object
        if 'properties' not in feature:
            feature['properties'] = {}
        
        props = feature['properties']
        
        # 1. Flatten tags: Move everything from properties['tags'] to properties
        # This ensures propertues['name'] exists instead of properties['tags']['name']
        if 'tags' in props and isinstance(props['tags'], dict):
            tags = props.pop('tags')
            props.update(tags)
        
        # 2. Only keep features that actually have a name? 
        # (Optional: remove this check if you want unnamed service roads too)
        # if 'name' not in props:
        #    continue

        feature['properties'] = props
        cleaned_features.append(feature)

    geojson_data['features'] = cleaned_features
    return geojson_data

def fetch_city_data(city_name):
    print(f"Fetching data for: {city_name}...")

    # Overpass QL Query
    # [out:json] requests JSON format from Overpass
    # out geom; includes the geometry and tags
    
    # UPDATED QUERY:
    # 1. We match against "name" OR "name:en" (English name)
    # 2. We use regex "^" to match the start of the string (e.g. "Brussels" matches "Brussels-Capital Region")
    # 3. We filter by admin_level 4-8 to ensure we get a city/region boundary, not a building/POI
    query = f"""
    [out:json][timeout:60];
    area[~"name|name:en"~"^{city_name}"]
        [admin_level~"^[4-8]$"]->.searchArea;
    (
      way["highway"~"^(primary|secondary|tertiary|residential|unclassified)$"](area.searchArea);
    );
    out geom;
    """

    url = "https://overpass-api.de/api/interpreter"
    
    try:
        response = requests.get(url, params={'data': query})
        response.raise_for_status()
        
        osm_data = response.json()
        
        # Convert raw OSM JSON to GeoJSON
        geojson_data = osm2geojson.json2geojson(osm_data)
        
        # Post-process to ensure clean structure and accessible names
        final_geojson = process_geojson(geojson_data)
        
        return final_geojson
        
    except Exception as e:
        print(f"❌ Failed to fetch/convert {city_name}: {e}")
        return None

def main():
    print(f"Starting batch download to {OUTPUT_DIR}...")
    
    for city in CITIES:
        geojson = fetch_city_data(city)
        
        if geojson:
            safe_name = clean_filename(city)
            filename = f"{safe_name}.json"
            file_path = os.path.join(OUTPUT_DIR, filename)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Added indent=2 here to make the file multi-line and readable
                    json.dump(geojson, f, ensure_ascii=False, indent=2)
                
                print(f"✅ Saved {city} -> {filename} ({len(geojson['features'])} streets)")
            except Exception as e:
                print(f"❌ Error writing file for {city}: {e}")
        
        # CRITICAL: Wait between requests to honor API usage policy
        print("Waiting 5 seconds...")
        time.sleep(5)

    print("Done! All maps are in public/data/")

if __name__ == "__main__":
    main()