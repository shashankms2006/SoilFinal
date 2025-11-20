import pandas as pd
from knapsack import YIELD_PER_HA_KG

def generate_verification_report(soil_params, weather_data, market_prices, recommendations, land_area):
    """
    Generate a verification report showing how recommendations depend on all inputs.
    """
    report = {
        "soil_analysis": {
            "pH": soil_params.get("pH", "NA"),
            "Nitrogen (kg/ha)": soil_params.get("Nitrogen", "NA"),
            "Phosphorus (kg/ha)": soil_params.get("Phosphorus", "NA"),
            "Potassium (kg/ha)": soil_params.get("Potassium", "NA"),
        },
        "weather_analysis": {
            "Avg Max Temp (°C)": f"{weather_data.get('avg_max_temp', 0):.1f}",
            "Avg Min Temp (°C)": f"{weather_data.get('avg_min_temp', 0):.1f}",
            "Total Rainfall (mm)": f"{weather_data.get('total_rainfall', 0):.1f}",
            "Avg Soil Moisture (m³/m³)": f"{weather_data.get('avg_soil_moisture', 0):.3f}",
        },
        "market_analysis": {},
        "recommendation_details": []
    }
    
    for rec in recommendations:
        crop = rec["crop"]
        market_price = market_prices.get(crop, "NA")
        yield_per_ha = YIELD_PER_HA_KG.get(crop.lower(), 0)
        
        report["market_analysis"][crop] = f"₹{market_price}/quintal" if isinstance(market_price, (int, float)) else market_price
        
        if isinstance(market_price, (int, float)) and market_price > 0:
            total_yield = yield_per_ha * land_area
            total_revenue = total_yield * (market_price / 100)
            
            report["recommendation_details"].append({
                "crop": crop,
                "suitability_score": rec["score"],
                "score_reasons": rec["reasons"],
                "yield_per_hectare": yield_per_ha,
                "total_yield_kg": f"{total_yield:.0f}",
                "market_price_per_quintal": f"₹{market_price}",
                "total_revenue": f"₹{total_revenue:,.0f}",
                "land_area_hectares": land_area
            })
    
    return report

def format_verification_report(report):
    """Format verification report for display"""
    output = "📋 VERIFICATION REPORT\n"
    output += "=" * 60 + "\n\n"
    
    output += "🌱 SOIL ANALYSIS\n"
    output += "-" * 60 + "\n"
    for key, value in report["soil_analysis"].items():
        output += f"  {key}: {value}\n"
    
    output += "\n🌤️ WEATHER ANALYSIS\n"
    output += "-" * 60 + "\n"
    for key, value in report["weather_analysis"].items():
        output += f"  {key}: {value}\n"
    
    output += "\n🏪 MARKET ANALYSIS\n"
    output += "-" * 60 + "\n"
    for crop, price in report["market_analysis"].items():
        output += f"  {crop}: {price}\n"
    
    output += "\n🎯 RECOMMENDATION DETAILS\n"
    output += "-" * 60 + "\n"
    for detail in report["recommendation_details"]:
        output += f"\n  Crop: {detail['crop']}\n"
        output += f"    Suitability Score: {detail['suitability_score']}/100\n"
        output += f"    Reasons: {', '.join(detail['score_reasons'])}\n"
        output += f"    Yield/ha: {detail['yield_per_hectare']} kg\n"
        output += f"    Total Yield: {detail['total_yield_kg']} kg\n"
        output += f"    Market Price: {detail['market_price_per_quintal']}\n"
        output += f"    Total Revenue: {detail['total_revenue']}\n"
    
    return output
