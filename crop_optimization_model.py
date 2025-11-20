import google.generativeai as genai
import json
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_recommendations(soil_data: Dict, land_area: float, location: str, preferred_crops: List[str] = None, weather_data: Dict = None) -> tuple:
    """Get crop recommendations and detailed analysis from Gemini"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = f"""You are an agricultural expert.
I will give you soil test values, land area, and location.
Based on this, generate a structured "Crop Recommendation Table" with columns.
Follow EXACTLY the output format below.
Do NOT produce paragraphs outside the specified structure.

1. **CROP OPTION TABLE (COLUMN FORMAT)**
Create a table with these columns:

| Option | Crop Allocation (hectares) | Expected Yield per ha (kg) | Total Yield (kg) | Market Price (₹/kg) | Total Revenue (₹) | Revenue Split | Pros | Cons |

Generate **5 options**:
- Option A: Best single crop (soil + climate suitable)
- Option B: Second-best single crop
- Option C: Third-best single crop
- Option D: Best realistic 3-crop combination (crops must be compatible)
- Option E: Best realistic 2-crop combination

### RULES:
- Use REAL India-specific yields
- Use REAL mandi price ranges of India
- DO NOT create combinations that are unrealistic (e.g., potato + cardamom together).
- If soil pH is extremely low (like 3.0), clearly state that yield assumptions depend on lime correction.
- Calculate all totals correctly:
  Total Yield = Yield/ha × Area
  Total Revenue = Total Yield × Market Price

===========================
2. **REVENUE SUMMARY (below table)**
Write a clear revenue comparison explaining which option earns the highest and why,
based on realistic yield, price, soil suitability and crop requirements.

===========================
3. **MONTH-WISE TO-DO LIST (CROP-WISE, NOT OPTION-WISE)**

IMPORTANT:
- Timeline MUST start from the correct month for **soil preparation**, not always January.
- Months MUST be calendar months such as: January, February, March… NOT Month1/Month2.
- Create **separate month-wise tables for each crop** that appears in ANY option.
  Example: If grapes, turmeric, and cardamom appear in any option, then produce 3 separate tables:
  - "Month-wise Plan for Grapes"
  - "Month-wise Plan for Turmeric"
  - "Month-wise Plan for Cardamom"

Each crop table must include:
- Land preparation
- Soil correction (lime required if pH < 5.0)
- Sowing/planting
- Irrigation schedule
- Fertilizer schedule (NPK + micronutrients)
- Pruning (if grapes)
- Pest & disease management
- Harvesting
- Post-harvest & selling

Base the months on **real agricultural seasons in India** for each crop.

===========================
4. **OPTION-WISE TOTAL REVENUE + SELLING PLAN**

For each option A–E:
- Show final total revenue amount
- Give a realistic selling plan:
  *where to sell, required storage/processing, transporter availability, drying needs (if turmeric/cardamom)*

===========================
5. **FINAL EXPERT OPINION (5 lines only)**

Tell which option is best for the farmer considering:
- Soil pH and nutrient status
- Local climate
- Investment capacity
- Risk
- Time to first revenue
And give 3–5 lines of clear reasoning.

===========================
INPUT (USER WILL GIVE THESE)
===========================

- Land area (hectares)
- Soil test values (pH, EC, N, P, K, micronutrients)
- Location/state
- Weather data (temperature, rainfall)
- AI-recommended crops

===========================

LAND AREA: {land_area} hectares
SOIL DATA: pH {soil_data.get('pH', 'N/A')}, EC {soil_data.get('EC', 'N/A')}, OC {soil_data.get('OC', 'N/A')}%, N {soil_data.get('N', 'N/A')}, P {soil_data.get('P', 'N/A')}, K {soil_data.get('K', 'N/A')}, Zn {soil_data.get('Zn', 'N/A')}, B {soil_data.get('B', 'N/A')}, Fe {soil_data.get('Fe', 'N/A')}, Mn {soil_data.get('Mn', 'N/A')}
LOCATION: {location}
WEATHER DATA: Avg Max Temp {weather_data.get('avg_max_temp', 'N/A') if weather_data else 'N/A'}°C, Avg Min Temp {weather_data.get('avg_min_temp', 'N/A') if weather_data else 'N/A'}°C, Total Rainfall {weather_data.get('total_rainfall', 'N/A') if weather_data else 'N/A'} mm, Avg Soil Moisture {weather_data.get('avg_soil_moisture', 'N/A') if weather_data else 'N/A'} m³/m³
AI-RECOMMENDED CROPS: {', '.join(preferred_crops) if preferred_crops else 'None'}
"""
        
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.7))
        full_response = response.text
        
        crops_mentioned = extract_crops_from_response(full_response)
        
        return full_response, crops_mentioned
    except Exception as e:
        return f"Error generating recommendations: {e}", []


def extract_crops_from_response(response_text: str) -> List[str]:
    """Extract crop names mentioned in Gemini response"""
    common_crops = [
        'potato', 'garlic', 'sweetpotato', 'onion', 'tomato', 'chilli', 'capsicum',
        'carrot', 'beetroot', 'cabbage', 'cauliflower', 'brinjal', 'okra', 'spinach',
        'wheat', 'rice', 'maize', 'sugarcane', 'cotton', 'groundnut', 'soybean',
        'grapes', 'turmeric', 'cardamom', 'ginger', 'coriander', 'cumin', 'fenugreek',
        'mango', 'banana', 'coconut', 'arecanut', 'coffee', 'tea', 'spices'
    ]
    
    response_lower = response_text.lower()
    found_crops = []
    
    for crop in common_crops:
        if crop in response_lower and crop not in found_crops:
            found_crops.append(crop)
    
    return found_crops
