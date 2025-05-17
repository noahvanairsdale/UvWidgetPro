import streamlit as st
import time
import datetime
from uv_calculator import calculate_uv_index_with_clouds
from weather_service import get_weather_data

# Page configuration
st.set_page_config(
    page_title="Livonia UV & Weather",
    page_icon="🌤️",
    layout="wide"
)

# Constants
LIVONIA_LAT = 42.3834
LIVONIA_LONG = -83.3527
LOCATION_NAME = "Livonia, Michigan"
REFRESH_INTERVAL = 15 * 60  # 15 minutes in seconds

# Function to get UV index color based on value
def get_uv_color(uv_index):
    if uv_index < 3:
        return "green"  # Low
    elif uv_index < 6:
        return "yellow"  # Moderate
    elif uv_index < 8:
        return "orange"  # High
    elif uv_index < 11:
        return "red"  # Very High
    else:
        return "purple"  # Extreme

# Function to get UV risk category
def get_uv_category(uv_index):
    if uv_index < 3:
        return "Low"
    elif uv_index < 6:
        return "Moderate"
    elif uv_index < 8:
        return "High"
    elif uv_index < 11:
        return "Very High"
    else:
        return "Extreme"

# Function to get protection recommendations
def get_uv_recommendations(uv_index):
    if uv_index < 3:
        return "Wear sunglasses on bright days. If you burn easily, cover up and use sunscreen."
    elif uv_index < 6:
        return "Take precautions - cover up, wear a hat, sunglasses, and sunscreen. Seek shade during midday hours."
    elif uv_index < 8:
        return "Protection required - UV damages skin and can cause sunburn. Reduce time in the sun between 11am-4pm."
    elif uv_index < 11:
        return "Extra protection needed - unprotected skin will be damaged and can burn quickly. Avoid the sun between 11am-4pm."
    else:
        return "Take all precautions - unprotected skin can burn in minutes. Avoid the sun between 11am-4pm, wear a hat, sunglasses and sunscreen."

# Main function to update data and display widgets
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

def update_and_display():
    # Get current UTC time
    current_time_utc = datetime.now(ZoneInfo('UTC'))

    # Convert to Eastern Time (handles daylight saving automatically)
    current_time_eastern = current_time_utc.astimezone(ZoneInfo('America/New_York'))

    # Get weather data FIRST so we can extract parameters for UV calculation
    weather_data = get_weather_data(LIVONIA_LAT, LIVONIA_LONG)

    # Extract cloud cover, temperature (convert to Celsius if needed), and weather description
    if weather_data:
        cloud_cover_percent = weather_data.get('cloud_cover', 0)
        # If your API provides temperature in Fahrenheit, convert to Celsius:
        temperature_f = weather_data.get('temperature')
        temperature = (temperature_f - 32) * 5.0 / 9.0 if temperature_f is not None else None
        weather_description = weather_data.get('description', '')
    else:
        cloud_cover_percent = 0
        temperature = None
        weather_description = ''

    # Calculate UV index with new API
    uv_index = calculate_uv_index_with_clouds(
        LIVONIA_LAT,
        LIVONIA_LONG,
        cloud_cover_percent,
        temperature,
        weather_description
    )

    # --- (rest of your code remains unchanged) ---

    # Display header
    st.title(f"Weather & UV Index for {LOCATION_NAME}")
    st.subheader(f"Last updated: {current_time_eastern.strftime('%B %d, %Y %I:%M %p')}")

    # Create columns for layout
    col1, col2 = st.columns(2)

    # Display UV Index in first column
    with col1:
        st.markdown("## UV Index")
        uv_color = get_uv_color(uv_index)
        uv_category = get_uv_category(uv_index)
        st.markdown(
            f"""
            <div style="background-color: {uv_color}; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: white; font-size: 48px; margin: 0;">{uv_index:.1f}</h1>
                <h3 style="color: white; margin: 5px 0;">{uv_category}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("### Recommendations")
        st.info(get_uv_recommendations(uv_index))

    # Display Weather in second column
    with col2:
        st.markdown("## Current Weather")
        if weather_data:
            st.markdown(f"### Temperature: {weather_data['temperature']}°F")
            st.markdown(f"### Conditions: {weather_data['description']}")
            st.markdown(f"### Humidity: {weather_data['humidity']}%")
            st.markdown(f"### Wind: {weather_data['wind_speed']} mph")
        else:
            st.error("Unable to retrieve weather data. Please try again later.")
