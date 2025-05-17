import requests

def get_uv_from_open_meteo(latitude, longitude):
    """
    Fetches the current UV index, cloud cover, and precipitation from Open-Meteo for the given location.

    Parameters:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: {
            "uv_index": float or None,
            "cloud_cover": float or None,
            "precipitation": float or None
        }
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&current=uv_index,cloudcover,precipitation"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        return {
            "uv_index": current.get("uv_index"),
            "cloud_cover": current.get("cloudcover"),
            "precipitation": current.get("precipitation")
        }
    except Exception as e:
        print("Error fetching from Open-Meteo:", e)
        return {
            "uv_index": None,
            "cloud_cover": None,
            "precipitation": None
        }

# Example usage
if __name__ == "__main__":
    # Replace with your desired coordinates
    lat, lon = 42.4, -83.4  # Example: Livonia, MI
    uv_data = get_uv_from_open_meteo(lat, lon)
    print(f"UV Index: {uv_data['uv_index']}")
    print(f"Cloud Cover: {uv_data['cloud_cover']}%")
    print(f"Precipitation: {uv_data['precipitation']} mm")
