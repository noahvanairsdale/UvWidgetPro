import streamlit as st
import time
import datetime
from uv_index_calculator import calculate_uv_index
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
def update_and_display():
    # Get current time
    current_time = datetime.datetime.now()
    
    # Calculate UV index
    uv_index = calculate_uv_index(LIVONIA_LAT, LIVONIA_LONG, current_time)
    
    # Get weather data
    weather_data = get_weather_data(LIVONIA_LAT, LIVONIA_LONG)

    # Display header
    st.title(f"Weather & UV Index for {LOCATION_NAME}")
    st.subheader(f"Last updated: {current_time.strftime('%B %d, %Y %I:%M %p')}")

    # Create columns for layout
    col1, col2 = st.columns(2)

    # Display UV Index in first column
    with col1:
        st.markdown("## UV Index")
        uv_color = get_uv_color(uv_index)
        uv_category = get_uv_category(uv_index)
        
        # Create a custom HTML widget for UV Index
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
            # Temperature
            st.markdown(f"### Temperature: {weather_data['temperature']}°F")
            
            # Weather condition
            st.markdown(f"### Conditions: {weather_data['description']}")
            
            # Additional data
            st.markdown(f"### Humidity: {weather_data['humidity']}%")
            st.markdown(f"### Wind: {weather_data['wind_speed']} mph")
        else:
            st.error("Unable to retrieve weather data. Please try again later.")

# Main app execution
if __name__ == "__main__":
    # Add auto-refresh using a placeholder and empty
    refresh_placeholder = st.empty()
    
    # Initial display
    update_and_display()
    
    # Auto-refresh info
    st.markdown("---")
    st.info(f"Data automatically refreshes every 15 minutes. You can also refresh manually by reloading the page.")
    
    # Set up auto-refresh functionality
    with st.sidebar:
        st.title("About")
        st.write("""
        This app displays the current UV index and weather conditions for Livonia, Michigan.
        
        The UV index is calculated using scientific formulas based on:
        - Solar position
        - Date and time
        - Location coordinates
        - Atmospheric conditions
        
        Weather data is provided by the National Weather Service (NWS).
        """)
        
        if st.button("Refresh Data Now"):
            st.rerun()
