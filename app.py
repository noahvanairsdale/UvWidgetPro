import streamlit as st
import datetime
import requests
from uv_index_calculator import calculate_uv_index
from weather_service import get_weather_data, get_ozone_data, get_epa_uv_index

# Constants for Livonia, Michigan
LIVONIA_LAT = 42.3684
LIVONIA_LONG = -83.3527
LOCATION_NAME = "Livonia, Michigan"

# Helper functions
def get_uv_color(uv_index):
    if uv_index < 3:
        return "#00FF00"  # Green (Low)
    elif uv_index < 6:
        return "#FFFF00"  # Yellow (Moderate)
    elif uv_index < 8:
        return "#FFA500"  # Orange (High)
    elif uv_index < 11:
        return "#FF0000"  # Red (Very High)
    else:
        return "#800080"  # Purple (Extreme)

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

def get_uv_recommendations(uv_index):
    if uv_index < 3:
        return "Minimal risk. No protection needed."
    elif uv_index < 6:
        return "Wear sunglasses and sunscreen if outdoors for extended periods."
    elif uv_index < 8:
        return "Use sunscreen SPF 30+, wear protective clothing, hat, and sunglasses."
    elif uv_index < 11:
        return "Take extra precautions: SPF 30+ sunscreen, protective clothing, avoid midday sun."
    else:
        return "Avoid sun exposure between 10 AM and 4 PM, use maximum protection."

# Cache weather and ozone data to reduce API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_weather_data(lat, lon):
    return get_weather_data(lat, lon)

@st.cache_data(ttl=3600)
def get_cached_ozone_data(lat, lon):
    return get_ozone_data(lat, lon)

@st.cache_data(ttl=3600)
def get_cached_epa_uv_index(lat, lon):
    return get_epa_uv_index(lat, lon)

# Main app
from datetime import datetime
from zoneinfo import ZoneInfo

# Get current time in Eastern Time
eastern_now = datetime.now(ZoneInfo("America/New_York"))
print("Current Eastern Time:", eastern_now.strftime("%Y-%m-%d %H:%M:%S"))
    
# Get weather and atmospheric data
weather_data = get_cached_weather_data(LIVONIA_LAT, LIVONIA_LONG)
cloud_cover = weather_data.get('cloud_cover', 0) if weather_data else 0
ozone_column = get_cached_ozone_data(LIVONIA_LAT, LIVONIA_LONG)
aod = 0.1  # Placeholder; replace with actual AOD data if available
    
# Calculate UV index
uv_index = calculate_uv_index(LIVONIA_LAT, LIVONIA_LONG, current_time, cloud_cover, ozone_column, aod)
    
# Display header
st.title(f"Weather & UV Index for {LOCATION_NAME}")
st.subheader(f"Last updated: {current_time.strftime('%B %d, %Y %I:%M %p')}")
    
col1, col2 = st.columns(2)
    
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
        # Display EPA UV index for comparison
epa_uv = get_cached_epa_uv_index(LIVONIA_LAT, LIVONIA_LONG)
if epa_uv is not None:
    st.markdown(f"**EPA UV Index**: {epa_uv:.1f} (Reference)")
    st.markdown(f"**Difference**: {abs(uv_index - epa_uv):.1f}")
    st.markdown("### Recommendations")
    st.info(get_uv_recommendations(uv_index))
    
    with col2:
        st.markdown("## Weather")
        if weather_data:
            st.markdown(f"**Temperature**: {weather_data['temperature']}°F")
            st.markdown(f"**Conditions**: {weather_data['shortForecast']}")
            st.markdown(f"**Humidity**: {weather_data.get('relativeHumidity', 'N/A')}%")
            st.markdown(f"**Wind**: {weather_data.get('windSpeed', 'N/A')} {weather_data.get('windDirection', '')}")
        else:
            st.warning("Weather data unavailable.")

if __name__ == "__main__":
    update_and_display()
