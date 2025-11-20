"""
Gemini-powered crop recommendation helper.

Pipeline:
1. Build a context JSON from soil / weather / location / predicted crops.
2. Fetch recent market prices from Agmarknet (data.gov.in).
3. Compute knapsack-style allocation options using yield-per-hectare data.
4. Ask Gemini to synthesize fertilizer + farming guidance for each option.
"""

from __future__ import annotations

import itertools
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None  # type: ignore


BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
AGMARKNET_API_KEY = os.getenv("AGMARKNET_API_KEY", "579b464db66ec23bdd0000017977df66bcc0429362f8ac2c4d51a29d")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

YIELD_PER_HA_KG: Dict[str, int] = {
    "banana": 33500,
    "barley": 3200,
    "bittergourd": 15000,
    "blackgram": 600,
    "blackpepper": 1500,
    "bottlegourd": 12000,
    "brinjal": 17500,
    "cardamom": 400,
    "coriander": 600,
    "cotton": 550,
    "cowpea": 900,
    "cucumber": 20000,
    "chilli": 7000,
    "garlic": 8000,
    "grapes": 10000,
    "horsegram": 700,
    "jackfruit": 20000,
    "jowar": 900,
    "jute": 2540,
    "ladyfinger": 9000,
    "litchi": 8000,
    "maize": 2700,
    "mango": 8000,
    "moong": 650,
    "onion": 29000,
    "orange": 9000,
    "papaya": 40000,
    "pineapple": 40000,
    "potato": 22000,
    "pumpkin": 10000,
    "radish": 15000,
    "ragi": 1200,
    "rapeseed_mustard": 1387,
    "rice": 2859,
    "soyabean": 1084,
    "sunflower": 781,
    "sweetpotato": 12000,
    "tomato": 22000,
    "turmeric": 4000,
    "wheat": 3521,
}


@dataclass
class LocationInfo:
    state: Optional[str] = None
    district: Optional[str] = None
    market: Optional[str] = None
    pincode: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


def build_context_json(
    soil_values: Dict[str, float],
    soil_type: str,
    location: LocationInfo,
    weather_data: Dict[str, float],
    predicted_crops: List[str],
) -> Dict:
    """Create a single payload that Gemini can reason over."""
    return {
        "soil": {
            "type": soil_type,
            "parameters": soil_values,
        },
        "location": {
            "state": location.state,
            "district": location.district,
            "market": location.market,
            "pincode": location.pincode,
            "lat": location.lat,
            "lon": location.lon,
        },
        "weather": weather_data,
        "predicted_crops": predicted_crops,
    }


def _normalize_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def fetch_market_prices(
    crop_names: List[str],
    location: LocationInfo,
    api_key: Optional[str] = None,
    limit: int = 200,
) -> Dict[str, float]:
    """Fetch modal prices (INR per quintal) for given crops from Agmarknet."""
    api_key = api_key or AGMARKNET_API_KEY
    params = {
        "api-key": api_key,
        "format": "json",
        "offset": 0,
        "limit": limit,
    }

    filters: Dict[str, str] = {}
    if location.state:
        filters["state"] = location.state
    if location.district:
        filters["district"] = location.district
    if location.market:
        filters["market"] = location.market

    for key, value in filters.items():
        params[f"filters[{key}]"] = value

    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    records = data.get("records", [])

    price_map: Dict[str, float] = {}
    crop_lookup = {_normalize_name(c): c for c in crop_names}

    for row in records:
        commodity = row.get("commodity") or row.get("Commodity")
        if not commodity:
            continue
        norm = _normalize_name(commodity)
        if norm not in crop_lookup:
            continue
        price = row.get("modal_price") or row.get("Modal_Price") or row.get("Modal_x0020_Price")
        try:
            price_val = float(price)
        except (TypeError, ValueError):
            continue
        price_map[crop_lookup[norm]] = price_val

    return price_map


def compute_knapsack_options(
    crops_with_price: Dict[str, float],
    land_area: float,
    max_options: int = 5,
) -> List[Dict]:
    """Generate single and multi-crop allocations ordered by revenue."""
    options: List[Dict] = []
    valid_crops = [
        crop
        for crop, price in crops_with_price.items()
        if price and price > 0 and _normalize_name(crop) in YIELD_PER_HA_KG
    ]

    if not valid_crops:
        return []

    def add_option(allocations: List[Tuple[str, float, float, float]]) -> None:
        total_revenue = sum(yield_kg * (price / 100) for _, _, yield_kg, price in allocations)
        options.append(
            {
                "option": len(options) + 1,
                "allocations": allocations,
                "total_revenue": total_revenue,
            }
        )

    # Single crop allocations
    for crop in valid_crops:
        price = crops_with_price[crop]
        yield_per_ha = YIELD_PER_HA_KG[_normalize_name(crop)]
        yield_kg = yield_per_ha * land_area
        add_option([(crop, land_area, yield_kg, price)])

    # Multi-crop allocations (up to 3 crops for readability)
    for r in range(2, min(len(valid_crops), 3) + 1):
        for combo in itertools.combinations(valid_crops, r):
            area_per_crop = land_area / len(combo)
            allocations = []
            for crop in combo:
                price = crops_with_price[crop]
                yield_per_ha = YIELD_PER_HA_KG[_normalize_name(crop)]
                yield_kg = yield_per_ha * area_per_crop
                allocations.append((crop, area_per_crop, yield_kg, price))
            add_option(allocations)

    options.sort(key=lambda opt: opt["total_revenue"], reverse=True)
    return options[:max_options]


def call_gemini(
    prompt: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-pro",
) -> str:
    """Call Gemini with the assembled prompt."""
    api_key = api_key or GEMINI_API_KEY
    if not api_key:
        raise RuntimeError("Gemini API key not configured. Set GEMINI_API_KEY env var.")

    if genai is None:
        raise ImportError("google-generativeai package not installed. Run `pip install google-generativeai`.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text.strip()


def generate_recommendation_report(
    soil_values: Dict[str, float],
    soil_type: str,
    location: LocationInfo,
    weather_data: Dict[str, float],
    predicted_crops: List[str],
    land_area: float,
    max_options: int = 5,
    gemini_api_key: Optional[str] = None,
    agmark_api_key: Optional[str] = None,
) -> Dict:
    """
    Full pipeline returning JSON with:
        - context payload
        - market prices
        - knapsack options
        - Gemini guidance text
    """
    context_payload = build_context_json(soil_values, soil_type, location, weather_data, predicted_crops)

    crops_for_market = predicted_crops or list(YIELD_PER_HA_KG.keys())
    prices = fetch_market_prices(crops_for_market, location, api_key=agmark_api_key)

    knapsack_options = compute_knapsack_options(prices, land_area, max_options=max_options)

    prompt = f"""
You are an agronomy assistant. Given the following context and candidate crop allocations,
recommend the best options, list natural/organic fertilizers, and provide step-by-step farming
instructions from land preparation to selling.

Context JSON:
{json.dumps(context_payload, indent=2)}

Market Prices (₹ per quintal):
{json.dumps(prices, indent=2)}

Land area: {land_area} hectares

Allocation options (area in ha, yield in kg):
{json.dumps(knapsack_options, indent=2)}

Return a concise but informative plan covering:
1. Recommended crop option(s) with revenue reasoning.
2. Natural/organic fertilizer suggestions and quantities.
3. Key agronomic steps (preparation, sowing, crop care, harvesting, selling tips).
"""

    guidance = call_gemini(prompt, api_key=gemini_api_key)

    return {
        "context": context_payload,
        "market_prices": prices,
        "knapsack_options": knapsack_options,
        "guidance": guidance,
    }
