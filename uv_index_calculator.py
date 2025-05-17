import math
import datetime
import ephem

def calculate_uv_index(
    latitude,
    longitude,
    current_time,
    cloud_cover=0,  # % (0-100)
    ozone_column=300,
    aod=0.1,
    is_raining=False
):
    """
    Calculate UV index based on solar position, date, location, and atmospheric conditions.
    
    Parameters:
    latitude (float): Latitude of the location
    longitude (float): Longitude of the location
    current_time (datetime): Current date and time
    cloud_cover (float): Cloud cover percentage (0-100)
    ozone_column (float): Total column ozone in Dobson Units
    aod (float): Aerosol optical depth
    is_raining (bool): Is it currently raining? (default False)
    
    Returns:
    float: Estimated UV index
    """
    try:
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
        
        # Solar zenith angle (90° - altitude)
        solar_zenith_angle = 90 - sun_altitude
        
        # If sun is below horizon, UV index is 0
        if solar_zenith_angle >= 90:
            return 0
    except Exception as e:
        print(f"Error calculating solar position: {str(e)}")
        # Fallback to average UV index for Livonia based on month
        month = current_time.month
        avg_uv = [3.0, 4.0, 5.5, 7.0, 8.5, 9.0, 8.5, 7.0, 5.5, 4.0, 3.0, 2.5][month - 1]
        # Apply much stronger cloud/rain reduction
        reduction = 0.95 if is_raining or cloud_cover >= 90 else 0.7 * cloud_cover / 100
        cloud_factor = 1 - reduction
        return round(avg_uv * cloud_factor, 1)

    # Parameters adjusted for mid-latitudes
    uv_max = 12.0  # Typical max for Livonia
    alpha = 1.2    # Empirical constant

    # Seasonal adjustment
    day_of_year = current_time.timetuple().tm_yday
    year_length = 366 if current_time.year % 4 == 0 else 365
    seasonal_adjustment = math.sin((day_of_year / year_length) * 2 * math.pi - math.pi/2) * 0.25 + 1

    # Cloud cover and rain adjustment
    # If raining or very cloudy, UV is reduced by 95-99%
    if is_raining or cloud_cover >= 90:
        cloud_adjustment = 0.05
    elif cloud_cover >= 75:
        cloud_adjustment = 0.10  # 90% reduction for thick clouds
    elif cloud_cover >= 50:
        cloud_adjustment = 0.30  # 70% reduction for broken clouds
    elif cloud_cover >= 25:
        cloud_adjustment = 0.60  # 40% reduction for scattered clouds
    else:
        cloud_adjustment = 1.0   # Clear or mostly clear

    # Ozone adjustment
    ozone_adjustment = 300 / max(100, ozone_column)  # Avoid division by zero, normalize to 300 DU

    # Aerosol adjustment
    air_mass = 1 / max(0.1, math.cos(math.radians(solar_zenith_angle)))  # Avoid division by zero
    aerosol_adjustment = math.exp(-aod * air_mass)

    # Time of day adjustment
    hours_since_midnight = current_time.hour + current_time.minute / 60
    hours_from_noon = hours_since_midnight - 12
    time_adjustment = max(0.3, math.cos(math.pi / 12 * abs(hours_from_noon)))

    # Altitude adjustment (Livonia ~200m)
    altitude_meters = 200
    altitude_adjustment = 1 + (altitude_meters / 1000) * 0.1

    # Calculate UV index
    if solar_zenith_angle < 75:
        uv_index = (
            uv_max
            * (math.cos(math.radians(solar_zenith_angle)) ** alpha)
            * seasonal_adjustment
            * cloud_adjustment
            * time_adjustment
            * altitude_adjustment
            * ozone_adjustment
            * aerosol_adjustment
        )
    else:
        uv_index = (
            uv_max
            * 0.2
            * ((90 - solar_zenith_angle) / 15)
            * seasonal_adjustment
            * cloud_adjustment
            * time_adjustment
            * altitude_adjustment
            * ozone_adjustment
            * aerosol_adjustment
        )

    # Ensure UV index is non-negative and round to 1 decimal place
    return round(max(0, uv_index), 1)
