/** Reverse geocode coordinates into a human-readable address using OSM Nominatim (no API key required). */
export async function reverseGeocode(lat: number, lng: number): Promise<string> {
  const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`;
  try {
    const response = await fetch(url, { headers: { 'Accept-Language': 'pt-BR' } });
    if (!response.ok) {
      return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }
    const data = await response.json();
    return data.display_name ?? `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  } catch {
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  }
}
