import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import tempfile
import base64
import requests
from soil_extractor_multi import MultiEngineExtractor as SoilExtractor
from soil_classifier import SoilClassifier
from location_utils import LocationResolver
from weather_data import get_past_weather, get_forecast_weather, get_weather_summary, save_weather_data
from market_data import get_ranked_crops_for_location
from recommendation_training import recommend_crops_ml
from crop_optimization_model import get_gemini_recommendations, extract_crops_from_response

st.set_page_config(page_title="Soil Health Analysis", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    button[kind="primary"] { background-color: #28a745 !important; }
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "input"
if "uploaded_pdf" not in st.session_state:
    st.session_state.uploaded_pdf = None
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "location_input" not in st.session_state:
    st.session_state.location_input = ""
if "land_area" not in st.session_state:
    st.session_state.land_area = 0.0
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = {}
if "soil_type" not in st.session_state:
    st.session_state.soil_type = ""
if "location_name" not in st.session_state:
    st.session_state.location_name = ""
if "lat" not in st.session_state:
    st.session_state.lat = None
if "lon" not in st.session_state:
    st.session_state.lon = None
if "ai_recommendations" not in st.session_state:
    st.session_state.ai_recommendations = []
if "weather_summary" not in st.session_state:
    st.session_state.weather_summary = {}
if "gemini_recommendations" not in st.session_state:
    st.session_state.gemini_recommendations = ""
if "gemini_crops" not in st.session_state:
    st.session_state.gemini_crops = []

PARAMETER_UNITS = {
    "pH": "pH", "Nitrogen": "kg/ha", "Phosphorus": "kg/ha", "Potassium": "kg/ha",
    "Organic Carbon": "%", "Organic Matter": "%", "Calcium": "mg/kg", "Magnesium": "mg/kg",
    "Sulfur": "mg/kg", "Sulphur": "mg/kg", "Zinc": "mg/kg", "Iron": "mg/kg",
    "Copper": "mg/kg", "Manganese": "mg/kg", "Boron": "mg/kg", "EC": "dS/m", "Moisture": "%"
}

def display_pdf_viewer(pdf_file, zoom=100):
    pdf_file.seek(0)
    pdf_bytes = pdf_file.read()
    pdf_b64 = base64.b64encode(pdf_bytes).decode()
    html = f'<iframe src="data:application/pdf;base64,{pdf_b64}" width="100%" height="600px" style="transform: scale({zoom/100}); transform-origin: top left; border: 1px solid #ddd; border-radius: 8px;"></iframe>'
    st.markdown(html, unsafe_allow_html=True)

@st.cache_resource
def get_extractor():
    extractor = SoilExtractor()
    extractor.load_engines()
    return extractor

@st.cache_resource
def get_classifier():
    return SoilClassifier()

@st.cache_resource
def get_location_resolver():
    return LocationResolver()

def extract_pdf_values(pdf_file):
    try:
        extractor = get_extractor()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name
        results = extractor.process_file(tmp_path)
        extracted = {param: data['value'] for param, data in results.items()}
        return extracted
    except Exception as e:
        st.error(f"PDF extraction failed: {e}")
        return {}

def classify_soil_type(image_file):
    try:
        classifier = get_classifier()
        soil_type, confidence = classifier.classify_image(image_file)
        return soil_type, confidence
    except Exception as e:
        st.warning(f"Soil classification failed: {e}")
        return "Unknown", 0.0

def get_location_from_pincode(query: str):
    try:
        resolver = get_location_resolver()
        location_name, lat, lon = resolver.resolve_location(query)
        return location_name, lat, lon
    except Exception as e:
        st.warning(f"Could not fetch location: {e}")
        return None, None, None

def clear_chat_history():
    for key in list(st.session_state.keys()):
        if key not in ["page"]:
            del st.session_state[key]
    st.session_state.page = "input"

def input_page():
    st.title("🌱 Soil Health Analysis ")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Soil Health Card (PDF)")
        pdf_file = st.file_uploader("Upload Soil Health Card PDF", type=["pdf"], key="pdf_upload")
        if pdf_file:
            st.session_state.uploaded_pdf = pdf_file
            st.success("✅ PDF uploaded")
    
    with col2:
        st.subheader("🖼️ Soil Image (Optional)")
        image_file = st.file_uploader("Upload Soil Image for Classification", type=["jpg", "jpeg", "png"], key="img_upload")
        if image_file:
            st.session_state.uploaded_image = image_file
            st.image(image_file, width=200, caption="Uploaded Image")
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📍 Location / Pincode")
        location_input = st.text_input(
            "Enter Location Name or Pincode",
            value=st.session_state.location_input,
            placeholder="e.g., 560001 or Bangalore"
        )
        st.session_state.location_input = location_input
    
    with col4:
        st.subheader("🌾 Land Area")
        land_area = st.number_input(
            "Enter Land Area (in hectares)",
            min_value=0.0,
            value=st.session_state.land_area,
            step=0.1
        )
        st.session_state.land_area = land_area
    
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns([1, 1])
    
    with col_btn1:
        if st.button("✅ Proceed to Confirmation", use_container_width=True, type="primary"):
            errors = []
            if not st.session_state.uploaded_pdf:
                errors.append("❌ Soil Health Card PDF is required")
            if not st.session_state.location_input:
                errors.append("❌ Location/Pincode is required")
            if st.session_state.land_area <= 0:
                errors.append("❌ Land Area must be greater than 0")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                with st.spinner("🔄 Extracting data from PDF..."):
                    extracted = extract_pdf_values(st.session_state.uploaded_pdf)
                    st.session_state.extracted_data = extracted
                
                if st.session_state.uploaded_image:
                    with st.spinner("🔄 Classifying soil type..."):
                        soil_type, confidence = classify_soil_type(st.session_state.uploaded_image)
                        st.session_state.soil_type = soil_type
                
                with st.spinner("🔄 Fetching location details..."):
                    location_name, lat, lon = get_location_from_pincode(st.session_state.location_input)
                    st.session_state.location_name = location_name or st.session_state.location_input
                    st.session_state.lat = lat
                    st.session_state.lon = lon
                
                st.session_state.page = "confirmation"
                st.rerun()

def confirmation_page():
    st.title("✅ Confirmation - Review Details")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Location Details")
        st.write(f"**Input:** {st.session_state.location_input}")
        st.write(f"**Recognized Location:** {st.session_state.location_name}")
    
    with col2:
        st.subheader("🌾 Land Area")
        st.write(f"**Area:** {st.session_state.land_area} hectares")
    
    st.markdown("---")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        st.subheader("📄 Soil Health Card PDF")
        if st.session_state.uploaded_pdf:
            display_pdf_viewer(st.session_state.uploaded_pdf, 100)
    
    with col4:
        st.subheader("📊 Extracted Soil Parameters")
        if st.session_state.extracted_data:
            for param, value in st.session_state.extracted_data.items():
                unit = PARAMETER_UNITS.get(param, "")
                col_label, col_input, col_unit = st.columns([2, 1.5, 1])
                with col_label:
                    st.write(f"**{param}**")
                with col_input:
                    st.session_state.extracted_data[param] = st.number_input(
                        f"{param}_input",
                        value=value,
                        format="%.2f",
                        label_visibility="collapsed",
                        key=f"param_{param}"
                    )
                with col_unit:
                    st.write(unit)
        else:
            st.warning("⚠️ No parameters extracted from PDF.")
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("🖼️ Soil Image")
        if st.session_state.uploaded_image:
            st.image(st.session_state.uploaded_image, use_container_width=True)
        else:
            st.info("No soil image uploaded")
    
    with col6:
        st.subheader("🧪 Soil Type Classification")
        if st.session_state.soil_type:
            st.success(f"**Detected:** {st.session_state.soil_type}")
        else:
            st.info("No soil type detected")
    
    st.markdown("---")
    
    col_action1, col_action2 = st.columns([1, 1])
    
    with col_action1:
        if st.button("🔙 Back", use_container_width=True):
            st.session_state.page = "input"
            st.rerun()
    
    with col_action2:
        if st.button("✅ Confirm & Proceed", use_container_width=True, type="primary"):
            st.session_state.page = "recommendation"
            st.rerun()

def recommendation_page():
    st.title("🌾 Crop Recommendation")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🌤️ Weather Snapshot (Past 90 Days)")
        if st.session_state.lat and st.session_state.lon:
            try:
                df_past = get_past_weather(st.session_state.lat, st.session_state.lon)
                df_forecast = get_forecast_weather(st.session_state.lat, st.session_state.lon)
                if df_past.empty:
                    st.warning("No weather data available for this location.")
                else:
                    save_weather_data(
                        st.session_state.lat,
                        st.session_state.lon,
                        st.session_state.location_name or st.session_state.location_input,
                        df_past,
                        df_forecast,
                    )
                    st.session_state.weather_summary = get_weather_summary(df_past)
                    st.metric("Avg Max Temp", f"{st.session_state.weather_summary['avg_max_temp']:.1f}°C")
                    st.metric("Avg Min Temp", f"{st.session_state.weather_summary['avg_min_temp']:.1f}°C")
                    st.metric("Total Rainfall", f"{st.session_state.weather_summary['total_rainfall']:.1f} mm")
                    st.metric("Avg Soil Moisture", f"{st.session_state.weather_summary['avg_soil_moisture']:.3f} m³/m³")
            except Exception as exc:
                st.error(f"Weather fetch failed: {exc}")
        else:
            st.warning("Location coordinates not available. Please provide a valid location/pincode.")

    with col2:
        st.subheader("🏪 Nearby Markets")
        try:
            market_df = get_ranked_crops_for_location(st.session_state.location_input, days_window=3)
            if not market_df.empty:
                unique_locations = []
                seen = set()
                for _, row in market_df.iterrows():
                    state = row.get("state") or row.get("State")
                    district = row.get("district") or row.get("District")
                    market_name = row.get("market") or row.get("Market")
                    key = (state, district, market_name)
                    if key in seen:
                        continue
                    seen.add(key)
                    unique_locations.append(key)
                if unique_locations:
                    for state, district, market_name in unique_locations[:10]:
                        parts = [part for part in [market_name, district, state] if part]
                        st.write(" • " + ", ".join(parts))
                else:
                    st.info("Market locations not available in the current dataset.")
            else:
                st.info("No market data available for the provided location.")
        except Exception as exc:
            st.warning(f"Market data unavailable: {exc}")

    st.markdown("---")

    st.subheader("🤖 AI Recommendations")
    if not st.session_state.extracted_data:
        st.info("Upload and confirm soil data to unlock model-based recommendations.")
    else:
        rainfall_input = st.session_state.weather_summary.get("total_rainfall", 500) if st.session_state.weather_summary else 500
        temp_input = st.session_state.weather_summary.get("avg_max_temp", 25) if st.session_state.weather_summary else 25
        try:
            ml_recs = recommend_crops_ml(
                st.session_state.extracted_data.get("Nitrogen", 0),
                st.session_state.extracted_data.get("Phosphorus", 0),
                st.session_state.extracted_data.get("Potassium", 0),
                st.session_state.extracted_data.get("pH", 7),
                rainfall_input,
                temp_input,
                top_k=5,
            )
            st.session_state.ai_recommendations = [rec["crop"] for rec in ml_recs]
            if ml_recs:
                for idx, rec in enumerate(ml_recs, 1):
                    st.markdown(f"<p style='font-size:1.2rem'><strong>{idx}. {rec['crop'].upper()}</strong></p>", unsafe_allow_html=True)
            else:
                st.info("No crops met the 10% confidence threshold.")
        except FileNotFoundError:
            st.warning("Model artifacts not found. Please run `recommendation_training.py` first.")
        except Exception as exc:
            st.error(f"Unable to generate recommendations: {exc}")

    st.markdown("---")
    st.subheader("📋 Comprehensive Crop Analysis")
    
    if st.button("Generate Crop Recommendations & Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing soil and generating recommendations..."):
            recommendations, crops = get_gemini_recommendations(
                st.session_state.extracted_data,
                st.session_state.land_area,
                st.session_state.location_name or st.session_state.location_input,
                st.session_state.ai_recommendations,
                st.session_state.weather_summary
            )
            st.session_state.gemini_recommendations = recommendations
            st.session_state.gemini_crops = crops
    
    if st.session_state.gemini_recommendations:
        st.markdown(st.session_state.gemini_recommendations)
    
    st.markdown("---")
    col_back, col_clear = st.columns([1, 0.5])
    with col_back:
        if st.button("🔙 Back", use_container_width=True):
            st.session_state.page = "confirmation"
            st.rerun()
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            clear_chat_history()
            st.rerun()

def main():
    if st.session_state.page == "input":
        input_page()
    elif st.session_state.page == "confirmation":
        confirmation_page()
    elif st.session_state.page == "recommendation":
        recommendation_page()

if __name__ == "__main__":
    main()
