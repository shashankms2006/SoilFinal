# 🌱 Smart AI Agriculture - Soil Health Analysis

An intelligent agricultural platform powered by AI that analyzes soil health, recommends optimal crops, and provides comprehensive farming guidance.

## Features

- **Soil Health Analysis**: Extract and analyze soil parameters from PDF reports
- **AI-Powered Crop Recommendations**: ML-based crop suggestions based on soil and weather
- **Smart Agriculture Insights**: AI-driven guidance on soil management, water, pests, and sustainability
- **Market Intelligence**: Real-time market data and selling strategies
- **Risk Assessment**: Profitability analysis and risk mitigation
- **Month-wise Planning**: Detailed crop-wise farming calendar

## Installation

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the root directory:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Running Locally

```bash
streamlit run "streamlit app.py"
```

## Deployment on Streamlit Cloud

1. Push code to GitHub repository
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Click "New app"
4. Select repository, branch, and main file: `streamlit app.py`
5. Add secrets in Streamlit Cloud dashboard:
   - `GEMINI_API_KEY`: Your Gemini API key

## Project Structure

```
SoilFinal/
├── streamlit app.py              # Main application
├── crop_optimization_model.py    # Gemini recommendations
├── smart_agriculture.py          # AI insights module
├── soil_classifier.py            # Soil classification
├── soil_extractor_multi.py       # PDF extraction
├── recommendation_training.py    # ML model
├── weather_data.py               # Weather API
├── market_data.py                # Market data
├── knapsack.py                   # Crop yields
├── smart_style.css               # UI theme
├── requirements.txt              # Dependencies
└── .streamlit/config.toml        # Streamlit config
```

## Technologies

- **Frontend**: Streamlit
- **AI/ML**: Google Gemini API, Scikit-learn
- **Data**: Pandas, NumPy
- **APIs**: Weather, Market data

## License

MIT
