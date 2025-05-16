import requests
import json
import time

def get_weather_data(latitude, longitude):
    """
    Get current weather data for a location using the National Weather Service API
    
    Parameters:
    latitude (float): Latitude of the location
    longitude (float): Longitude of the location
    
    Returns:
    dict: Weather data including temperature, description, humidity, and wind speed
    """
    try:
        # Format coordinates for API
        lat_str = f"{latitude:.4f}"
        lon_str = f"{longitude:.4f}"
        
        # Use the National Weather Service API which doesn't require a key
        # First, get the grid point information
        points_url = f"https://api.weather.gov/points/{lat_str},{lon_str}"
        headers = {
            "User-Agent": "LivoniaWeatherApp/1.0 (your@email.com)",
            "Accept": "application/json"
        }
        
        # Make the API request with exponential backoff for reliability
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.get(points_url, headers=headers, timeout=10)
                response.raise_for_status()  # Raise exception for HTTP errors
                break
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(retry_delay)
                retry_delay *= 2
        
        points_data = response.json()
        
        # Extract grid endpoints from the response
        if 'properties' in points_data and 'forecast' in points_data['properties']:
            forecast_url = points_data['properties']['forecast']
            stations_url = points_data['properties']['observationStations']
            
            # Get weather forecast
            forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # Get nearest observation stations
            stations_response = requests.get(stations_url, headers=headers, timeout=10)
            stations_response.raise_for_status()
            stations_data = stations_response.json()
            
            # Get observations from nearest station
            if 'features' in stations_data and len(stations_data['features']) > 0:
                station_id = stations_data['features'][0]['properties']['stationIdentifier']
                observations_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
                
                observations_response = requests.get(observations_url, headers=headers, timeout=10)
                observations_response.raise_for_status()
                observations_data = observations_response.json()
                
                # Extract the relevant weather information
                if 'properties' in observations_data:
                    properties = observations_data['properties']
                    
                    # Temperature - convert from C to F if necessary
                    temperature = None
                    if properties.get('temperature', {}).get('value') is not None:
                        temp_c = properties['temperature']['value']
                        temperature = round((temp_c * 9/5) + 32, 1)
                    
                    # Extract other weather data
                    description = properties.get('textDescription', 'No description available')
                    
                    humidity = None
                    if properties.get('relativeHumidity', {}).get('value') is not None:
                        humidity = round(properties['relativeHumidity']['value'], 0)
                    
                    wind_speed = None
                    if properties.get('windSpeed', {}).get('value') is not None:
                        # Convert from m/s to mph
                        wind_ms = properties['windSpeed']['value']
                        wind_speed = round(wind_ms * 2.237, 1)
                    
                    # Compile weather data
                    weather_data = {
                        'temperature': temperature if temperature is not None else "N/A",
                        'description': description,
                        'humidity': humidity if humidity is not None else "N/A",
                        'wind_speed': wind_speed if wind_speed is not None else "N/A"
                    }
                    
                    return weather_data
        
        # If we get here, something went wrong with getting the observations
        # Fallback to just forecast data
        if 'properties' in forecast_data and 'periods' in forecast_data['properties'] and len(forecast_data['properties']['periods']) > 0:
            current_period = forecast_data['properties']['periods'][0]
            
            weather_data = {
                'temperature': current_period.get('temperature', 'N/A'),
                'description': current_period.get('shortForecast', 'No description available'),
                'humidity': 'N/A',  # Forecast doesn't include humidity
                'wind_speed': current_period.get('windSpeed', 'N/A')
            }
            
            return weather_data
        
        raise Exception("Unable to retrieve weather data from NWS API")
        
    except Exception as e:
        print(f"Error retrieving weather data: {str(e)}")
        return None
