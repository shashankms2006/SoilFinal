import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path

def get_past_weather(lat, lon):
    end = datetime.now().date()
    if end > datetime(2025, 11, 20).date():
        end = datetime(2025, 11, 20).date()
    start = end - timedelta(days=90)
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,soil_moisture_0_to_7cm_mean&timezone=auto"
    r = requests.get(url).json()
    if "error" in r:
        raise Exception(r.get("reason", "API Error"))
    df = pd.DataFrame({
        "date": r["daily"]["time"],
        "temp_max": r["daily"]["temperature_2m_max"],
        "temp_min": r["daily"]["temperature_2m_min"],
        "rain": r["daily"]["precipitation_sum"],
        "soil_moisture": r["daily"]["soil_moisture_0_to_7cm_mean"]
    })
    df["date"] = pd.to_datetime(df["date"])
    return df

def get_forecast_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&forecast_days=16&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,soil_moisture_0_to_7cm_mean&timezone=auto"
    r = requests.get(url).json()
    if "error" in r:
        raise Exception(r.get("reason", "API Error"))
    df = pd.DataFrame({
        "date": r["daily"]["time"],
        "temp_max": r["daily"]["temperature_2m_max"],
        "temp_min": r["daily"]["temperature_2m_min"],
        "rain": r["daily"]["precipitation_sum"],
        "soil_moisture": r["daily"]["soil_moisture_0_to_7cm_mean"]
    })
    df["date"] = pd.to_datetime(df["date"])
    return df

def get_weather_summary(df):
    return {
        "avg_max_temp": df["temp_max"].mean(),
        "avg_min_temp": df["temp_min"].mean(),
        "total_rainfall": df["rain"].sum(),
        "avg_soil_moisture": df["soil_moisture"].mean()
    }

def save_weather_data(lat, lon, location_name, df_past, df_forecast):
    data = {
        "location": {
            "name": location_name,
            "lat": lat,
            "lon": lon
        },
        "past_90_days": df_past.to_dict(orient="records"),
        "forecast_16_days": df_forecast.to_dict(orient="records"),
        "summary": get_weather_summary(df_past)
    }
    filepath = Path("weather_data.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
