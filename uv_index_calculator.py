import math
import datetime
import ephem

def calculate_uv_index(latitude, longitude, current_time, cloud_cover=0.0, altitude_meters=200):
    """
    Calculate UV index based on solar position, date, location, cloud cover, and altitude.

    Parameters:
    latitude (float): Latitude of the location
    longitude (float): Longitude of the location
    current_time (datetime): Current date and time
    cloud_cover (float): Cloud cover as a fraction (0.0 = clear, 1.0 = completely overcast)
    altitude_meters (float): Altitude above sea level in meters

    Returns:
    float: Estimated UV index
    """
    import math
    import ephem

    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.date = current_time

    sun = ephem.Sun()
    sun.compute(observer)
    sun_altitude = math.degrees(sun.alt)
    solar_zenith_angle = 90 - sun_altitude

    if solar_zenith_angle >= 90:
        return 0

    # UV base and clear-sky model
    uv_clear_sky = 12.0  # typical max at equator/sea level, adjust for your region

    # Air mass for atmospheric attenuation
    am = 1 / (math.cos(math.radians(solar_zenith_angle)) + 0.15 * ((93.885 - solar_zenith_angle) ** -1.253))
    attenuation = math.exp(-0.4 * (am - 1))  # empirical

    # Seasonal adjustment
    day_of_year = current_time.timetuple().tm_yday
    year_length = 366 if current_time.year % 4 == 0 else 365
    seasonal_adjustment = math.sin((day_of_year / year_length) * 2 * math.pi - math.pi/2) * 0.25 + 1

    # Time of day adjustment
    hours_since_midnight = current_time.hour + current_time.minute / 60
    time_adjustment = 1.0
    if hours_since_midnight < 6 or hours_since_midnight > 18:
        time_adjustment = 0.3
    elif hours_since_midnight < 9:
        time_adjustment = 0.5 + (hours_since_midnight - 6) * 0.1667
    elif hours_since_midnight > 15:
        time_adjustment = 0.5 + (18 - hours_since_midnight) * 0.1667

    # Altitude adjustment
    altitude_adjustment = 1 + (altitude_meters / 1000) * 0.1

    # Cloud adjustment (linear: clear=1.0, overcast=0.1)
    # You can refine this to use non-linear if you prefer
    # Full overcast reduces UV by about 90%
    cloud_adjustment = 1 - 0.9 * cloud_cover

    uv_index = uv_clear_sky * attenuation * seasonal_adjustment * cloud_adjustment * altitude_adjustment * time_adjustment
    uv_index = max(0, uv_index)
    return round(uv_index, 1)
