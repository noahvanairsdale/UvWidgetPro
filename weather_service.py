import requests
import re

def get_weather_data(latitude, longitude):
    """
    Fetch weather data from the National Weather Service API.
    
    Parameters:
    latitude (float): Latitude of the location
    longitude (float): Longitude of the location
    
    Returns:
    dict: Weather data including temperature, conditions, and estimated cloud cover
    """
    try:
        # Get forecast URL
        points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
        headers = {"User-Agent": "LivoniaWeatherApp/1.0 (your@email.com)"}
        response = requests.get(points_url, headers=headers, timeout=10)
        response.raise_for_status()
        points_data = response.json()
        
        # Get forecast data
        forecast_url = points_data["properties"]["forecast"]
        response = requests.get(forecast_url, headers=headers, timeout=10)
        response.raise_for_status()
        forecast_data = response.json()
        
        # Extract current period data
        current_period = forecast_data["properties"]["periods"][0]
        
        # Estimate cloud cover from shortForecast
        short_forecast = current_period.get("shortForecast", "").lower()
        cloud_cover = 0
        if "clear" in short_forecast:
            cloud_cover = 0
        elif "partly cloudy" in short_forecast or "partly sunny" in short_forecast:
            cloud_cover = 50
        elif "cloudy" in short_forecast or "overcast" in short_forecast:
            cloud_cover = 100
        elif "mostly cloudy" in short_forecast:
            cloud_cover = 75
        elif "mostly clear" in short_forecast:
            cloud_cover = 25
        
        return {
            "temperature": current_period.get("temperature"),
            "shortForecast": current_period.get("shortForecast"),
            "relativeHumidity": current_period.get("relativeHumidity", {}).get("value"),
            "windSpeed": current_period.get("windSpeed"),
            "windDirection": current_period.get("windDirection"),
            "cloud_cover": cloud_cover
        }
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return None

def get_ozone_data(latitude, longitude):
    """
    Fetch ozone data (placeholder; replace with actual API).
    
    Parameters:
    latitude (float): Latitude of the location
    longitude (float): Longitude of the location
    
    Returns:
    float: Total column ozone in Dobson Units
    """
    try:
        # Placeholder: Use a real ozone API like CAMS (requires registration)
        # Example: ozone_url = f"https://api.copernicus.eu/ozone?lat={latitude}&lon={longitude}"
        # For now, return a default value
        return 300  # Typical ozone value in Dobson Units
    except Exception as e:
        print(f"Error fetching ozone data: {str(e)}")
        return 300  # Fallback value

def get_epa_uv_index(latitude, longitude):
    """
    Fetch UV index from EPA API for Livonia, Michigan.
    
    Parameters:
    latitude (float): Latitude of the location
    longitude (float): Longitude of the location
    
    Returns:
    float: EPA UV index or None if unavailable
    """
    try:
        zip_code = "48154"  # Livonia ZIP code
        epa_url = f"https://data.epa.gov/efservice/UV_HOURLY/ZIP/{zip_code}/JSON"
        headers = {"User-Agent": "LivoniaWeatherApp/1.0 (your@email.com)"}
        response = requests.get(epa_url, headers=headers, timeout=10)
        response.raise_for_status()
        uv_data = response.json()
        if uv_data:
            return float(uv_data[-1].get("UV_VALUE", None))  # Get latest hourly UV index
        return None
    except Exception as e:
        print(f"Error fetching EPA UV index: {str(e)}")
        return None
