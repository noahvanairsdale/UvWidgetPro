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
    
    # Base equation: UV = UVo * cos(SZA)^alpha
    # Where UVo is the maximum UV index at zero zenith angle
    # and alpha is an empirical constant
    
    # Parameters adjusted for mid-latitudes
    uv_max = 12.5  # Maximum theoretical UV index
    alpha = 1.2    # Empirical constant
    
    # Time of year adjustment (UV is stronger in summer)
    day_of_year = current_time.timetuple().tm_yday
    year_length = 366 if current_time.year % 4 == 0 else 365
    
    # Northern hemisphere seasonal adjustment
    seasonal_adjustment = math.sin((day_of_year / year_length) * 2 * math.pi - math.pi/2) * 0.25 + 1
    
    # Cloud cover approximation (assume default for now)
    # In a full implementation, this would come from weather data
    cloud_adjustment = 1.0  # 1.0 = clear sky
    
    # Time of day adjustment (UV peaks at solar noon)
    hours_since_midnight = current_time.hour + current_time.minute / 60
    time_adjustment = 1.0
    if hours_since_midnight < 6 or hours_since_midnight > 18:
        time_adjustment = 0.3
    elif hours_since_midnight < 9:
        time_adjustment = 0.5 + (hours_since_midnight - 6) * 0.1667
    elif hours_since_midnight > 15:
        time_adjustment = 0.5 + (18 - hours_since_midnight) * 0.1667
    
    # Calculate estimated UV index
    if solar_zenith_angle < 75:  # Scientific models are more accurate below 75 degrees
        uv_index = uv_max * (math.cos(math.radians(solar_zenith_angle)) ** alpha) * seasonal_adjustment * cloud_adjustment * time_adjustment
    else:
        # For high zenith angles, use an alternative formula to avoid overestimation
        uv_index = uv_max * 0.2 * ((90 - solar_zenith_angle) / 15) * seasonal_adjustment * cloud_adjustment * time_adjustment
    
    # Adjust for altitude (UV increases ~10% per 1000m)
    # Livonia is approximately 200m above sea level
    altitude_meters = 200
    altitude_adjustment = 1 + (altitude_meters / 1000) * 0.1
    uv_index *= altitude_adjustment
    
    # Ensure UV index is never negative
    uv_index = max(0, uv_index)
    
    # Round to 1 decimal place for display purposes
    return round(uv_index, 1)
