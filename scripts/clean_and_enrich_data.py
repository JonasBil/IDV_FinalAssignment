import os
import json
import math
import urllib.request
import urllib.parse
import time
from collections import defaultdict
from statistics import median

# Get script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration
PERSON_DATA_FILE = os.path.join(SCRIPT_DIR, 'data.json')
GEODATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'app', 'src', 'CityStreetData')
SUMMARY_FILE = os.path.join(SCRIPT_DIR, 'merge_summary.json')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# City name mapping (data.json names -> geodata file names)
CITY_MAPPING = {
    'Ancona': 'ancona',
    'Barcelona': 'barcelona',
    'Berlin, Stadt': 'berlin',
    'Bologna': 'bologna',
    'Brussels': 'brussels',
    'Budapest': 'budapest',
    'Chisinau': 'chisinau',
    'Debrecen': 'debrecen',
    'Firenze': 'firenze',
    'Gdańsk': 'gdansk',
    'Genova': 'genova',
    'Grad Zagreb': 'zagreb',
    'Katowice': 'katowice',
    'Kraków': 'krakow',
    'Kyiv': 'kyiv',
    'København': 'københavn',
    'Lisbon': 'lisboa',
    'Lyon': 'lyon',
    'Madrid': 'madrid',
    'Milano': 'milano',
    'Municipiul Bucureşti': 'bucuresti',
    'Municipiul Sibiu': 'sibiu',
    'München, Landeshauptstadt': 'munchen',
    'Oslo kommune': 'oslo',
    'Palermo': 'palermo',
    'Paris': 'paris',
    'Praha': 'praha',
    'Roma': 'roma',
    'Sevilla': 'sevilla',
    'Stockholm': 'stockholm',
    'Torino': 'torino',
    'Warszawa': 'warszawa',
    'Wien': 'wien',
    'Wrocław': 'wrocław',
    'Łódź': 'łodz',
    'Ψευδοδημοτική Κοινότητα Αθηναίων': 'athene'
}

def get_osm_center(city_name):
    # Clean city name for better search results
    search_name = city_name
    replacements = [
        ("Municipiul ", ""),
        ("Grad ", ""),
        (" kommune", ""),
        (", Stadt", ""),
        (", Landeshauptstadt", ""),
        ("Ψευδοδημοτική Κοινότητα Αθηναίων", "Athens")
    ]
    for old, new in replacements:
        search_name = search_name.replace(old, new)
    
    print(f"  🔍 Looking up center for '{search_name}' via OSM...")
    
    try:
        query = urllib.parse.urlencode({'q': search_name, 'format': 'json', 'limit': 1})
        url = f"https://nominatim.openstreetmap.org/search?{query}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'VUB-Student-Project/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                print(f"    ✅ Found: {lat}, {lon}")
                return {'lat': lat, 'lon': lon, 'source': 'osm'}
            else:
                print(f"    ❌ Not found in OSM")
                return None
    except Exception as e:
        print(f"    ⚠️ Error fetching from OSM: {e}")
        return None

def normalize_street_name(name):
    if not name:
        return ''
    return name.strip().lower().replace('  ', ' ')

def clean_person_data(record):
    cleaned = {}
    for key, value in record.items():
        if value in [None, '', 'null', 'NULL']:
            continue
        elif isinstance(value, str):
            cleaned[key] = value.strip()
        else:
            cleaned[key] = value
    
    if cleaned.get('person') == 1.0:
        cleaned['is_person'] = True
    elif cleaned.get('person') == 0.0:
        cleaned['is_person'] = False
    else:
        # If person status is unknown/null, we might not want to store it as a property if we want to save space
        # But let's keep it if it was explicitly in the data
        pass
    
    # Remove redundant fields that are common to the whole city or not needed
    for field in ['person', 'lau_name', 'gisco_id', 'country', 'named_after_n']:
        if field in cleaned:
            del cleaned[field]
            
    return cleaned

def simplify_coordinates(coords, tolerance=0.0005):
    """
    Simplify a list of coordinates using a basic distance-based algorithm.
    tolerance: 0.0005 degrees is roughly 55 meters.
    """
    if not coords or len(coords) <= 2:
        return coords
    
    simplified = [coords[0]]
    last_point = coords[0]
    
    for i in range(1, len(coords) - 1):
        point = coords[i]
        # Calculate squared distance (faster than sqrt)
        dist_sq = (point[0] - last_point[0])**2 + (point[1] - last_point[1])**2
        
        if dist_sq > tolerance**2:
            simplified.append(point)
            last_point = point
            
    simplified.append(coords[-1])
    return simplified

def round_coordinates(coords, precision=4):
    """Recursively round coordinates in a list/nested list"""
    if not coords:
        return coords
    
    if isinstance(coords[0], (int, float)):
        return [round(c, precision) for c in coords]
    
    # Handle LineString (list of points)
    if isinstance(coords[0], list) and isinstance(coords[0][0], (int, float)):
        # Simplify first, then round
        simplified = simplify_coordinates(coords)
        return [[round(c, precision) for c in point] for point in simplified]

    return [round_coordinates(c, precision) for c in coords]

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def merge_city_data(city_name, person_records, city_center=None):
    """
    Merge person data with geodata for a city
    """
    print(f"\n📍 Processing {city_name}...")
    
    # Get geodata file name
    geodata_filename = CITY_MAPPING.get(city_name)
    if not geodata_filename:
        print(f"  ⚠️  No geodata mapping found, skipping")
        return None, None, None
    
    geodata_path = os.path.join(GEODATA_DIR, f"{geodata_filename}.json")
    if not os.path.exists(geodata_path):
        print(f"  ⚠️  Geodata file not found: {geodata_path}")
        return None, None, None
    
    # Load geodata
    with open(geodata_path, 'r', encoding='utf-8') as f:
        geodata = json.load(f)
    
    print(f"  📊 Person records: {len(person_records)}")
    print(f"  📊 Geodata features: {len(geodata.get('features', []))}")
    
    # Create lookup for person data by street name
    person_lookup = defaultdict(list)
    for record in person_records:
        street_name = normalize_street_name(record.get('street_name'))
        if street_name:
            person_lookup[street_name].append(clean_person_data(record))
    
    # Merge data
    # We will group geometries by street name to avoid having thousands of small segments
    # for the same street (OSM data is often segmented).
    street_geometries = defaultdict(list)
    street_person_data = {}
    
    matched_count = 0
    person_streets_count = 0
    
    # First pass: Collect all valid street geometries
    all_points_lat = []
    all_points_lon = []

    for feature in geodata.get('features', []):
        # Get street name from geodata
        geo_street_name = feature.get('properties', {}).get('name')
        normalized_geo_name = normalize_street_name(geo_street_name)
        
        # Find matching person data
        person_data_list = person_lookup.get(normalized_geo_name, [])
        
        if person_data_list:
            # If multiple person records for same street, pick the best one
            # Prefer records where is_person is True
            selected_person_data = person_data_list[0]
            for pd in person_data_list:
                if pd.get('is_person') is True:
                    selected_person_data = pd
                    break
            
            # Store person data for this street if we haven't yet
            if normalized_geo_name not in street_person_data:
                street_person_data[normalized_geo_name] = {
                    'name': geo_street_name, # Keep original casing from first segment
                    'highway': feature.get('properties', {}).get('highway'), # Keep highway type
                    **selected_person_data
                }
                matched_count += 1
                if selected_person_data.get('is_person'):
                    person_streets_count += 1

            # Collect geometry segments
            geom = feature.get('geometry', {})
            if not geom:
                continue
                
            coords = geom.get('coordinates')
            if not coords:
                continue

            # Round/Simplify coordinates
            rounded_coords = round_coordinates(coords)

            if geom.get('type') == 'LineString':
                street_geometries[normalized_geo_name].append(rounded_coords)
                # Collect points for centroid calculation (sample first point of segment)
                if rounded_coords:
                    all_points_lon.append(rounded_coords[0][0])
                    all_points_lat.append(rounded_coords[0][1])

            elif geom.get('type') == 'MultiLineString':
                street_geometries[normalized_geo_name].extend(rounded_coords)
                # Collect points for centroid calculation
                if rounded_coords and rounded_coords[0]:
                    all_points_lon.append(rounded_coords[0][0][0])
                    all_points_lat.append(rounded_coords[0][0][1])

    # Determine Center
    if city_center:
        center_lat = city_center['lat']
        center_lon = city_center['lon']
        print(f"  📍 Using OSM Center: {center_lat:.4f}, {center_lon:.4f}")
        center_info = city_center
    else:
        # Fallback to median calculation
        if not all_points_lat:
            print("  ⚠️  No valid geometries found")
            return None, None, None

        center_lat = median(all_points_lat)
        center_lon = median(all_points_lon)
        print(f"  📍 Calculated Center (Median): {center_lat:.4f}, {center_lon:.4f}")
        center_info = {'lat': center_lat, 'lon': center_lon, 'source': 'median'}

    # Construct final merged features with Distance Filtering
    enriched_features = []
    MAX_DISTANCE_KM = 10 # Filter streets further than 10km from center
    
    dropped_segments = 0
    total_segments = 0

    for norm_name, coords_list in street_geometries.items():
        valid_segments = []
        for segment in coords_list:
            if not segment:
                continue
            
            total_segments += 1
            
            # Check distance of the first point of the segment
            # segment is a list of points [[lon, lat], [lon, lat], ...]
            # Ensure we have valid coordinates
            if isinstance(segment[0], (int, float)):
                 # Should not happen for MultiLineString segments, but safety fallback
                 p_lon, p_lat = segment[0], segment[1]
            else:
                 p_lon, p_lat = segment[0][0], segment[0][1]

            dist = haversine_distance(center_lat, center_lon, p_lat, p_lon)
            
            if dist <= MAX_DISTANCE_KM:
                valid_segments.append(segment)
            else:
                dropped_segments += 1
        
        if not valid_segments:
            continue

        # Create a MultiLineString for the whole street
        enriched_feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'MultiLineString',
                'coordinates': valid_segments
            },
            'properties': street_person_data[norm_name]
        }
        enriched_features.append(enriched_feature)
    
    if total_segments > 0:
        print(f"  ✂️  Filtered out {dropped_segments} / {total_segments} segments (> {MAX_DISTANCE_KM}km)")
    
    # Create enriched GeoJSON
    enriched_geojson = {
        'type': 'FeatureCollection',
        'features': enriched_features
    }
    
    stats = {
        'total_features': len(enriched_features),
        'matched_streets': matched_count,
        'person_streets': person_streets_count
    }
    
    return enriched_geojson, stats, center_info

def main():
    print('DATA MERGING SCRIPT')
    
    with open(PERSON_DATA_FILE, 'r', encoding='utf-8') as f:
        person_data = json.load(f)
    
    cities = defaultdict(list)
    for record in person_data:
        cities[record['lau_name']].append(record)
    
    all_stats = {}
    
    # Load existing city centers if available
    centers_file = os.path.join(OUTPUT_DIR, '..', 'city_centers.json')
    city_centers = {}
    if os.path.exists(centers_file):
        with open(centers_file, 'r', encoding='utf-8') as f:
            city_centers = json.load(f)
    
    for city_name, records in sorted(cities.items()):
        safe_name = CITY_MAPPING.get(city_name, city_name.lower())
        
        # Check if we have a valid OSM center already
        current_center = city_centers.get(safe_name)
        if not current_center or current_center.get('source') != 'osm':
            osm_center = get_osm_center(city_name)
            if osm_center:
                city_centers[safe_name] = osm_center
                current_center = osm_center
                # Save immediately to cache progress
                with open(centers_file, 'w', encoding='utf-8') as f:
                    json.dump(city_centers, f, ensure_ascii=False, indent=2)
                time.sleep(1.1) # Respect Nominatim rate limit (1 sec)
        
        enriched_geojson, stats, center = merge_city_data(city_name, records, current_center)
        
        if enriched_geojson:
            all_stats[city_name] = stats
            output_file = os.path.join(OUTPUT_DIR, f'{safe_name}_enriched.json')
            
            # Update center info if it was calculated (fallback)
            if not current_center:
                 city_centers[safe_name] = center

            # Save minified JSON to save space
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enriched_geojson, f, ensure_ascii=False, separators=(',', ':'))
            
            print(f'Saved to {output_file}')
    
    # Final save of city centers
    with open(centers_file, 'w', encoding='utf-8') as f:
        json.dump(city_centers, f, ensure_ascii=False, indent=2)
    print(f'Saved city centers to {centers_file}')

    summary = {
        'total_cities_processed': len(all_stats),
        'cities': all_stats
    }
    
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print('MERGING COMPLETE!')

if __name__ == '__main__':
    main()

