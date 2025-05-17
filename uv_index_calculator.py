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
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        observer.date = current_time

        sun = ephem.Sun()
        sun.compute(observer)
        sun_altitude = math.degrees(sun.alt)
        solar_zenith_angle = 90 - sun_altitude

        if solar_zenith_angle >= 90:
            return 0.0
    except Exception as e:
        print(f"Error calculating solar position: {str(e)}")
        month = current_time.month
        avg_uv = [3.0, 4.0, 5.5, 7.0, 8.5, 9.0, 8.5, 7.0, 5.5, 4.0, 3.0, 2.5][month - 1]
        cloud_penalty = 0.01 if is_raining else math.exp(-3.5 * (cloud_cover / 100))
        return round(avg_uv * cloud_penalty, 1)

    uv_max = 12.0
    alpha = 1.2

    day_of_year = current_time.timetuple().tm_yday
    year_length = 366 if current_time.year % 4 == 0 else 365
    seasonal_adjustment = math.sin((day_of_year / year_length) * 2 * math.pi - math.pi/2) * 0.25 + 1

    # --- STRONGER CLOUD & RAIN REDUCTION (nonlinear, much steeper) ---
    if is_raining:
        cloud_adjustment = 0.01  # 99% reduction for rain
    else:
        # Exponential penalty: 0% clouds = 1, 50% = ~0.18, 80% = ~0.03, 100% = ~0.002
        cloud_adjustment = math.exp(-3.5 * (cloud_cover / 100))
        # Clamp minimum to a realistic lower bound (not zero, but almost)
        cloud_adjustment = max(cloud_adjustment, 0.01)

    ozone_adjustment = 300 / max(100, ozone_column)
    air_mass = 1 / max(0.1, math.cos(math.radians(solar_zenith_angle)))
    aerosol_adjustment = math.exp(-aod * air_mass)
    hours_since_midnight = current_time.hour + current_time.minute / 60
    hours_from_noon = hours_since_midnight - 12
    time_adjustment = max(0.3, math.cos(math.pi / 12 * abs(hours_from_noon)))
    altitude_meters = 200
    altitude_adjustment = 1 + (altitude_meters / 1000) * 0.1

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

    # Clamp UV index to [0, 12] range for realism
    return round(min(max(uv_index, 0.0), 12.0), 1)
