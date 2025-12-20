// Explicit mapping from city_centers.json keys to dataset lau_name values
export const CITY_KEY_TO_LAU = {
  'berlin': 'Berlin, Stadt',
  'munchen': 'München, Landeshauptstadt',
  'münchen': 'München, Landeshauptstadt',
  'munich': 'München, Landeshauptstadt',
  'athene': 'Ψευδοδημοτική Κοινότητα Αθηναίων',
  'athens': 'Ψευδοδημοτική Κοινότητα Αθηναίων',
  'athen': 'Ψευδοδημοτική Κοινότητα Αθηναίων',
  'bucuresti': 'Municipiul Bucureşti',
  'bucharest': 'Municipiul Bucureşti',
  'sibiu': 'Municipiul Sibiu',
  'oslo': 'Oslo kommune',
  'zagreb': 'Grad Zagreb',
  'lisboa': 'Lisbon',
  'lisbon': 'Lisbon',
  'gdansk': 'Gdańsk',
  'gdańsk': 'Gdańsk',
  'krakow': 'Kraków',
  'kraków': 'Kraków',
  'łodz': 'Łódź',
  'lodz': 'Łódź',
  'wrocław': 'Wrocław',
  'wroclaw': 'Wrocław',
  'københavn': 'København',
  'kobenhavn': 'København',
  'copenhagen': 'København',
  'warszawa': 'Warszawa',
  'warsaw': 'Warszawa'
};

// Mapping from native lau_name to English display names
export const DISPLAY_NAMES = {
  'Berlin, Stadt': 'Berlin',
  'München, Landeshauptstadt': 'Munich',
  'Ψευδοδημοτική Κοινότητα Αθηναίων': 'Athens',
  'Municipiul Bucureşti': 'Bucharest',
  'Municipiul Sibiu': 'Sibiu',
  'Oslo kommune': 'Oslo',
  'Grad Zagreb': 'Zagreb',
  'Lisbon': 'Lisbon',
  'Gdańsk': 'Gdansk',
  'Kraków': 'Krakow',
  'Łódź': 'Lodz',
  'Wrocław': 'Wroclaw',
  'København': 'Copenhagen',
  'Warszawa': 'Warsaw',
  'Wien': 'Vienna',
  'Praha': 'Prague',
  'Firenze': 'Florence',
  'Milano': 'Milan',
  'Roma': 'Rome',
  'Torino': 'Turin',
  'Genova': 'Genoa',
  'Sevilla': 'Seville',
  'Kyiv': 'Kyiv',
  'Chisinau': 'Chisinau'
};

// Mapping from dataset lau_name to city_centers.json keys (reverse of CITY_KEY_TO_LAU)
export const LAU_NAME_TO_CITY_KEY = {
  'berlin, stadt': 'berlin',
  'münchen, landeshauptstadt': 'munchen',
  'ψευδοδημοτική κοινότητα αθηναίων': 'athene',
  'municipiul bucureşti': 'bucuresti',
  'municipiul sibiu': 'sibiu',
  'oslo kommune': 'oslo',
  'grad zagreb': 'zagreb',
  'lisbon': 'lisboa',
  'gdańsk': 'gdansk',
  'kraków': 'krakow',
  'łódź': 'łodz',
  'wrocław': 'wrocław',
  'københavn': 'københavn',
  'warszawa': 'warszawa'
};

// Helper function to get display name for a city
export function displayCityName(name) {
  if (!name) return '';
  return DISPLAY_NAMES[name] ?? name;
}

// Helper function to normalize city keys (strip diacritics)
export function normalizeCityKey(v) {
  return (v ?? '')
    .toString()
    .trim()
    .toLowerCase()
    .normalize('NFKD')
    .replace(/\p{Diacritic}/gu, '');
}
