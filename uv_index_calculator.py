import math
import datetime
import ephem
import logging

logger = logging.getLogger(__name__)

def calculate_uv_index_with_clouds(latitude, longitude, cloud_cover_percent=0, temperature=None, weather_description=''):
    """
    Enhanced UV index calculation that takes into account cloud cover and regional factors.
    
    Parameters:
    latitude (float): Latitude of the location
    longitude (float): Longitude of the location
    cloud_cover_percent (float): Cloud cover percentage (0-100)
    temperature (float, optional): Current temperature in Celsius
    weather_description (str, optional): Text description of the weather
    
    Returns:
    float: Estimated UV index adjusted for clouds and regional factors
    """
    current_time = datetime.datetime.now()
    
    # Calculate the base UV index
    base_uv = calculate_base_uv_index(latitude, longitude, current_time)
    logger.debug(f"Base UV index: {base_uv}")
    
    # Calculate cloud adjustment factor (more sophisticated than before)
    cloud_adjustment = calculate_cloud_adjustment(cloud_cover_percent, weather_description)
    logger.debug(f"Cloud adjustment factor: {cloud_adjustment}")
    
    # Regional adjustment factor for Michigan/Midwest
    regional_adjustment = calculate_regional_adjustment(latitude, longitude, current_time, temperature)
    logger.debug(f"Regional adjustment factor: {regional_adjustment}")
    
    # Apply the adjustments
    adjusted_uv = base_uv * cloud_adjustment * regional_adjustment
    
    # Ensure UV index is never negative and round to 1 decimal place
    adjusted_uv = max(0, round(adjusted_uv, 1))
    
    logger.debug(f"Final adjusted UV index: {adjusted_uv}")
    return adjusted_uv

def calculate_base_uv_index(latitude, longitude, current_time):
    """
    Calculate the base UV index without cloud cover adjustments.
    This is a more calibrated version of the original algorithm.
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
    
    # Recalibrated parameters for more realistic UV index
    # The maximum UV index is reduced from 12.5 to 11 to better match real-world measurements
    uv_max = 11.0
    alpha = 1.35  # Slightly increased to reduce values at higher zenith angles
    
    # Seasonal adjustment (enhanced to be more accurate)
    day_of_year = current_time.timetuple().tm_yday
    year_length = 366 if current_time.year % 4 == 0 else 365
    
    # Calculate seasonal factor (more realistic curve)
    # Northern hemisphere seasonal adjustment - Michigan specific
    seasonal_adjustment = 0.8 + 0.5 * math.sin((day_of_year / year_length) * 2 * math.pi - math.pi/2)
    
    # Time of day adjustment (UV peaks at solar noon)
    hours_since_midnight = current_time.hour + current_time.minute / 60
    
    # Improved time adjustment curve
    if solar_zenith_angle >= 90:  # Night time
        time_adjustment = 0
    else:
        # Create a bell curve centered at solar noon (approximately 12-13)
        solar_noon_offset = abs(hours_since_midnight - 12.5)
        if solar_noon_offset > 6:
            time_adjustment = 0
        else:
            time_adjustment = math.cos(solar_noon_offset * math.pi / 6) ** 2
    
    # Calculate base UV index
    if solar_zenith_angle < 75:
        uv_index = uv_max * (math.cos(math.radians(solar_zenith_angle)) ** alpha) * seasonal_adjustment * time_adjustment
    else:
        # For high zenith angles, use a more conservative formula
        uv_index = uv_max * 0.15 * ((90 - solar_zenith_angle) / 15) * seasonal_adjustment * time_adjustment
    
    # Altitude adjustment for Livonia (approximately 200m above sea level)
    altitude_meters = 200
    altitude_adjustment = 1 + (altitude_meters / 1000) * 0.1
    uv_index *= altitude_adjustment
    
    return uv_index

def calculate_cloud_adjustment(cloud_cover_percent, weather_description):
    """
    Calculate a more sophisticated cloud adjustment factor.
    Different cloud types affect UV differently, and thicker clouds block more UV.
    
    Parameters:
    cloud_cover_percent (float): Cloud cover percentage (0-100)
    weather_description (str): Weather description text
    
    Returns:
    float: Cloud adjustment factor (0-1)
    """
    # Convert cloud cover to a decimal (0-1)
    cloud_cover = cloud_cover_percent / 100
    
    # Base adjustment - cloud cover has a significant impact on UV
    # This formula gives ~0.9 for 10% cover, ~0.6 for 50% cover, and ~0.2 for 90% cover
    base_adjustment = 1 - (cloud_cover ** 0.6)
    
    # Adjust based on cloud type from weather description
    weather_description = weather_description.lower()
    
    # Heavy cloud conditions have stronger UV reduction
    if any(term in weather_description for term in ['rain', 'shower', 'thunderstorm', 'storm']):
        type_multiplier = 0.5
    elif any(term in weather_description for term in ['overcast', 'fog', 'mist']):
        type_multiplier = 0.7
    elif any(term in weather_description for term in ['partly cloudy', 'scattered clouds']):
        type_multiplier = 0.9
    else:
        type_multiplier = 1.0
        
    # Calculate final cloud adjustment
    cloud_adjustment = base_adjustment * type_multiplier
    
    # Ensure sensible range
    return max(0.1, min(1.0, cloud_adjustment))

def calculate_regional_adjustment(latitude, longitude, current_time, temperature=None):
    """
    Apply regional adjustment factors specific to Michigan/Midwest.
    
    Parameters:
    latitude (float): Latitude
    longitude (float): Longitude
    current_time (datetime): Current date and time
    temperature (float, optional): Current temperature in Celsius
    
    Returns:
    float: Regional adjustment factor
    """
    # Michigan-specific adjustments
    
    # 1. Winter adjustment - Michigan winters have very low UV
    month = current_time.month
    if month in [12, 1, 2]:  # Winter months
        winter_factor = 0.7
    elif month in [3, 11]:  # Transition months
        winter_factor = 0.85
    else:
        winter_factor = 1.0
    
    # 2. Great Lakes effect - proximity to large bodies of water can affect UV
    # Approximate adjustment based on Michigan geography
    great_lakes_factor = 0.95  # Slight reduction due to humidity and air quality
    
    # 3. Urban/pollution adjustment for areas near Detroit
    # Livonia is close to Detroit
    distance_to_detroit_center = math.sqrt((latitude - 42.3314) ** 2 + (longitude - (-83.0458)) ** 2)
    if distance_to_detroit_center < 0.5:  # Very close to Detroit
        urban_factor = 0.85
    elif distance_to_detroit_center < 1.0:  # Somewhat close (like Livonia)
        urban_factor = 0.9
    else:
        urban_factor = 1.0
    
    # 4. Temperature factor (if available)
    if temperature is not None:
        # In colder weather, people tend to overestimate UV intensity
        if temperature < 5:  # Cold
            temp_factor = 0.85
        elif temperature < 15:  # Cool
            temp_factor = 0.9
        else:
            temp_factor = 1.0
    else:
        temp_factor = 1.0
    
    # Combine all regional factors
    regional_adjustment = winter_factor * great_lakes_factor * urban_factor * temp_factor
    
    return regional_adjustment
