import streamlit as st
import requests
import os
import pandas as pd
import time

# ----------------------
# Configuration
# ----------------------
ACCUWEATHER_API_KEY = "YOUR_ACCUWEATHER_API_KEY"
BASE_URL = "http://dataservice.accuweather.com"


# ----------------------
# API Functions
# ----------------------
def get_location_key(city_name):
    """Search for a location and return its AccuWeather location key"""
    try:
        search_url = f"{BASE_URL}/locations/v1/search"
        params = {
            "apikey": ACCUWEATHER_API_KEY,
            "q": city_name,
            "country": "NG"  # Nigeria
        }
        response = requests.get(search_url, params=params, timeout=10)



        results = response.json()
        if not results:
            return None, "No matching city found"

        # Filter for Nigerian locations
        nigeria_results = [r for r in results if r.get("Country", {}).get("ID") == "NG"]
        if not nigeria_results:
            return None, "No Nigerian city found. Try a different name."

        location = nigeria_results[0]
        return location["Key"], None

    except Exception as e:
        return None, f"Search error: {str(e)}"


def get_current_weather(location_key):
    """Get current weather data for a location"""
    try:
        weather_url = f"{BASE_URL}/currentconditions/v1/{location_key}"
        params = {
            "apikey": ACCUWEATHER_API_KEY,
            "details": "true"
        }
        response = requests.get(weather_url, params=params, timeout=10)



        data = response.json()[0]  # First result
        return {
                   "temperature": data["Temperature"]["Metric"]["Value"],
                   "unit": data["Temperature"]["Metric"]["Unit"],
                   "condition": data["WeatherText"],
                   "humidity": data["RelativeHumidity"],
                   "wind_speed": data["Wind"]["Speed"]["Metric"]["Value"],
                   "uv_index": data["UVIndex"]
               }, None

    except Exception as e:
        return None, f"Weather fetch error: {str(e)}"


def get_air_quality(location_key):
    """Get air quality index for a location"""
    try:
        aqi_url = f"{BASE_URL}/indices/v1/currentconditions/aqi/{location_key}"
        params = {
            "apikey": ACCUWEATHER_API_KEY
        }
        response = requests.get(aqi_url, params=params, timeout=10)



        data = response.json()[0]  # First result
        return {
                   "aqi": data["aqi"],
                   "category": data["category"],
                   "description": data["description"]
               }, None

    except Exception as e:
        return None, f"Some slight Issues: {str(e)}"


# ----------------------
# Streamlit App
# ----------------------
st.set_page_config(page_title="Environmental Monitoring and Conservation", layout="centered")
st.title("🌤️ Environmental Monitoring")
st.markdown("Enter any **city name** to get current weather and air quality")

# Input field
city_input = st.text_input("🏙️ City Name", placeholder="e.g., Mubi, Maiduguri, Lagos")

# Fetch button
if st.button("🔍 Get Weather Data") and city_input:
    with st.spinner("Searching for location..."):
        time.sleep(1)

        # Step 1: Get location key
        location_key, error = get_location_key(city_input)
        if error:
            st.error(error)
            st.stop()

        st.success(f"Found location key: {location_key}")

    with st.spinner("Fetching weather data..."):
        # Step 2: Get weather data
        weather_data, error = get_current_weather(location_key)
        if error:
            st.error(error)
            st.stop()

    with st.spinner("Fetching air quality data..."):
        # Step 3: Get air quality data
        aqi_data, error = get_air_quality(location_key)
        if error:
            st.warning(error)  # Continue even if AQI fails

    # ----------------------
    # Display Results
    # ----------------------
    st.markdown("## 🌤️ Weather Conditions")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Temperature", f"{weather_data['temperature']}°{weather_data['unit']}")
        st.metric("Humidity", f"{weather_data['humidity']}%")
        st.metric("Wind Speed", f"{weather_data['wind_speed']} km/h")

    with col2:
        st.markdown("### Condition")
        st.info(weather_data["condition"])
        st.markdown("### UV Index")
        uv_index = weather_data["uv_index"]
        if uv_index < 3:
            st.success(f"Low ({uv_index})")
        elif uv_index < 6:
            st.warning(f"Moderate ({uv_index})")
        else:
            st.error(f"High ({uv_index})")

    st.markdown("## 🌫️ Air Quality")
    if aqi_data:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("AQI", aqi_data["aqi"])
        with col2:
            st.markdown("### Category")
            category = aqi_data["category"]
            if category == "Good":
                st.success(category)
            elif category in ["Moderate", "Unhealthy for sensitive groups"]:
                st.warning(category)
            else:
                st.error(category)

        st.markdown(f"**Description:** {aqi_data['description']}")
    else:
        st.info("Air quality data not available for this location")

# Footer
st.markdown("---")
st.markdown(
    "⚠️ BE CAUTIONED, RESULT MIGHT SLIGHTLY VARY")