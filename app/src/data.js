import dataJson from './Streets.json';

const cityNameEN = {
  "Ancona": "Ancona",
  "Barcelona": "Barcelona",
  "Berlin, Stadt": "Berlin",
  "Bologna": "Bologna",
  "Brussels": "Brussels",
  "Budapest": "Budapest",
  "Chisinau": "Chisinau",
  "Debrecen": "Debrecen",
  "Firenze": "Florence",
  "Gdańsk": "Gdansk",
  "Genova": "Genoa",
  "Grad Zagreb": "Zagreb",
  "Katowice": "Katowice",
  "Kraków": "Krakow",
  "Kyiv": "Kyiv",
  "København": "Copenhagen",
  "Lisbon": "Lisbon",
  "Lyon": "Lyon",
  "Madrid": "Madrid",
  "Milano": "Milan",
  "Municipiul București": "Bucharest",
  "Municipiul Sibiu": "Sibiu",
  "München, Landeshauptstadt": "Munich",
  "Oslo kommune": "Oslo",
  "Palermo": "Palermo",
  "Paris": "Paris",
  "Praha": "Prague",
  "Roma": "Rome",
  "Sevilla": "Seville",
  "Stockholm": "Stockholm",
  "Torino": "Turin",
  "Warszawa": "Warsaw",
  "Wien": "Vienna",
  "Wrocław": "Wroclaw",
  "Łódź": "Lodz",
  "Δημοτική Κοινότητα Αθηναίων": "Athens"
};


export const data_en = dataJson.map(d => ({
  ...d,
  city_native: d.lau_name,
  city_en: cityNameEN[d.lau_name] ?? d.lau_name
}));
