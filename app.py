import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
from uv_calculator import calculate_uv_index_with_clouds
from weather_service import get_weather_data as raw_get_weather_data

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

# UV index thresholds and related info
UV_LEVELS = [
    {"max": 3, "color": "green", "category": "Low", "recommendation": "Wear sunglasses on bright days. If you burn easily, cover up and use sunscreen."},
    {"max": 6, "color": "yellow", "category": "Moderate", "recommendation": "Take precautions - cover up, wear a hat, sunglasses, and sunscreen. Seek shade during midday hours."},
    {"max": 8, "color": "orange", "category": "High", "recommendation": "Protection required - UV damages skin and can cause sunburn. Reduce time in the sun between 11am-4pm."},
    {"max": 11, "color": "red", "category": "Very High", "recommendation": "Extra protection needed - unprotected skin will be damaged and can burn quickly. Avoid the sun between 11am-4pm."},
    {"max": float('inf'), "color": "purple", "category": "Extreme", "recommendation": "Take all precautions - unprotected skin can burn in minutes. Avoid the sun between 11am-4pm, wear a hat, sunglasses and sunscreen."}
]

def get_uv_info(uv_index):
    """
    Get UV color, category, and recommendation based on the UV index value.

    Args:
        uv_index (float): The UV index value.

    Returns:
        tuple: (color, category, recommendation)
    """
    for level in UV_LEVELS:
        if uv_index < level["max"]:
            return level["color"], level["category"], level["recommendation"]
    # Fallback
    return "gray", "Unknown", "No recommendation available."

def get_contrasting_text_color(bg_color):
    """
    Given a background color, return 'black' or 'white' for best contrast.
    Limited to standard color names in UV_LEVELS for now.
    """
    dark_colors = {"green", "orange", "red", "purple"}
    return "white" if bg_color in dark_colors else "black"

@st.cache_data(show_spinner=False)
def get_weather_data_cached(lat, lon):
    """
    Cached wrapper for weather data retrieval.
    """
    return raw_get_weather_data(lat, lon)

def update_and_display():
    doc = """
This is a multi-line string.
"""
