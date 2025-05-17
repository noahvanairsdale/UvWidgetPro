import math
import datetime
import ephem

def calculate_uv_index(latitude, longitude, current_time):
    """
    Calculate UV index based on solar position, date, and location.
    
    Parameters:
    latitude (float): Latitude of the location
    longitude (float): Longitude of the location
    current_time (datetime): Current date and time
    
    Returns:
    float: Estimated UV index
    """
    # Create a location object
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.date = current_time
    
    # Calculate sun's position
    sun = ephem.Sun()
    sun.compute(observer)
    
    # Convert altitude to degrees
    sun_altitude = math.degrees(sun.alt)
    
    # Calculate the solar zenith angle (90° - altitude)
    solar_zenith_angle = 90 - sun_altitude
    
    # If sun is below horizon, UV index is 0
    if solar_zenith_angle >= 90:
        return 0
    
    # Calculate clear sky UV index using a scientific model
    # This is a simplified model based on the relationship between
    # UV index and solar zenith angle
    
       # Calculate air mass (for zenith angles < 89°)
    am = 1 / (math.cos(math.radians(solar_zenith_angle)) + 0.15 * ((93.885 - solar_zenith_angle) ** -1.253))
    
    # Standard clear-sky max UV index at sea level at equator
    uv_clear_sky = 12.0  # Adjust as needed for your region

    # Atmospheric attenuation factor (empirically, UV decreases with higher air mass)
    attenuation = math.exp(-0.4 * (am - 1))  # 0.4 is an empirical constant

    # Altitude adjustment: ~10% per 1000m above sea level
    if 'altitude_meters' in locals():
        altitude_m = altitude_meters
    else:
        altitude_m = 0  # Default to sea level if not set
    altitude_adjustment = 1 + (altitude_m / 1000) * 0.1

    # Estimate UV index
    uv_index = uv_clear_sky * attenuation * seasonal_adjustment * cloud_adjustment * altitude_adjustment * time_adjustment

    uv_index = max(0, uv_index)
    return round(uv_index, 1)
